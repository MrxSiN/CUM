"""Generic digest-pinned file allowlist bundling for independent tool packages."""
import os
import shutil
from pathlib import Path

from .errors import require
from .storage import (atomic_json, confined, digest, inventory, new_stage,
                      no_links, publish_tree, remove_stage)


def bundle(spec):
    require(spec["files"], "SCOPE", "Explicit verified runtime file allowlist required")
    stage = new_stage(spec["destination"])
    total = 0
    try:
        for item in spec["files"]:
            source = Path(item["source"])
            no_links(source)
            require(source.is_file() and digest(source) == item["sha256"], "TOOL_IDENTITY", "Runtime input differs from approved digest")
            total += source.stat().st_size
            require(total <= spec["max_bytes"], "RESOURCE_BUDGET", "Runtime bundle exceeds explicit byte budget")
            destination = confined(stage, item["path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            require(not destination.exists(), "COLLISION", "Duplicate runtime path")
            shutil.copy2(source, destination)
            require(digest(destination) == item["sha256"] and digest(source) == item["sha256"], "INTEGRITY", "Runtime input changed while bundling")
        record = inventory(stage)
        publish_tree(stage, spec["destination"])
        atomic_json(spec["manifest"], record)
        return record
    finally:
        if stage.exists():
            remove_stage(stage)
