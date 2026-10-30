"""Enumerate generic file metadata and ask BF to classify/approve every entry."""
from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_json, inventory
from .worker import exchange


def discover(spec):
    entries = inventory(spec["root"])["entries"]
    observed = []
    policy = pinned_executable(spec["policy"])
    for entry in entries:
        body, state, wall = exchange(spec["classifier"], entry["path"].encode("utf-8"), b"\x00\x00")
        require(len(body) == 1, "CLASSIFICATION", "Malformed BF classification")
        require(entry["path"] in spec["dispositions"], "SCOPE", "Unreviewed entry disposition", path=entry["path"])
        review = spec.get("entry_reviews", {}).get(entry["path"], spec["review_fact"])
        request = bytes([body[0], spec["dispositions"][entry["path"]], review, 1 if entry["type"] == "file" else 2])
        result = checked([policy], stdin=request, timeout=spec["timeout_seconds"], max_output=16)
        require(result["stdout"] == b"\x01", "SCOPE", "BF scope policy refused entry", path=entry["path"])
        observed.append({**entry, "classification_byte": body[0], "disposition_byte": request[1],
                         "review_byte": review, "approval_byte": result["stdout"][0]})
    atomic_json(spec["report"], {"format": "BF-PROJECT-DISCOVERY", "entries": observed})
    return observed
