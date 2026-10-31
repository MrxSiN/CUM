"""Optional generic content-addressed storage for pure byte-worker results.

Only independently pinned byte inputs/tools/configuration identify an entry.
Caching is a draft service, not a measured optimization or release evidence.
"""
import hashlib
import os
from pathlib import Path

from .errors import require
from .storage import (atomic_json, canonical, digest, load, no_links,
                      new_stage, publish_tree, remove_stage)
from .worker import seal, unseal


def store(spec):
    key = Path(spec["authentication_key"]).read_bytes()
    require(len(key) >= 32, "STATE_KEY", "Cache authentication key too short")
    identity = spec["identity"]
    name = hashlib.sha256(canonical(identity)).hexdigest()
    root = Path(spec["root"]) / name
    no_links(root.parent)
    source = Path(spec["source"])
    no_links(source)
    require(source.is_file(), "TYPE", "Cache source must be a regular file")
    total = source.stat().st_size
    require(total <= spec["max_bytes"], "RESOURCE_BUDGET", "Cache entry exceeds explicit budget")
    record = {"format": "OPAQUE-CACHE-HMAC-SHA256", "identity": identity,
              "bytes": total, "sha256": digest(source)}
    stage = new_stage(root)
    try:
        copied = 0
        with source.open("rb") as input_file, (stage / "payload").open("xb") as output:
            for block in iter(lambda: input_file.read(1024 * 1024), b""):
                copied += len(block)
                require(copied <= spec["max_bytes"], "RESOURCE_BUDGET", "Cache entry exceeds explicit budget")
                output.write(block)
            output.flush()
            os.fsync(output.fileno())
        require(copied == total and digest(stage / "payload") == record["sha256"] and
                digest(source) == record["sha256"], "INTEGRITY", "Cache payload changed")
        atomic_json(stage / "record.json", seal(record, key))
        publish_tree(stage, root)
    finally:
        if stage.exists():
            remove_stage(stage)
    return {"identity_sha256": name}


def retrieve(spec):
    key = Path(spec["authentication_key"]).read_bytes()
    name = hashlib.sha256(canonical(spec["identity"])).hexdigest()
    root = Path(spec["root"]) / name
    no_links(root)
    record = unseal(load(root / "record.json"), key)
    require(record["identity"] == spec["identity"] and digest(root / "payload") == record["sha256"],
            "INTEGRITY", "Cache identity/content mismatch")
    from .vm import copy_file
    copy_file({"source": str(root / "payload"), "destination": spec["destination"]})
    return record
