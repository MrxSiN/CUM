"""Generic two-byte workflow VM. Only a pinned byte program chooses instructions.

Bindings are operands, not a second workflow: they supply paths, tool identities,
budgets and argument vectors. No binding can add conditional execution or source
rewrites. Any service rejection aborts the remaining instruction stream.
"""
import hashlib
import os
import platform
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

from . import archive, crypto
from .errors import HostError, require
from .process import checked, isolated, pinned_executable
from .storage import (atomic_bytes, atomic_json, canonical, confined, digest, inventory,
                      load, no_links, publish_tree, verify_tree)
from .worker import map_file
from .assembly import assemble
from .dispatch import machine_tree, dispatch_list
from .trusted import invoke, replace_file, append_record, copy_replacements, assert_filesystem
from .git_transport import stage as git_stage, audit as git_audit
from .scope import capture_directory
from .cache import store as cache_store, retrieve as cache_retrieve
from .metrics import collect as collect_metrics, paired as paired_metrics
from .guards import guard_tree, measured_predicate
from .discovery import discover
from .securestore import create_private_directory
from .projection import project
from .bundle import bundle
from .metadata import directory_blob
from .trusted_recovery import trusted_isolated


def inspect_tool(spec):
    executable = pinned_executable(spec["tool"])
    result = checked([executable, *spec.get("argv", [])], timeout=spec["timeout_seconds"],
                     max_output=spec["max_output_bytes"])
    record = {"format": "BYTE-TOOL-OBSERVATION", "executable_sha256": digest(executable),
              "stdout_hex": result["stdout"].hex(), "stderr_hex": result["stderr"].hex(),
              "argv": spec.get("argv", []), "platform": platform.platform()}
    if "repository" in spec:
        git = pinned_executable(spec["git"])
        commit = checked([git, "-C", spec["repository"], "rev-parse", "HEAD"],
                         timeout=spec["timeout_seconds"], max_output=spec["max_output_bytes"])
        record["repository_commit"] = commit["stdout"].strip().decode("ascii")
        if "expected_commit" in spec:
            require(record["repository_commit"] == spec["expected_commit"],
                    "TOOLCHAIN_COMMIT", "Compiler repository changed since job binding")
    atomic_json(spec["report"], record)
    return record


def map_tree(spec):
    root = Path(spec["root"])
    names = spec["paths"]
    require(names and len(set(names)) == len(names), "SCOPE", "Explicit unique mapping paths required")
    results = []
    for index, name in enumerate(names):
        source = confined(root, name)
        require(source.is_file(), "SCOPE", "Mapping input is not a regular file")
        destination = source.with_name(source.name + ".mapped")
        request = dict(spec["mapping"], source=str(source), destination=str(destination),
                       journal=str(Path(spec["journal_directory"]) / (str(index) + ".json")))
        result = map_file(request)
        os.replace(destination, source)
        results.append({"path": name, **result})
    atomic_json(spec["report"], {"format": "BYTE-MAP-REPORT", "files": results})
    return results


def write_inventory(spec):
    record = inventory(spec["root"], spec.get("excludes", []), public=spec.get("public", False),
                       executable_paths=spec.get("executable_paths", []))
    atomic_json(spec["destination"], record)
    return {"sha256": hashlib.sha256(canonical(record)).hexdigest()}


def compose_record(spec):
    """Generic content-address binding; no implicit release/signature exclusions."""
    record = dict(spec["fields"])
    for name, observation in spec.get("observed_fields", {}).items():
        require(name not in record, "RECORD", "Observed field cannot replace a literal field")
        value = load(observation["file"])
        for field in observation["fields"]:
            value = value[field]
        record[name] = value
    require("digests" not in record, "RECORD", "Reserved record field")
    record["digests"] = {name: digest(path) for name, path in spec["files"].items()}
    atomic_json(spec["destination"], record)
    return record


