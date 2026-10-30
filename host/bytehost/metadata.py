"""Apply a native-produced named UTF-8 suffix to explicit tree directories.

The byte program chooses the name/content. No Git or source grammar lives here.
Only the staged output's declared portable execution permissions are changed.
"""
import os
from pathlib import Path
from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_bytes, confined, inventory, relative_name


def directory_blob(spec):
    result = checked([pinned_executable(spec["worker"])], timeout=spec["timeout_seconds"],
                     max_output=spec["max_response_bytes"])["stdout"]
    require(result[:8] == b"DIRBLOB\0" and len(result) >= 9, "FORMAT", "Unknown directory-blob descriptor")
    length = result[8]
    require(length > 0 and len(result) >= 9 + length, "FORMAT", "Truncated directory-blob name")
    name = result[9:9 + length].decode("utf-8")
    require(len(relative_name(name).parts) == 1, "PATH", "Directory blob needs a leaf name")
    suffix = result[9 + length:]
    suffix.decode("utf-8")
    require(b"\0" not in suffix, "FORMAT", "Text suffix contains NUL")
    root = Path(spec["root"])
    before = inventory(root)
    directories = [root] + [confined(root, entry["path"]) for entry in before["entries"] if entry["type"] == "directory"]
    for directory in directories:
        target = directory / name
        original = target.read_bytes() if target.exists() else b""
        original.decode("utf-8")
        require(b"\0" not in original and len(original) + len(suffix) <= spec["max_file_bytes"],
                "RESOURCE_BUDGET", "Invalid/oversized text metadata")
        if target.exists():
            os.chmod(target, 0o644)
        atomic_bytes(target, original + suffix, replace=target.exists())
    executable = set(spec["executable_paths"])
    for entry in inventory(root)["entries"]:
        target = confined(root, entry["path"])
        os.chmod(target, 0o755 if entry["type"] == "directory" or entry["path"] in executable else 0o644)
    return inventory(root, public=True, executable_paths=executable)
