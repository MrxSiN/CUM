"""Generic command surface. Application command numbers are opaque to the host."""
import argparse
import io
import json
import sys
from pathlib import Path

from .errors import HostError, require
from .storage import atomic_bytes, canonical, load
from .transport import frame, read_frame, worker_input, worker_output
from .process import checked, pinned_executable
from .vm import SERVICES, flow
from .worker import exchange, map_file


def main():
    parser = argparse.ArgumentParser(description="Generic native byte-worker host")
    sub = parser.add_subparsers(dest="operation", required=True)
    invoke = sub.add_parser("service")
    invoke.add_argument("opcode", type=int)
    invoke.add_argument("binding")
    mapper = sub.add_parser("map")
    mapper.add_argument("binding")
    pipeline = sub.add_parser("flow")
    pipeline.add_argument("binding")
    pipeline.add_argument("--command", required=True, type=int)
    pipeline.add_argument("--mode", default=1, type=int)
    transport = sub.add_parser("exchange")
    transport.add_argument("binding")
    transport.add_argument("--input", required=True)
    transport.add_argument("--output", required=True)
    application = sub.add_parser("app")
    application.add_argument("binding")
    application.add_argument("request", nargs="+")
    application.add_argument("--mode", default=1, type=int)
    args = parser.parse_args()
    spec = load(args.binding)
    if args.operation == "service":
        require(args.opcode in SERVICES, "OPCODE", "Unknown service")
        result = SERVICES[args.opcode](spec)
    elif args.operation == "map":
        result = map_file(spec)
    elif args.operation == "flow":
        result = flow(spec, args.command, args.mode)
    elif args.operation == "app":
        parser_spec = spec["command_worker"]
        request = worker_input(bytes([args.mode, 0]), " ".join(args.request).encode("utf-8"))
        require(len(request) <= parser_spec["input_capacity_bytes"], "INPUT_CAPACITY", "Command record exceeds parser transport")
        response = checked([pinned_executable(parser_spec["worker"])], stdin=request,
                           timeout=parser_spec["timeout_seconds"], max_output=parser_spec["output_capacity_bytes"])
        command, state = worker_output(response["stdout"])
        require(len(command) == 2, "COMMAND", "Malformed BF command response")
        result = flow(spec, command[0], command[1])
    else:
        with Path(args.input).open("rb") as source:
            header, payload = read_frame(source, max_header=spec["max_header_bytes"],
                                         max_payload=spec["record_payload_bytes"])
        # Every request is operation/sequence-bound by its independently supplied expected envelope.
        require({k: header[k] for k in ("operation", "request", "sequence", "state")} == spec["expected"],
                "REQUEST_BINDING", "Unexpected, stale, reordered or duplicate request")
        output, state, wall = exchange(spec, payload, bytes.fromhex(header["state"]))
        response = {"operation": header["operation"], "request": header["request"],
                    "sequence": str(int(header["sequence"]) + 1), "state": state.hex()}
        atomic_bytes(args.output, frame(response, output))
        result = {"worker_wall_seconds": wall, "output_bytes": len(output)}
    if isinstance(result, dict):
        result = dict(result)
        for field in ("stdout", "stderr"):
            if isinstance(result.get(field), bytes):
                require(field + "_hex" not in result, "FORMAT", "Ambiguous binary service output")
                result[field + "_hex"] = result.pop(field).hex()
    sys.stdout.buffer.write(canonical({"status": "PASS", "result": result}))


if __name__ == "__main__":
    try:
        main()
    except HostError as exc:
        sys.stderr.buffer.write(canonical(exc.record()))
        raise SystemExit(1)
    except (OSError, ValueError, KeyError, TypeError, MemoryError, OverflowError) as exc:
        sys.stderr.buffer.write(canonical({"status": "FAIL", "error": type(exc).__name__, "message": str(exc)}))
        raise SystemExit(2)
    except Exception as exc:
        sys.stderr.buffer.write(canonical({"status": "FAIL", "error": "SERVICE_FAILURE",
                                           "exception": type(exc).__name__, "message": str(exc)}))
        raise SystemExit(2)
