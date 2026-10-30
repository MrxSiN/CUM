"""Generic immutable Git-commit export and explicit regular-tree archives."""
import io
import os
import re
import shutil
import tarfile
import tempfile
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable, to_file
from .storage import (atomic_json, canonical, confined, inventory, load, new_stage,
                      no_links, publish_tree, relative_name, remove_stage, verify_tree)


def _unpack_members(archive, stage, limits, manifest=None, *, members=None):
    seen, total, count = set(), 0, 0
    for member in (archive if members is None else members):
        name = member.name.rstrip("/") if member.isdir() else member.name
        relative_name(name)
        key = name.casefold()
        require(key not in seen, "COLLISION", "Duplicate archive path", path=name)
        seen.add(key)
        require(member.isfile() or member.isdir(), "TYPE", "Archive links/special files are unsupported")
        require(not member.pax_headers.get("linkpath"), "TYPE", "Archive link metadata is unsupported")
        count += 1
        total += member.size
        require(count <= limits["entries"] and total <= limits["bytes"],
                "RESOURCE_BUDGET", "Archive exceeds configured resource budget")
        path = confined(stage, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if member.isdir():
            path.mkdir(exist_ok=True)
        else:
            source = archive.extractfile(member)
            require(source is not None, "ARCHIVE", "Missing archive file body")
            with source, path.open("xb") as target:
                copied = 0
                while block := source.read(1024 * 1024):
                    target.write(block)
                    copied += len(block)
                require(copied == member.size, "TRUNCATED", "Truncated archive member")
            os.chmod(path, member.mode & 0o777)
    # Apply directory permissions after children have been written.
    if manifest:
        for entry in reversed(manifest["entries"]):
            if entry["type"] == "directory":
                os.chmod(confined(stage, entry["path"]), entry["mode"] & 0o777)


def capture(spec):
    """Capture committed, explicit paths, never the mutable developer worktree.

    Git archive's export attributes apply. Submodules and symlinks are rejected;
    untracked files and Git development history are explicitly outside this scope.
    """
    executable = pinned_executable(spec["git"])
    revision = spec["commit"]
    require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision), "COMMIT", "Full immutable commit required")
    paths = spec["paths"]
    require(paths and len(set(paths)) == len(paths), "SCOPE", "Explicit unique paths required")
    for path in paths:
        relative_name(path)
    root = str(Path(spec["repository"]).absolute())
    identity = checked([executable, "-C", root, "rev-parse", revision + "^{commit}"],
                       timeout=spec["timeout_seconds"], max_output=spec["max_metadata_bytes"])["stdout"].strip().decode("ascii")
    require(identity == revision, "COMMIT", "Reference is not an immutable commit")
    listing = checked([executable, "--literal-pathspecs", "-C", root, "ls-tree", "-r", "-z", revision, "--", *paths],
                      timeout=spec["timeout_seconds"], max_output=spec["max_metadata_bytes"])["stdout"]
    require(listing, "SCOPE", "No committed entries selected")
    for entry in listing.split(b"\0"):
        if entry:
            require(entry.split(b" ", 1)[0] in (b"100644", b"100755"),
                    "TYPE", "Selected scope contains a link, submodule or unsupported Git entry")
    destination = Path(spec["destination"])
    stage = new_stage(destination)
    try:
        with tempfile.TemporaryDirectory(prefix="byte-export-", dir=stage.parent) as temp:
            exported = Path(temp) / "export.tar"
            to_file([executable, "--literal-pathspecs", "-C", root, "archive", "--format=tar", revision, "--", *paths],
                    exported, timeout=spec["timeout_seconds"], max_bytes=spec["limits"]["bytes"])
            with tarfile.open(exported, "r:") as archive:
                _unpack_members(archive, stage, spec["limits"])
        record = inventory(stage)
        require(record["entries"], "SCOPE", "Export attributes excluded the complete selected scope")
        publish_tree(stage, destination)
        atomic_json(spec["manifest"], record)
        atomic_json(spec["provenance"], {"format": "BYTE-GIT-CAPTURE", "commit": identity,
                    "paths": paths, "scope": "Git archive export of explicit committed paths; no Git history"})
        return record
    finally:
        if stage.exists():
            remove_stage(stage)


def pack(spec):
    root = Path(spec["root"])
    record = load(spec["manifest"])
    verify_tree(root, record)
    require(not record["excludes"], "SCOPE", "Exact archive cannot omit entries")
    require(not (root / ".byte-tree.json").exists(), "COLLISION", "Archive metadata path is reserved")
    destination = Path(spec["destination"])
    require(not destination.exists(), "EXISTS", "Archive destination exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=destination.parent)
    os.close(fd)
    try:
        with tarfile.open(temporary, "w", format=tarfile.PAX_FORMAT) as archive:
            encoded = canonical(record)
            header = tarfile.TarInfo(".byte-tree.json")
            header.size = len(encoded)
            header.mode = 0o600
            archive.addfile(header, io.BytesIO(encoded))
            for item in record["entries"]:
                path = confined(root, item["path"])
                header = tarfile.TarInfo(item["path"])
                header.mode = item["mode"] & 0o777
                if item["type"] == "directory":
                    header.type = tarfile.DIRTYPE
                    archive.addfile(header)
                else:
                    header.size = item["size"]
                    with path.open("rb") as source:
                        archive.addfile(header, source)
        verify_tree(root, record)
        require(Path(temporary).stat().st_size <= spec["max_archive_bytes"],
                "RESOURCE_BUDGET", "Archive exceeds configured budget")
        os.link(temporary, destination)
    finally:
        os.unlink(temporary)


def extract(spec):
    source = Path(spec["source"])
    no_links(source)
    require(source.stat().st_size <= spec["limits"]["bytes"], "RESOURCE_BUDGET", "Archive exceeds configured budget")
    destination = Path(spec["destination"])
    stage = new_stage(destination)
    try:
        with tarfile.open(source, "r:") as archive:
            members = iter(archive)
            first = next(members, None)
            require(first is not None and first.name == ".byte-tree.json" and first.isfile(),
                    "FORMAT", "Missing archive scope record")
            require(first.size <= spec["limits"]["metadata_bytes"], "RESOURCE_BUDGET", "Scope record exceeds budget")
            data = archive.extractfile(first).read()
            with tempfile.TemporaryDirectory(prefix="byte-record-") as temp:
                record_path = Path(temp) / "record.json"
                record_path.write_bytes(data)
                record = load(record_path)
            require(canonical(record) == data, "FORMAT", "Noncanonical scope record")
            require(record.get("format") == "BYTE-TREE-SHA256-NFC" and record.get("excludes") == [],
                    "FORMAT", "Unsupported recovery scope")
            _unpack_members(archive, stage, spec["limits"], manifest=record, members=members)
        verify_tree(stage, record)
        publish_tree(stage, destination)
        if spec.get("manifest"):
            atomic_json(spec["manifest"], record)
        return record
    finally:
        if stage.exists():
            remove_stage(stage)


def copy_tree(spec):
    source = Path(spec["source"])
    before = inventory(source)
    stage = new_stage(spec["destination"])
    try:
        for entry in before["entries"]:
            target = confined(stage, entry["path"])
            if entry["type"] == "directory":
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(confined(source, entry["path"]), target)
        verify_tree(source, before)
        verify_tree(stage, before)
        publish_tree(stage, spec["destination"])
    finally:
        if stage.exists():
            remove_stage(stage)
