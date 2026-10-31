"""Generic restartable byte transducers with opaque storage and integer registers.

There is no source token table or transformation here. A pinned BF kernel chooses
every emitted byte, stack operation, integer operation and acceptance decision.
One bounded native invocation processes one fixed physical event record.
"""
import hashlib
import os
import time
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_json, canonical, digest, load, no_links
from .worker import seal, unseal


def _request(event, byte, spec, state):
    integers = state["integers"]
    stack = state["stacks"][0]
    current = int(integers[0])
    limit = spec["integer_limit"]
    require(limit is None or (type(limit) is int and limit >= 0),
            "BUDGET", "Integer ceiling must be an explicit nonnegative budget or null")
    # Generic arithmetic facts, with meanings assigned solely by the byte kernel.
    facts = [int(current == 0), int(current < 0),
             int(bool(stack) and current == int(stack[-1])), int(not stack),
             int(limit is not None and current >= limit)]
    opaque = bytes.fromhex(state["opaque"])
    require(len(opaque) == 16, "STATE", "Machine requires sixteen opaque state bytes")
    return bytes([177, event, byte, spec["profile"], spec["selector"], *facts]) + opaque


def _effects(actions, state, output, spec):
    position = 0
    handoff = None
    def take(count):
        nonlocal position
        require(position + count <= len(actions), "MACHINE_RESPONSE", "Truncated effect instruction")
        value = actions[position:position + count]
        position += count
        return value
    def slot(value, collection):
        require(value < len(collection), "MACHINE_SLOT", "Invalid opaque storage slot")
        return value
    while position < len(actions):
        opcode = take(1)[0]
        if opcode == 1:
            output.write(take(1))
        elif opcode == 2:
            index, byte = take(2)
            index = slot(index, state["buffers"])
            state["buffers"][index] += bytes([byte]).hex()
        elif opcode == 3:
            index = slot(take(1)[0], state["buffers"])
            output.write(bytes.fromhex(state["buffers"][index]))
        elif opcode == 4:
            state["buffers"][slot(take(1)[0], state["buffers"])] = ""
        elif opcode == 5:
            stack, register = take(2)
            state["stacks"][slot(stack, state["stacks"])].append(state["integers"][slot(register, state["integers"])])
        elif opcode == 6:
            stack = state["stacks"][slot(take(1)[0], state["stacks"])]
            require(stack, "MACHINE_STACK", "Opaque stack underflow")
            stack.pop()
        elif opcode == 7:
            register, delta = take(2)
            register = slot(register, state["integers"])
            state["integers"][register] = str(int(state["integers"][register]) + (delta if delta < 128 else delta - 256))
        elif opcode == 8:
            register, value = take(2)
            state["integers"][slot(register, state["integers"])] = str(value)
        elif opcode == 9:
            source, destination = take(2)
            state["integers"][slot(destination, state["integers"])] = state["integers"][slot(source, state["integers"])]
        elif opcode == 10:
            stack, value = take(2)
            state["stacks"][slot(stack, state["stacks"])].append(str(value))
        elif opcode == 11:
            require(handoff is None, "MACHINE_HANDOFF", "Multiple kernel handoffs in one response")
            handoff = take(1)[0]
        else:
            require(False, "MACHINE_OPCODE", "Unknown byte-machine effect", opcode=opcode)
        require(output.tell() <= spec["max_output_bytes"], "OUTPUT_BUDGET", "Machine output budget exceeded")
        storage_bytes = sum(len(value) // 2 for value in state["buffers"])
        require(storage_bytes <= spec["max_storage_bytes"] and
                sum(len(value) for value in state["stacks"]) <= spec["max_stack_entries"],
                "RESOURCE_BUDGET", "Opaque storage exceeds explicit job budget")
    return handoff


def transduce(spec):
    started = time.perf_counter()
    deadline = started + spec["max_operation_seconds"]
    def remaining_seconds():
        remaining = deadline - time.perf_counter()
        require(remaining > 0, "RESOURCE_BUDGET", "Machine operation exceeded explicit time budget")
        return remaining
    native_wall_seconds = 0.0
    native_cpu_seconds = 0.0
    native_peak_bytes = 0
    counter_complete = True
    source, destination = Path(spec["source"]).absolute(), Path(spec["destination"]).absolute()
    no_links(source)
    no_links(destination.parent)
    require(source != destination and not destination.exists(), "DESTINATION", "Transduction requires a new destination")
    executable = pinned_executable(spec["worker"])
    argv = [executable]
    if spec.get("launcher"):
        argv.insert(0, pinned_executable(spec["launcher"]))
    key = Path(spec["state_key"]).read_bytes()
    require(len(key) >= 32, "STATE_KEY", "At least 256-bit checkpoint key required")
    identity = {"format": "OPAQUE-BYTE-MACHINE-HMAC", "input_sha256": digest(source),
                "binding_sha256": hashlib.sha256(canonical(spec)).hexdigest(),
                "worker_sha256": spec["worker"]["sha256"]}
    journal = Path(spec["journal"])
    pending = destination.with_name(destination.name + ".partial")
    state = dict(identity, opaque="00" * 16, integers=["0"] * 4,
                 buffers=[""] * 8, stacks=[[] for _ in range(4)],
                 input_offset="0", output_offset="0", event="0", sequence="0",
                 output_sha256=hashlib.sha256(b"").hexdigest(), complete=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if journal.exists():
        state = unseal(load(journal), key)
        require(all(state.get(k) == v for k, v in identity.items()), "STATE_BINDING", "Machine checkpoint belongs to different inputs")
        require(not state["complete"], "REPLAY", "Completed machine checkpoint")
        require(pending.exists(), "STATE_OUTPUT", "Missing pending machine output")
        with pending.open("r+b") as output:
            require(output.seek(0, 2) >= int(state["output_offset"]), "STATE_OUTPUT", "Truncated pending output")
            output.truncate(int(state["output_offset"]))
        require(digest(pending) == state["output_sha256"], "STATE_OUTPUT", "Committed machine output changed")
    else:
        require(not pending.exists(), "ORPHAN", "Pending output without authenticated state")
        pending.touch(exist_ok=False)
        atomic_json(journal, seal(state, key))
    hasher = hashlib.sha256()
    with pending.open("rb") as prior:
        for block in iter(lambda: prior.read(1024 * 1024), b""):
            hasher.update(block)
    with source.open("rb") as input_file, pending.open("r+b") as output:
        input_file.seek(int(state["input_offset"]))
        output.seek(int(state["output_offset"]))
        while int(state["event"]) != 3:
            remaining_seconds()
            event = int(state["event"])
            data = b"" if event == 0 else input_file.read(1)
            if event != 0:
                event = 1 if data else 2
            before = output.tell()
            active_argv = argv
            handoffs = 0
            while True:
                request = _request(event, data[0] if data else 0, spec, state)
                result = checked(active_argv, stdin=request,
                                 timeout=min(spec["timeout_seconds"], remaining_seconds()),
                                 max_output=spec["max_response_bytes"])
                remaining_seconds()
                native_wall_seconds += result["wall_seconds"]
                counters = result["resources"]
                if counters["status"] == "PASS":
                    native_cpu_seconds += counters["kernel_cpu_seconds"] + counters["user_cpu_seconds"]
                    native_peak_bytes = max(native_peak_bytes, counters["peak_working_set_bytes"])
                else:
                    counter_complete = False
                response = result["stdout"]
                require(len(response) >= 18 and response[0] == 178,
                        "MACHINE_RESPONSE", "Missing machine response format/state")
                require(response[-1] == 0, "WORKER_REJECT", "BF machine refused event", worker_status=response[-1], offset=str(input_file.tell()))
                state["opaque"] = response[-17:-1].hex()
                handoff = _effects(response[1:-17], state, output, spec)
                if handoff is None:
                    break
                handoffs += 1
                require(handoffs <= spec["max_handoffs_per_event"], "RESOURCE_BUDGET", "Kernel handoff budget exceeded")
                require(str(handoff) in spec["kernels"], "MACHINE_HANDOFF", "Missing pinned kernel")
                active_argv = [pinned_executable(spec["kernels"][str(handoff)])]
                if spec.get("launcher"):
                    active_argv.insert(0, pinned_executable(spec["launcher"]))
            output.flush()
            after = output.tell()
            output.seek(before)
            hasher.update(output.read(after - before))
            output.seek(after)
            state.update(input_offset=str(input_file.tell()), output_offset=str(after),
                         sequence=str(int(state["sequence"]) + 1), event="3" if event == 2 else "1",
                         output_sha256=hasher.hexdigest())
            interval = spec["checkpoint_events"]
            require(interval > 0, "BUDGET", "Positive checkpoint interval required")
            if int(state["sequence"]) % interval == 0 or event == 2:
                os.fsync(output.fileno())
                atomic_json(journal, seal(state, key), replace=True)
    require(digest(source) == identity["input_sha256"], "CHANGED", "Machine input changed")
    remaining_seconds()
    os.link(pending, destination)
    pending.unlink()
    state["complete"] = True
    atomic_json(journal, seal(state, key), replace=True)
    return {"input_bytes": int(state["input_offset"]), "output_bytes": int(state["output_offset"]),
            "events": int(state["sequence"]), "output_sha256": state["output_sha256"],
            "wall_seconds": time.perf_counter() - started, "native_process_wall_seconds": native_wall_seconds,
            "native_cpu_seconds": native_cpu_seconds if counter_complete else None,
            "native_peak_working_set_bytes": native_peak_bytes if counter_complete else None,
            "counter_status": "PASS" if counter_complete else "BLOCKED",
            "measurement_scope": "this invocation; native process counters exclude host and previous resume attempts"}
