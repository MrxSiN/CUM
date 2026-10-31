"""Generic canonical records, confined regular-file trees and atomic writes.

The supported metadata scope is regular bytes, directories and POSIX permission
bits. Symlinks, junctions, device entries, ACLs, ADS and hardlink identity are not
silently claimed to be preserved.
"""
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath

from .errors import HostError, require


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "DUPLICATE_KEY", "Duplicate record key", key=key)
            result[key] = value
        return result
    with Path(path).open("r", encoding="utf-8") as source:
        return json.load(source, object_pairs_hook=unique)


def atomic_bytes(path, data, replace=False):
    path = Path(path).absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    require(replace or not path.exists(), "EXISTS", "Destination exists", path=str(path))
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(data)
            target.flush()
            os.fsync(target.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            # Hard-link publication does not overwrite an existing destination.
            os.link(temporary, path)
            os.unlink(temporary)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_json(path, value, replace=False):
    atomic_bytes(path, canonical(value), replace=replace)


def relative_name(name):
    require(isinstance(name, str) and name and "\\" not in name,
            "PATH", "Expected canonical relative POSIX path")
    require(unicodedata.normalize("NFC", name) == name, "PATH", "Noncanonical Unicode path")
    pure = PurePosixPath(name)
    require(not pure.is_absolute() and str(pure) == name, "PATH", "Noncanonical path", path=name)
    for part in pure.parts:
        require(part not in (".", "..") and not part.endswith((" ", ".")),
                "PATH", "Unsafe path segment", path=name)
        require(not any(ord(c) < 32 or c in '<>:"|?*' for c in part),
                "PATH", "Unsafe Windows path", path=name)
        require(not re.fullmatch(r"(?i:CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])", part.split(".")[0]),
                "PATH", "Reserved Windows name", path=name)
        require(part.casefold() != ".git", "PATH", "Git internals are not tree content")
    return pure


def no_links(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            st = item.lstat()
            require(not stat.S_ISLNK(st.st_mode) and not
                    (getattr(st, "st_file_attributes", 0) & 0x400),
                    "REPARSE", "Symlink/reparse point is outside the supported scope", path=str(item))


def confined(root, name):
    pure = relative_name(name)
    root = Path(root).absolute()
    no_links(root)
    target = root.joinpath(*pure.parts)
    no_links(target)
    require(target.is_relative_to(root), "PATH", "Path escapes root")
    return target


def inventory(root, excludes=(), *, public=False, executable_paths=()):
    root = Path(root).absolute()
    no_links(root)
    require(root.is_dir(), "TREE", "Missing tree", root=str(root))
    excluded = {str(relative_name(p)) for p in excludes}
    executable = {str(relative_name(p)) for p in executable_paths}
    result, seen = [], set()
    for base, dirs, files in os.walk(root, followlinks=False):
        if public and Path(base) == root:
            dirs[:] = [name for name in dirs if name.casefold() != ".git"]
            files[:] = [name for name in files if name.casefold() != ".git"]
        dirs.sort()
        files.sort()
        for name in dirs + files:
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            relative_name(rel)
            no_links(path)
            folded = rel.casefold()
            require(folded not in seen, "COLLISION", "Case-insensitive path collision", path=rel)
            seen.add(folded)
            st = path.lstat()
            require(stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode),
                    "TYPE", "Unsupported tree entry", path=rel)
            if rel in excluded:
                require(stat.S_ISREG(st.st_mode), "EXCLUDE", "Only individual files may be excluded")
                continue
            item = {"path": rel, "type": "directory" if path.is_dir() else "file"}
            if not public:
                item["mode"] = stat.S_IMODE(st.st_mode)
            if path.is_file():
                if public:
                    item["executable"] = rel in executable
                    if os.name != "nt":
                        require(not item["executable"] or bool(st.st_mode & 0o111), "PERMISSIONS", "Required public execution permission missing", path=rel)
                item.update(size=st.st_size, sha256=digest(path))
                after = path.stat()
                require((st.st_size, st.st_mtime_ns, st.st_ino) ==
                        (after.st_size, after.st_mtime_ns, after.st_ino),
                        "CHANGED", "File changed during inventory", path=rel)
            result.append(item)
    result.sort(key=lambda entry: entry["path"].encode("utf-8"))
    record = {"format": "BYTE-TREE-PUBLIC-GIT" if public else "BYTE-TREE-SHA256-NFC", "entries": result,
              "excludes": sorted(excluded)}
    if public:
        require(executable <= {entry["path"] for entry in result if entry["type"] == "file"}, "PERMISSIONS", "Execution policy names a missing file")
        record.update(executable_paths=sorted(executable), nonrelease_metadata=[".git"])
    return record


def verify_tree(root, record):
    require(record.get("format") in ("BYTE-TREE-SHA256-NFC", "BYTE-TREE-PUBLIC-GIT"), "FORMAT", "Unknown tree record")
    public = record["format"] == "BYTE-TREE-PUBLIC-GIT"
    require(inventory(root, record["excludes"], public=public, executable_paths=record.get("executable_paths", [])) == record,
            "INTEGRITY", "Tree inventory mismatch")


def new_stage(destination):
    destination = Path(destination).absolute()
    no_links(destination.parent)
    require(not destination.exists(), "EXISTS", "Destination exists", path=str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=".stage-", dir=destination.parent))


def publish_tree(stage, destination):
    destination = Path(destination).absolute()
    require(not destination.exists(), "EXISTS", "Destination exists")
    no_links(destination.parent)
    os.rename(stage, destination)


def remove_stage(path):
    # Only callers' explicit temporary stages may be removed, never a source tree.
    path = Path(path).absolute()
    require(path.name.startswith(".stage-"), "CLEANUP", "Refusing non-stage cleanup")
    no_links(path)
    original = sys.exc_info()[1]
    def retry_readonly(function, name, error):
        if not isinstance(error[1], PermissionError):
            raise error[1]
        target = Path(name).absolute()
        require(target.is_relative_to(path), "CLEANUP", "Cleanup escaped its stage")
        no_links(target)
        os.chmod(target, stat.S_IMODE(target.stat().st_mode) | stat.S_IWUSR)
        function(target)
    try:
        # Restored directory modes must not prevent removal of our own stage.
        os.chmod(path, stat.S_IMODE(path.stat().st_mode) | stat.S_IRWXU)
        for base, directories, _ in os.walk(path):
            for name in directories:
                directory = Path(base) / name
                no_links(directory)
                os.chmod(directory, stat.S_IMODE(directory.stat().st_mode) | stat.S_IRWXU)
        shutil.rmtree(path, onerror=retry_readonly)
    except Exception as error:
        if original is not None:
            original.add_note("Temporary stage cleanup failed: " + str(path) + ": " + str(error))
            if isinstance(original, HostError):
                original.details["cleanup_failure"] = {"stage": str(path), "reason": str(error)}
            raise original from error
        raise
