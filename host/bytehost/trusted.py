"""Pinned external tools on the trusted side of the host boundary.

Use only reviewed generic compilers, Git and signing utilities here. Project
scripts/executables belong in the isolation service. No shell expansion occurs.
"""
import os
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_json, digest, no_links


def invoke(spec):
    executable = pinned_executable(spec["tool"])
    for name, expected in spec.get("inputs_sha256", {}).items():
        no_links(name)
        require(digest(name) == expected, "TOOL_IDENTITY", "Trusted tool input differs from its independent pin", path=name)
    data = Path(spec["stdin_file"]).read_bytes() if spec.get("stdin_file") else b""
    environment = None
    if spec.get("clear_environment_prefixes") or spec.get("environment"):
        environment = {key: value for key, value in os.environ.items()
                       if not any(key.upper().startswith(prefix.upper()) for prefix in spec.get("clear_environment_prefixes", []))}
        environment.update(spec.get("environment", {}))
    result = checked([executable, *spec["argv"]], stdin=data, timeout=spec["timeout_seconds"],
                     max_output=spec["max_output_bytes"], cwd=spec.get("cwd"), env=environment)
    if "expected_stdout_hex" in spec:
        require(result["stdout"] == bytes.fromhex(spec["expected_stdout_hex"]), "TOOL_RESPONSE", "Pinned tool response differs from approved bytes")
    record = {"format": "PINNED-TOOL-RECEIPT", "tool_sha256": spec["tool"]["sha256"],
              "inputs_sha256": spec.get("inputs_sha256", {}),
              "argv": spec["argv"], "exit": result["exit"], "wall_seconds": result["wall_seconds"],
              "resources": result["resources"],
              "stdout_hex": result["stdout"].hex(), "stderr_hex": result["stderr"].hex()}
    if spec.get("report"):
        atomic_json(spec["report"], record)
    return record


def replace_file(spec):
    source, destination = Path(spec["source"]), Path(spec["destination"])
    no_links(source)
    no_links(destination)
    require(source.is_file() and destination.is_file(), "DESTINATION", "Replacement needs two regular files")
    if "expected_digest_record" in spec:
        from .storage import load
        expected = load(spec["expected_digest_record"])[spec["expected_digest_field"]]
    else:
        expected = spec["expected_destination_sha256"]
    require(digest(destination) == expected, "STALE", "Replacement base changed")
    require(source.parent.resolve() == destination.parent.resolve(), "ATOMIC", "Atomic replacement requires same directory")
    os.replace(source, destination)


def append_record(spec):
    from .storage import canonical, load
    destination = Path(spec["destination"])
    no_links(destination.parent)
    destination.parent.mkdir(parents=True, exist_ok=True)
    record = dict(spec["fields"])
    record["digests"] = {name: digest(path) for name, path in spec["files"].items()}
    with destination.open("ab") as output:
        output.write(canonical(record))
        output.flush()
        os.fsync(output.fileno())
    return record


def copy_replacements(spec):
    """Generic checked byte-copy replacement of explicit destination files."""
    import shutil
    import stat
    import tempfile
    require(spec["files"], "SCOPE", "No explicit replacement files")
    for entry in spec["files"]:
        source, destination = Path(entry["source"]).absolute(), Path(entry["destination"]).absolute()
        no_links(source)
        no_links(destination)
        require(source != destination and source.is_file() and destination.is_file(), "DESTINATION", "Invalid copy replacement")
        original_source, original_destination = digest(source), digest(destination)
        descriptor, pending = tempfile.mkstemp(prefix=".pending-", dir=destination.parent)
        try:
            with source.open("rb") as input_file, os.fdopen(descriptor, "wb") as output:
                shutil.copyfileobj(input_file, output, length=1024 * 1024)
                output.flush()
                os.fsync(output.fileno())
            require(digest(pending) == original_source and digest(source) == original_source and
                    digest(destination) == original_destination, "CHANGED", "Replacement inputs changed")
            os.chmod(pending, stat.S_IMODE(source.stat().st_mode))
            os.replace(pending, destination)
        finally:
            if os.path.exists(pending):
                os.unlink(pending)


def assert_filesystem(spec):
    for name in spec.get("absent", []):
        path = Path(name)
        no_links(path.parent)
        require(not path.exists() and not path.is_symlink(), "EXISTS", "Filesystem precondition requires absence", path=str(path))
    for name in spec.get("empty_directories", []):
        path = Path(name)
        no_links(path.parent)
        path.mkdir(parents=True, exist_ok=True)
        no_links(path)
        require(not any(path.iterdir()), "EXISTS", "Expected empty controlled directory")
