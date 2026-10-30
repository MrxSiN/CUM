"""Opaque resumable byte mapping; no language recognition or rewrite logic."""
import hashlib
import hmac
import json
import os
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_json, canonical, digest, load, no_links
from .transport import worker_input, worker_output


def seal(value, key):
    body = canonical(value)
    return {"body": value, "hmac_sha256": hmac.new(key, body, hashlib.sha256).hexdigest()}


def unseal(value, key):
    expected = hmac.new(key, canonical(value["body"]), hashlib.sha256).hexdigest()
    require(hmac.compare_digest(value["hmac_sha256"], expected), "STATE_AUTH", "Continuation authentication failed")
    return value["body"]


def exchange(spec, payload, state):
    executable = pinned_executable(spec["worker"])
    data = worker_input(state, payload)
    require(len(data) <= spec["input_capacity_bytes"], "INPUT_CAPACITY", "Encoded record exceeds selected worker capability")
    argv = [executable]
    if spec.get("launcher"):
        argv.insert(0, pinned_executable(spec["launcher"]))
    result = checked(argv, stdin=data, timeout=spec["timeout_seconds"],
                     max_output=spec["output_capacity_bytes"])
    output, new_state = worker_output(result["stdout"])
    return output, new_state, result["wall_seconds"]


def map_file(spec):
    source, destination = Path(spec["source"]).absolute(), Path(spec["destination"]).absolute()
    no_links(source)
    no_links(destination.parent)
    require(source != destination and not destination.exists(), "DESTINATION", "Mapping requires a new destination")
    chunk = spec["record_payload_bytes"]
    require(chunk > 0 and 2 * chunk + 3 <= spec["input_capacity_bytes"],
            "INPUT_CAPACITY", "Record budget does not fit worker input")
    key = Path(spec["state_key"]).read_bytes()
    require(len(key) >= 32, "STATE_KEY", "Continuation key needs at least 256 random bits")
    journal = Path(spec["journal"]).absolute()
    temporary = destination.with_name(destination.name + ".partial")
    destination.parent.mkdir(parents=True, exist_ok=True)
    identity = {"format": "BYTE-MAP-STATE-HMAC-SHA256", "source_sha256": digest(source),
                "worker_sha256": spec["worker"]["sha256"],
                "config_sha256": hashlib.sha256(canonical(spec)).hexdigest()}
    header = bytes.fromhex(spec["initial_state_hex"])
    require(len(header) == 2, "STATE", "Expected two initial opaque state bytes")
    state = dict(identity, sequence="0", input_offset="0", output_offset="0",
                 output_sha256=hashlib.sha256(b"").hexdigest(), worker_state=header.hex(), complete=False)
    hasher = hashlib.sha256()
    if journal.exists():
        state = unseal(load(journal), key)
        require(all(state.get(k) == v for k, v in identity.items()), "STATE_BINDING", "Continuation belongs to different input/worker/configuration")
        require(not state["complete"], "REPLAY", "Completed operation cannot be replayed")
        require(temporary.is_file(), "STATE_OUTPUT", "Missing previously committed output")
        with temporary.open("r+b") as pending:
            remaining = int(state["output_offset"])
            while remaining:
                block = pending.read(min(remaining, 1024 * 1024))
                require(block, "STATE_OUTPUT", "Committed output is truncated")
                hasher.update(block)
                remaining -= len(block)
            require(hasher.hexdigest() == state["output_sha256"], "STATE_OUTPUT", "Committed output was modified")
            pending.truncate(int(state["output_offset"]))
    else:
        require(not temporary.exists(), "ORPHAN", "Unjournaled partial output exists")
        temporary.touch(exist_ok=False)
        atomic_json(journal, seal(state, key))
    total_wall = 0.0
    with source.open("rb") as input_file, temporary.open("r+b") as output_file:
        input_file.seek(int(state["input_offset"]))
        output_file.seek(int(state["output_offset"]))
        while True:
            payload = input_file.read(chunk)
            # An empty input still exercises the BF worker's domain/profile check.
            if not payload and int(state["sequence"]) > 0:
                break
            output, opaque_state, wall = exchange(spec, payload, bytes.fromhex(state["worker_state"]))
            total_wall += wall
            require(output_file.tell() + len(output) <= spec["max_output_bytes"],
                    "OUTPUT_BUDGET", "Mapped output exceeds configured file budget")
            output_file.write(output)
            output_file.flush()
            os.fsync(output_file.fileno())
            hasher.update(output)
            state.update(sequence=str(int(state["sequence"]) + 1),
                         input_offset=str(input_file.tell()), output_offset=str(output_file.tell()),
                         output_sha256=hasher.hexdigest(), worker_state=opaque_state.hex())
            atomic_json(journal, seal(state, key), replace=True)
            if not payload:
                break
    require(digest(source) == identity["source_sha256"], "CHANGED", "Input changed during mapping")
    os.link(temporary, destination)
    os.unlink(temporary)
    state["complete"] = True
    atomic_json(journal, seal(state, key), replace=True)
    return {"input_bytes": int(state["input_offset"]), "output_bytes": int(state["output_offset"]),
            "records": int(state["sequence"]), "worker_wall_seconds": total_wall,
            "output_sha256": state["output_sha256"]}
