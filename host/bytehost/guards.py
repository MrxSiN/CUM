"""Apply opaque BF predicates to generic tree metadata and explicit byte packets."""
from pathlib import Path

from .errors import require
from .storage import atomic_json, inventory, digest
from .worker import exchange


def guard_tree(spec):
    record = inventory(spec["root"], spec.get("excludes", []), public=spec.get("public", False),
                       executable_paths=spec.get("executable_paths", []))
    observations = []
    for entry in record["entries"]:
        payload = entry["path"].encode("utf-8")
        body, state, wall = exchange(spec["predicate"], payload, b"\x00\x00")
        require(body == b"", "PREDICATE", "Metadata predicate unexpectedly produced public bytes")
        observations.append({"path": entry["path"], "status": "PASS", "wall_seconds": wall})
    if spec.get("report"):
        atomic_json(spec["report"], {"format": "OPAQUE-TREE-PREDICATE", "entries": observations})
    return observations


def measured_predicate(spec):
    from .process import checked, pinned_executable
    from .storage import load
    require(spec["intervals"], "METRIC", "At least one explicit measured constraint is required")
    facts = []
    for interval in spec["intervals"]:
        record = load(interval["source"])
        for field in interval["fields"]:
            record = record[field]
        require(isinstance(record, (int, float)) and not isinstance(record, bool), "METRIC", "Missing measured value")
        facts.append(1 if interval["minimum"] <= record <= interval["maximum"] else 2)
    results = []
    executable = pinned_executable(spec["worker"])
    for fact in facts:
        request = bytes([spec["policy"], spec["eligibility_fact"], fact, spec["semantic_fact"]])
        response = checked([executable], stdin=request, timeout=spec["timeout_seconds"],
                           max_output=spec["max_response_bytes"])["stdout"]
        require(response in (b"\x01", b"\x02"), "BUDGET", "BF policy rejected measured budget")
        results.append(response[0])
    atomic_json(spec["report"], {"format": "BF-MEASURED-POLICY", "decisions": results,
                "meaning": "1 apply, 2 skip requested; skipped output is not release-ready"})
    if spec.get("decision_file"):
        from .storage import atomic_bytes
        from .transport import worker_input
        atomic_bytes(spec["decision_file"], worker_input(b"\x00\x00", bytes(results)))
    # A generic caller can require one exact decision; skipping must be handled
    # explicitly by a separate BF-authored plan, never passed off as acceptance.
    if spec.get("required_decision") is not None:
        require(all(result == spec["required_decision"] for result in results), "BUDGET", "Measured BF decision differs from required operation")
