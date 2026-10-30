"""Generic digest-pinned file allowlist bundling for independent tool packages."""
import os
import shutil
from pathlib import Path

from .errors import require
from .storage import (atomic_json, confined, digest, inventory, new_stage,
                      no_links, publish_tree, relative_name, remove_stage, load, verify_tree)


def bundle(spec):
    files = list(spec["files"])
    trees = spec.get("trees", [])
    directories = []
    for tree in trees:
        require(digest(tree["manifest"]) == tree["manifest_sha256"],
                "TOOL_IDENTITY", "Runtime distribution inventory differs from independent pin")
        record = load(tree["manifest"])
        require(record["format"] == "BYTE-TREE-SHA256-NFC" and not record["excludes"],
                "FORMAT", "Runtime distribution must have an exact private inventory")
        verify_tree(tree["source"], record)
        prefix = str(relative_name(tree["path"]))
        directories.extend({"path": prefix + "/" + item["path"], "mode": item["mode"]}
                           for item in record["entries"] if item["type"] == "directory")
        files.extend({"source": str(confined(tree["source"], item["path"])),
                      "path": prefix + "/" + item["path"], "sha256": item["sha256"]}
                     for item in record["entries"] if item["type"] == "file")
    require(files, "SCOPE", "Explicit verified runtime file allowlist required")
    stage = new_stage(spec["destination"])
    total = 0
    try:
        for item in directories:
            confined(stage, item["path"]).mkdir(parents=True, exist_ok=True)
        for item in files:
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
        for tree in trees:
            verify_tree(tree["source"], load(tree["manifest"]))
        for item in reversed(directories):
            os.chmod(confined(stage, item["path"]), item["mode"])
        record = inventory(stage)
        publish_tree(stage, spec["destination"])
        atomic_json(spec["manifest"], record)
        return record
    finally:
        if stage.exists():
            remove_stage(stage)