def verify_inventory(spec):
    verify_tree(spec["root"], load(spec["inventory"]))
    if "binding_record" in spec:
        record = load(spec["binding_record"])
        for field, expected in spec.get("expected_fields", {}).items():
            require(record.get(field) == expected, "FORMAT", "Bound record field mismatch", field=field)
        require(set(record["digests"]) == set(spec["files"]), "INVENTORY", "Unexpected bound artifact set")
        for name, path in spec["files"].items():
            require(digest(path) == record["digests"][name], "INTEGRITY", "Bound artifact was modified", name=name)


def compare_tree(spec):
    require(inventory(spec["left"]) == inventory(spec["right"]), "RECOVERY_MISMATCH", "Trees differ")


def assert_record(spec):
    """Exact expected fields in an externally authenticated review record.

    Signature verification is a separate VM instruction; selecting both is the
    byte program's responsibility. This service does not make legal judgments.
    """
    record = load(spec["source"])
    for key, expected in spec["fields"].items():
        require(record.get(key) == expected, "REVIEW", "Required review evidence is absent", field=key)
    for field, path in spec.get("file_digests", {}).items():
        require(record.get(field) == digest(path), "REVIEW_BINDING", "Review is bound to different input", field=field)
    for field, path in spec.get("digest_fields", {}).items():
        require(record["digests"].get(field) == digest(path), "INTEGRITY", "Bound record digest differs", field=field)


