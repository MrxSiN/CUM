"""Generic exact-byte Git staging/object queries and opaque digest predicates.

No source language or camouflage pass is implemented here. Git supplies object
bytes; native BF selectors/predicates own private-value selection and rejection.
"""
import hashlib
import os
import re
import tempfile
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable, to_file
from .storage import atomic_json, confined, digest, inventory, load, verify_tree


def _env(spec):
    environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    environment.update(spec["environment"])
    return environment


def _git(spec, arguments):
    return checked([pinned_executable(spec["git"]), "--literal-pathspecs", "-C", spec["repository"],
                    "-c", "core.hooksPath=" + spec["empty_hooks_directory"], *arguments],
                   timeout=spec["timeout_seconds"], max_output=spec["max_metadata_bytes"], env=_env(spec))["stdout"]


def _expected(spec):
    record = load(spec["inventory"])
    require(record["format"] == "BYTE-TREE-PUBLIC-GIT", "FORMAT", "Portable signed public inventory required")
    verify_tree(spec["repository"], record)
    files = {entry["path"]: entry for entry in record["entries"] if entry["type"] == "file"}
    for name in spec["extra_paths"]:
        path = confined(spec["repository"], name)
        require(path.is_file(), "INVENTORY", "Missing release-sidecar file", path=name)
        files[name] = {"path": name, "sha256": digest(path), "executable": False}
    return files


def _blob_digest(spec, oid, directory):
    require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid), "GIT", "Noncanonical object identity")
    destination = Path(directory) / oid
    to_file([pinned_executable(spec["git"]), "-C", spec["repository"], "cat-file", "blob", oid],
            destination, timeout=spec["timeout_seconds"], max_bytes=spec["max_object_bytes"], env=_env(spec))
    value = digest(destination)
    destination.unlink()
    return value


def stage(spec):
    files = _expected(spec)
    for name, entry in files.items():
        oid = _git(spec, ["hash-object", "-w", "--no-filters", "--", name]).strip().decode("ascii")
        require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid), "GIT", "Invalid written blob identity")
        _git(spec, ["update-index", "--add", "--cacheinfo",
                    "100755" if entry["executable"] else "100644", oid, name])
    rows = _git(spec, ["ls-files", "-s", "-z"]).split(b"\0")
    observed = set()
    with tempfile.TemporaryDirectory(prefix="git-objects-", dir=spec["scratch_directory"]) as scratch:
        for row in rows:
            if not row:
                continue
            fields, path = row.split(b"\t", 1)
            mode, oid, stage_number = fields.decode("ascii").split()
            name = path.decode("utf-8")
            require(name in files and stage_number == "0", "GIT", "Unexpected/conflicted staged path")
            require(mode == ("100755" if files[name]["executable"] else "100644"), "PERMISSIONS", "Git index mode differs")
            require(_blob_digest(spec, oid, scratch) == files[name]["sha256"], "INTEGRITY", "Git filtering changed release bytes", path=name)
            observed.add(name)
    require(observed == set(files), "INVENTORY", "Git index is incomplete")
    return {"staged_files": len(observed)}


def audit(spec):
    files = _expected(spec)
    rows = _git(spec, ["ls-tree", "-r", "-z", "--full-tree", "HEAD"]).split(b"\0")
    observed = set()
    selector = pinned_executable(spec["selector"])
    predicate = pinned_executable(spec["predicate"])
    private = set(spec.get("additional_private_digests", []))
    for entry in load(spec["private_records"])[spec["record_list_field"]]:
        if spec["digest_field"] not in entry:
            continue
        request = bytes(entry[field] for field in spec["selection_fields"])
        result = checked([selector], stdin=request, timeout=spec["timeout_seconds"], max_output=16)["stdout"]
        require(result in (b"\x00", b"\x01"), "PREDICATE", "Malformed BF selection")
        if result == b"\x01":
            private.add(entry[spec["digest_field"]])
    def check_facts(facts):
        request = b"".join(bytes([1, value]) for value in facts) + b"\x00"
        require(len(request) <= spec["predicate_input_capacity"], "INPUT_CAPACITY", "Digest-fact record exceeds native capacity")
        result = checked([predicate], stdin=request, timeout=spec["timeout_seconds"], max_output=16)["stdout"]
        require(result == b"\x01", "CONFIDENTIALITY", "BF predicate found a forbidden exact byte digest in history")
    with tempfile.TemporaryDirectory(prefix="git-audit-", dir=spec["scratch_directory"]) as scratch:
        for row in rows:
            if not row:
                continue
            fields, path = row.split(b"\t", 1)
            mode, kind, oid = fields.decode("ascii").split()
            name = path.decode("utf-8")
            require(name in files and kind == "blob", "INVENTORY", "Unexpected committed path/type")
            require(mode == ("100755" if files[name]["executable"] else "100644"), "PERMISSIONS", "Committed executable contract differs")
            require(_blob_digest(spec, oid, scratch) == files[name]["sha256"], "INTEGRITY", "Committed release bytes differ")
            observed.add(name)
        require(observed == set(files), "INVENTORY", "Committed release is incomplete")
        objects = _git(spec, ["rev-list", "--objects", "--all", "--no-object-names"]).splitlines()
        require(len(objects) <= spec["max_objects"], "RESOURCE_BUDGET", "History exceeds explicit audit budget")
        facts, scanned = [], 0
        for encoded in objects:
            oid = encoded.decode("ascii")
            if _git(spec, ["cat-file", "-t", oid]).strip() != b"blob":
                continue
            facts.append(int(_blob_digest(spec, oid, scratch) in private))
            scanned += 1
            if len(facts) == spec["facts_per_record"]:
                check_facts(facts)
                facts.clear()
        if facts:
            check_facts(facts)
    record = {"format": "BF-GIT-PRIVACY-AUDIT", "status": "PASS", "blobs_scanned": scanned,
              "committed_files": len(observed), "scope": "Exact known private-byte digests, all fetched refs; not a proof against fragments or reconstruction"}
    atomic_json(spec["report"], record)
    return record
