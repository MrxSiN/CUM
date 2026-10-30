"""Generic tree projection driven only by a pinned byte decision component.

Captured recovery-only bytes are never copied merely because they exist in a
snapshot. The BF program decides inclusion from previously observed approval and
explicit disposition data. The host supplies byte copies and tree confinement.
"""
import os
import shutil
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable
from .storage import (atomic_json, confined, inventory, load, new_stage,
                      publish_tree, remove_stage, verify_tree)


def project(spec):
    source = Path(spec["source"])
    scope = load(spec["manifest"])
    verify_tree(source, scope)
    entries = load(spec["discovery"])["entries"]
    metadata = [{key: value for key, value in entry.items() if key not in
                ("classification_byte", "disposition_byte", "review_byte", "approval_byte")} for entry in entries]
    require(metadata == scope["entries"], "SCOPE", "Discovery belongs to a different immutable scope")
    decision = pinned_executable(spec["worker"])
    stage = new_stage(spec["destination"])
    copied = []
    included = set()
    try:
        for entry in entries:
            response = checked([decision], stdin=bytes([entry["approval_byte"], entry["disposition_byte"]]),
                               timeout=spec["timeout_seconds"], max_output=16)["stdout"]
            require(response in (b"\x00\x00", b"\x01\x00"), "SCOPE", "BF refused public projection")
            if response[0] == 0:
                continue
            parts = entry["path"].split("/")
            require(all("/".join(parts[:index]) in included for index in range(1, len(parts))),
                    "SCOPE", "Included entry has an excluded/unapproved parent", path=entry["path"])
            target = confined(stage, entry["path"])
            if entry["type"] == "directory":
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(confined(source, entry["path"]), target)
            copied.append(entry)
            included.add(entry["path"])
        for entry in reversed(copied):
            if entry["type"] == "directory":
                os.chmod(confined(stage, entry["path"]), entry["mode"])
        verify_tree(source, scope)
        record = inventory(stage)
        publish_tree(stage, spec["destination"])
        atomic_json(spec["report"], {"format": "BF-PUBLIC-PROJECTION", "public_inventory": record})
        return record
    finally:
        if stage.exists():
            remove_stage(stage)
