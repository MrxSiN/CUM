"""Generic explicit Windows regular-tree capture using deny-write file handles.

All selected file handles remain locked while the materialized scope is copied.
No source classification, secret policy or transformation occurs here.
"""
import ctypes
import os
import shutil
import stat
from contextlib import ExitStack
from pathlib import Path

from .errors import require
from .storage import (atomic_json, confined, inventory, new_stage, no_links,
                      publish_tree, relative_name, remove_stage, verify_tree)


def _locked_read(path):
    require(os.name == "nt", "ISOLATION", "Live directory capture requires Windows deny-write handles; use Git capture elsewhere")
    import msvcrt
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                                  ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    handle = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x00200080, None)
    require(handle != ctypes.c_void_p(-1).value, "CAPTURE_LOCK", "Could not acquire deny-write capture handle",
            path=str(path), windows_error=ctypes.get_last_error())
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except Exception:
        kernel.CloseHandle(ctypes.c_void_p(handle))
        raise
    return os.fdopen(descriptor, "rb")


def _entries(root, names):
    selected = {}
    for name in names:
        path = confined(root, name)
        require(path.exists(), "SCOPE", "Selected capture entry is missing", path=name)
        candidates = [path]
        if path.is_dir():
            for base, dirs, files in os.walk(path, followlinks=False):
                candidates.extend(Path(base) / value for value in dirs + files)
        for candidate in candidates:
            no_links(candidate)
            relative = candidate.relative_to(root).as_posix()
            relative_name(relative)
            require(relative.casefold() not in selected, "SCOPE", "Duplicate/overlapping capture paths", path=relative)
            metadata = candidate.lstat()
            require(stat.S_ISREG(metadata.st_mode) or stat.S_ISDIR(metadata.st_mode), "TYPE", "Unsupported capture entry")
            selected[relative.casefold()] = {"path": relative,
                "type": "directory" if candidate.is_dir() else "file", "mode": stat.S_IMODE(metadata.st_mode)}
    return sorted(selected.values(), key=lambda entry: entry["path"].encode("utf-8"))


def capture_directory(spec):
    require(spec["paths"], "SCOPE", "Explicit capture paths required")
    root = Path(spec["root"]).absolute()
    no_links(root)
    entries = _entries(root, spec["paths"])
    require(len(entries) <= spec["max_entries"], "RESOURCE_BUDGET", "Capture exceeds entry budget")
    destination = Path(spec["destination"]).absolute()
    stage = new_stage(destination)
    try:
        with ExitStack() as locks:
            readers = {}
            for entry in entries:
                if entry["type"] == "file":
                    readers[entry["path"]] = locks.enter_context(_locked_read(confined(root, entry["path"])))
            require(_entries(root, spec["paths"]) == entries, "CHANGED", "Scope changed while capture locks were acquired")
            total = 0
            for entry in entries:
                path = confined(stage, entry["path"])
                if entry["type"] == "directory":
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("xb") as output:
                        while block := readers[entry["path"]].read(1024 * 1024):
                            total += len(block)
                            require(total <= spec["max_bytes"], "RESOURCE_BUDGET", "Capture exceeds byte budget")
                            output.write(block)
                    os.chmod(path, entry["mode"])
            for entry in reversed(entries):
                if entry["type"] == "directory":
                    os.chmod(confined(stage, entry["path"]), entry["mode"])
            require(_entries(root, spec["paths"]) == entries, "CHANGED", "Scope changed during capture")
            record = inventory(stage)
            publish_tree(stage, destination)
            atomic_json(spec["manifest"], record)
        return record
    finally:
        if stage.exists():
            remove_stage(stage)
