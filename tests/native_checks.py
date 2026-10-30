"""Independent compiler/runtime/normalization checks for isolated environments.

No protection algorithm is implemented here. Original and already transformed
files are explicit operands. An external BBC does its own documented compiler
work. A real result record is written only after every selected check passes.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from host.bytehost.errors import HostError, require
from host.bytehost.process import checked, pinned_executable
from host.bytehost.storage import atomic_json, digest, inventory, load
from host.bytehost.transport import worker_input, worker_output
from host.bytehost.worker import exchange
from tests.reference import execute
from tests.tools.normalize import normalize


def compiler_prefix(spec):
    compiler = pinned_executable(spec["compiler"])
    if spec.get("launcher"):
        return [pinned_executable(spec["launcher"]), compiler]
    return [compiler]


def compile_one(spec, source, destination, optimization):
    prefix = compiler_prefix(spec)
    return checked([*prefix, "compile", "windows-x86_64", optimization, str(destination)],
                   stdin=source.read_bytes(), timeout=spec["compile_timeout_seconds"],
                   max_output=spec["max_log_bytes"])


def run_native(spec, artifact, data):
    argv = [str(artifact)]
    if spec.get("launcher"):
        argv.insert(0, pinned_executable(spec["launcher"]))
    return checked(argv, stdin=data, timeout=spec["runtime_timeout_seconds"],
                   max_output=spec["max_runtime_output_bytes"])


def verify(spec, case):
    results, runtime_observations = [], []
    observed_expansions, observed_binaries, observed_runtimes = [], [], []
    if case == "boundary":
        require(set(spec["workers"]) == {"echo", "fixed", "transform"},
                "FIXTURE", "All three independent boundary workers required")
        for name, artifact_spec in spec["workers"].items():
            binding = {"worker": artifact_spec, "input_capacity_bytes": spec["worker_input_capacity_bytes"],
                       "output_capacity_bytes": spec["max_runtime_output_bytes"],
                       "timeout_seconds": spec["runtime_timeout_seconds"]}
            if spec.get("launcher"):
                binding["launcher"] = spec["launcher"]
            payloads = (b"", b"\x00", b"\x01\x00\xff", bytes(range(256))) if name != "transform" else (b"", b"+++[.-]", b",[-].\x00")
            for payload in payloads:
                body, state, _ = exchange(binding, payload, b"\x02\x00")
                if name == "echo":
                    require(body == payload, "BINARY", "Native binary round trip mismatch")
                elif name == "fixed":
                    require(body == b"FIXED", "HOST_BOUNDARY", "Fixed-response component was not fixed")
                else:
                    require(execute(payload, b"\x02").output == execute(body, b"\x02").output,
                            "HOST_BOUNDARY", "Real BF transformation failed independent behavior check")
                _, handed_state, _ = exchange(binding, b"", state)
                require(handed_state == state, "STATE", "Cross-process continuation mismatch")
                require(state == b"\x02\x00", "STATE", "Opaque state handoff mismatch")
                results.append({"worker": name, "input_bytes": len(payload), "status": "PASS"})
        # The host's complete-frame and HMAC/continuation suite is independent of native workers.
        checked([sys.executable, "-m", "unittest", "tests.test_transport", "tests.test_storage"],
                timeout=spec["compile_timeout_seconds"], max_output=spec["max_log_bytes"])
    else:
        require(spec["fixtures"], "FIXTURE", "Empty comparison set is not evidence")
        with tempfile.TemporaryDirectory(prefix="independent-native-") as temporary:
            for index, fixture in enumerate(spec["fixtures"]):
                original = Path(spec["original"]) / fixture["path"]
                protected = Path(spec["protected"]) / fixture["path"]
                require(original.is_file() and protected.is_file(), "FIXTURE", "Missing comparison input")
                if case == "normalization":
                    original_bf = bytes(c for c in original.read_bytes() if c in b"><+-.,[]")
                    protected_bf = bytes(c for c in protected.read_bytes() if c in b"><+-.,[]")
                    require(original_bf != protected_bf, "STRUCTURAL", "Ignored-text filtering removed all changes")
                    require(normalize(original.read_bytes()) != normalize(protected.read_bytes()),
                            "NORMALIZATION", "Independent run/clear normalization erased executable changes")
                    bfx = []
                    for source in (original, protected):
                        result = checked([*compiler_prefix(spec), "emit-bfx", "-O1"], stdin=source.read_bytes(),
                                         timeout=spec["compile_timeout_seconds"], max_output=spec["max_bfx_bytes"])
                        bfx.append(result["stdout"])
                    require(bfx[0] != bfx[1], "NORMALIZATION", "BBC O1 normalized both programs to identical BFX")
                    results.append({"path": fixture["path"], "original_bfx_sha256": hashlib.sha256(bfx[0]).hexdigest(),
                                    "protected_bfx_sha256": hashlib.sha256(bfx[1]).hexdigest()})
                    continue
                for optimization in ("-O0", "-O1"):
                    artifacts = []
                    for label, source in (("original", original), ("protected", protected)):
                        artifact = Path(temporary) / (str(index) + label + optimization + ".exe")
                        compiled = compile_one(spec, source, artifact, optimization)
                        artifacts.append(artifact)
                        observed_binaries.append(artifact.stat().st_size)
                        results.append({"path": fixture["path"], "side": label, "optimization": optimization,
                                        "compile_wall_seconds": compiled["wall_seconds"], "binary_bytes": artifact.stat().st_size})
                    if case in ("behavior", "development", "budgets"):
                        for encoded in fixture["input_hex"]:
                            data = bytes.fromhex(encoded)
                            expected = execute(original.read_bytes(), data, steps=spec["reference_steps"]).output
                            outputs = [run_native(spec, artifact, data) for artifact in artifacts]
                            require(all(result["stdout"] == expected for result in outputs),
                                    "SEMANTICS", "Native/reference output mismatch")
                            require(outputs[0]["stdin_file_offset"] == outputs[1]["stdin_file_offset"],
                                    "SEMANTICS", "Original and protected runtimes consumed different physical input")
                            runtime_observations.append({"path": fixture["path"], "optimization": optimization,
                                "input_hex": encoded, "output_hex": expected.hex(),
                                "stdin_file_offsets": [item["stdin_file_offset"] for item in outputs]})
                            if case == "budgets":
                                expansion = protected.stat().st_size / max(1, original.stat().st_size)
                                observed_expansions.append(expansion)
                                observed_runtimes.append(outputs[1]["wall_seconds"])
                                if spec.get("enforce_numeric_budgets", True):
                                    require(expansion <= spec["budgets"]["source_expansion_ratio"], "BUDGET", "Source expansion exceeds budget")
                                    require(artifacts[1].stat().st_size <= spec["budgets"]["max_binary_bytes"], "BUDGET", "Binary size exceeds budget")
                                    require(outputs[1]["wall_seconds"] <= spec["budgets"]["max_runtime_seconds"], "BUDGET", "Runtime exceeds budget")
    record = {"format": "INDEPENDENT-NATIVE-CHECK", "status": "PASS", "case": case,
              "execution_environment": "emulation" if spec.get("launcher") else "native Windows process",
              "compiler_sha256": spec.get("compiler", {}).get("sha256"), "results": results,
              "runtime_observations": runtime_observations}
    record["metrics"] = {"source_expansion_ratio": max(observed_expansions) if observed_expansions else None,
                         "max_binary_bytes": max(observed_binaries) if observed_binaries else None,
                         "max_runtime_seconds": max(observed_runtimes) if observed_runtimes else None}
    atomic_json(spec["report"], record)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=("build", "behavior", "normalization", "boundary", "budgets", "development"))
    parser.add_argument("binding")
    arguments = parser.parse_args()
    try:
        verify(load(arguments.binding), arguments.case)
    except HostError as exc:
        sys.stderr.write(json.dumps(exc.record()) + "\n")
        raise SystemExit(1)