def copy_file(spec):
    source, destination = Path(spec["source"]), Path(spec["destination"])
    no_links(source)
    no_links(destination.parent)
    require(not destination.exists(), "EXISTS", "Copy destination exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_file, destination.open("xb") as output:
        shutil.copyfileobj(input_file, output, length=1024 * 1024)
        output.flush()
        os.fsync(output.fileno())
    require(digest(source) == digest(destination), "INTEGRITY", "Copy mismatch")


def measurements(spec):
    """Generic repeated isolated process measurements, after correctness evidence.

    Peak memory must be supplied by a pinned measurement tool's report. Wall
    clock and stdout byte count are observed here; no fabricated RAM numbers.
    """
    assert_record(spec["correctness_evidence"])
    require(spec["repetitions"] > 0, "SAMPLES", "Positive repetition count required")
    samples = []
    for _ in range(spec["repetitions"]):
        samples.append(isolated(spec["process"])["wall_seconds"])
    result = {"format": "BYTE-WALL-SAMPLES", "samples_seconds": samples,
              "median_seconds": statistics.median(samples),
              "min_seconds": min(samples), "max_seconds": max(samples),
              "peak_memory": None, "peak_memory_status": "NOT STARTED",
              "context": spec["context"]}
    atomic_json(spec["destination"], result)
    return result


def numeric_budget(spec):
    record = load(spec["source"])
    observed = record[spec["field"]]
    require(isinstance(observed, (int, float)) and not isinstance(observed, bool),
            "METRIC", "Missing numeric measurement")
    require(spec["minimum"] <= observed <= spec["maximum"], "BUDGET", "Configured resource budget exceeded")


def byte_assertion(spec):
    executable = pinned_executable(spec["worker"])
    payload = bytes.fromhex(spec["input_hex"])
    require(len(payload) == spec["input_bytes"], "RECORD_LENGTH", "Incomplete byte-program request")
    result = checked([executable], stdin=payload,
                     timeout=spec["timeout_seconds"], max_output=spec["max_output_bytes"])
    require(result["stdout"] == bytes.fromhex(spec["expected_hex"]),
            "BYTE_ASSERTION", "Byte program refused request")


SERVICES = {
    1: inspect_tool,
    2: archive.capture,
    3: lambda s: verify_tree(s["root"], load(s["manifest"])),
    4: archive.pack,
    5: crypto.envelope,
    6: lambda s: crypto.envelope(s, decrypt=True),
    7: archive.extract,
    8: compare_tree,
    9: map_tree,
    10: isolated,
    11: write_inventory,
    12: compose_record,
    13: crypto.sign,
    14: crypto.verify_signature,
    15: verify_inventory,
    17: lambda s: publish_tree(s["source"], s["destination"]),
    18: archive.copy_tree,
    19: assert_record,
    20: measurements,
    21: numeric_budget,
    23: copy_file,
    24: byte_assertion,
    25: invoke,
    26: machine_tree,
    27: assemble,
    28: lambda s: flow(s, s["command"], s.get("mode", 1)),
    29: dispatch_list,
    30: append_record,
    31: replace_file,
    32: capture_directory,
    33: cache_store,
    34: cache_retrieve,
    35: collect_metrics,
    36: paired_metrics,
    37: guard_tree,
    38: measured_predicate,
    39: discover,
    40: copy_replacements,
    41: create_private_directory,
    42: project,
    43: bundle,
    44: trusted_isolated,
    45: git_stage,
    46: git_audit,
    47: directory_blob,
    48: assert_filesystem,
}


def flow(spec, command, mode=1):
    planner = pinned_executable(spec["planner"])
    request = Path(spec["request_file"]).read_bytes() if spec.get("request_file") else bytes((command, mode))
    require(len(request) <= spec.get("planner_input_bytes", 65536), "INPUT_CAPACITY", "Planner input exceeds declared transport")
    planner_argv = [planner]
    if spec.get("planner_launcher"):
        planner_argv.insert(0, pinned_executable(spec["planner_launcher"]))
    response = checked(planner_argv, stdin=request, timeout=spec["planner_timeout_seconds"],
                       max_output=spec["planner_output_bytes"])["stdout"]
    require(response and response[-1] == 0 and len(response) % 2 == 1,
            "PLAN", "Decision program rejected command or emitted malformed instructions")
    plan = [(response[i], response[i + 1]) for i in range(0, len(response) - 1, 2)]
    bindings = spec["bindings"]
    # Validate every operand before performing any side effect.
    for opcode, operand in plan:
        require(opcode in SERVICES or opcode in (16, 22), "OPCODE", "Unknown VM instruction")
        require(opcode == 22 or str(operand) in bindings, "BINDING", "Missing instruction operand", operand=operand)
    require(plan, "PLAN", "Empty decision plan")
    journal_path = Path(spec["journal"])
    require(not journal_path.exists(), "REPLAY", "Flow journal already exists; interrupted flows require a new operation")
    journal = {"format": "BYTE-FLOW-RECEIPTS", "planner_sha256": digest(planner),
               "request_hex": request.hex(), "plan_hex": response.hex(),
               "bindings_sha256": hashlib.sha256(canonical(bindings)).hexdigest(),
               "status": "PARTIAL", "receipts": []}
    atomic_json(journal_path, journal)
    receipts, selected = {}, []
    try:
        for sequence, (opcode, operand) in enumerate(plan):
            started = time.perf_counter()
            if opcode == 22:
                # A byte program selects evidence; missing evidence is not success.
                selected.append(1 if receipts.get(operand) == "PASS" else 0)
                continue
            binding = bindings[str(operand)]
            if opcode == 16:
                predicate = pinned_executable(binding["worker"])
                require(len(selected) == binding["input_bytes"], "EVIDENCE",
                        "Evidence record does not match predicate input contract")
                result = checked([predicate], stdin=bytes(selected), timeout=binding["timeout_seconds"],
                                 max_output=binding["max_output_bytes"])
                require(result["stdout"] == b"\x01", "EVIDENCE", "Decision predicate refused evidence")
                selected.clear()
            else:
                SERVICES[opcode](binding)
            receipts[operand] = "PASS"
            journal["receipts"].append({"sequence": sequence, "opcode": opcode,
                         "operand": operand, "status": "PASS",
                         "wall_seconds": time.perf_counter() - started})
            if spec.get("receipt_directory"):
                atomic_json(Path(spec["receipt_directory"]) / (str(operand) + ".json"),
                            journal["receipts"][-1], replace=True)
            atomic_json(journal_path, journal, replace=True)
        journal["status"] = "PASS"
        atomic_json(journal_path, journal, replace=True)
        return journal
    except Exception as exc:
        journal["status"] = "FAIL"
        journal["error"] = exc.record() if isinstance(exc, HostError) else {"error": type(exc).__name__, "message": str(exc)}
        atomic_json(journal_path, journal, replace=True)
        raise
