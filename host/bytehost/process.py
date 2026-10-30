"""Generic argument-vector process transport and network-disabled isolation."""
import os
import subprocess
import tempfile
import time
from pathlib import Path

from .errors import HostError, require
from .storage import digest, no_links
from .resources import ResourceSample


def run(argv, *, stdin=b"", timeout=60, max_output=1048576, cwd=None, env=None):
    require(isinstance(argv, list) and argv and all(isinstance(x, str) for x in argv),
            "ARGV", "Expected nonempty string argument vector")
    require(timeout > 0 and max_output >= 0, "BUDGET", "Invalid process budget")
    started = time.perf_counter()
    # Temporary files avoid deadlocks and unbounded in-memory pipe buffering.
    with tempfile.TemporaryFile() as input_file, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as error:
        input_file.write(stdin)
        input_file.seek(0)
        try:
            child = subprocess.Popen(argv, stdin=input_file, stdout=output, stderr=error,
                                     cwd=cwd, env=env, shell=False)
            counters = ResourceSample(child.pid)
        except OSError as exc:
            raise HostError("PROCESS_START", "Could not launch process", executable=argv[0], reason=str(exc)) from exc
        try:
            while child.poll() is None:
                if time.perf_counter() - started > timeout:
                    child.kill()
                    raise HostError("TIMEOUT", "Process exceeded time budget")
                if os.fstat(output.fileno()).st_size > max_output or os.fstat(error.fileno()).st_size > max_output:
                    child.kill()
                    raise HostError("OUTPUT_BUDGET", "Process exceeded output budget")
                time.sleep(0.01)
        finally:
            if child.poll() is None:
                child.kill()
            child.wait()
            resources = counters.finish()
        require(os.fstat(output.fileno()).st_size <= max_output and
                os.fstat(error.fileno()).st_size <= max_output,
                "OUTPUT_BUDGET", "Process exceeded output budget")
        output.seek(0)
        error.seek(0)
        stdout, stderr = output.read(), error.read()
    return {"exit": child.returncode, "stdout": stdout, "stderr": stderr,
            "wall_seconds": time.perf_counter() - started, "resources": resources}


def checked(argv, **kwargs):
    result = run(argv, **kwargs)
    require(result["exit"] == 0, "PROCESS_EXIT", "External process rejected operation",
            exit=result["exit"], stderr=result["stderr"].decode("utf-8", "replace"))
    return result


def to_file(argv, destination, *, timeout, max_bytes, cwd=None, env=None):
    """Stream stdout to a new file; do not materialize an archive in RAM."""
    destination = Path(destination)
    started = time.perf_counter()
    with destination.open("xb") as output, tempfile.TemporaryFile() as error:
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=output,
                                 stderr=error, cwd=cwd, env=env, shell=False)
        try:
            while child.poll() is None:
                require(time.perf_counter() - started <= timeout, "TIMEOUT", "Process exceeded time budget")
                require(os.fstat(output.fileno()).st_size <= max_bytes and
                        os.fstat(error.fileno()).st_size <= max_bytes,
                        "OUTPUT_BUDGET", "Process exceeded output budget")
                time.sleep(0.01)
        finally:
            if child.poll() is None:
                child.kill()
            child.wait()
        require(os.fstat(output.fileno()).st_size <= max_bytes, "OUTPUT_BUDGET", "Process exceeded output budget")
        error.seek(0)
        require(child.returncode == 0, "PROCESS_EXIT", "External file producer failed",
                exit=child.returncode, stderr=error.read(max_bytes).decode("utf-8", "replace"))
        output.flush()
        os.fsync(output.fileno())
    return {"wall_seconds": time.perf_counter() - started, "bytes": destination.stat().st_size}


def pinned_executable(spec):
    executable = Path(spec["executable"]).absolute()
    no_links(executable)
    require(executable.is_file() and digest(executable) == spec["sha256"],
            "TOOL_IDENTITY", "Executable does not match pinned digest", path=str(executable))
    return str(executable)


def isolated(spec):
    """No shell, image pulling, network, credentials or undeclared mounts.

    Uses either a preprovisioned pinned VM or a Linux container daemon and pinned
    image. The isolation implementation itself remains trusted infrastructure.
    """
    if spec.get("backend") == "qemu":
        from .qemu_isolation import isolated as vm_isolated
        return vm_isolated(spec)
    require(spec.get("backend", "docker") == "docker", "ISOLATION", "Unknown isolation backend")
    require("@sha256:" in spec["image"], "IMAGE", "Container image must be digest-pinned")
    executable = pinned_executable(spec["engine"])
    container = "bytehost-" + os.urandom(12).hex()
    argv = [executable, "run", "--name", container, "--rm", "--pull=never",
            "--network=none", "--read-only", "--cap-drop=ALL",
            "--security-opt=no-new-privileges", "--pids-limit", str(spec["pids"]),
            "--memory", str(spec["memory_bytes"]), "--cpus", str(spec["cpus"]),
            "--user", str(spec["user"]), "--tmpfs", "/tmp:rw,nosuid,nodev,size=" + str(spec["tmp_bytes"])]
    for mount in spec.get("mounts", []):
        path = Path(mount["source"]).absolute()
        if mount.get("create"):
            require(not mount["readonly"], "MOUNT", "Only explicit writable working mounts may be created")
            no_links(path.parent)
            path.mkdir(parents=True, exist_ok=True)
        no_links(path)
        require("," not in str(path) and "," not in mount["target"], "MOUNT", "Ambiguous mount")
        argv += ["--mount", "type=bind,source=" + str(path) + ",target=" + mount["target"] +
                 (",readonly" if mount["readonly"] else "")]
    for name, value in spec.get("environment", {}).items():
        import re
        require(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name), "ENVIRONMENT", "Invalid explicit environment name")
        argv += ["--env", name + "=" + value]
    argv += ["--workdir", spec.get("workdir", "/tmp"), spec["image"], *spec["argv"]]
    try:
        result = checked(argv, timeout=spec["timeout_seconds"], max_output=spec["max_output_bytes"])
        if spec.get("measurement_report"):
            import json
            from .storage import atomic_json
            observed = json.loads(result["stdout"])
            require(observed.get("format") == "CGROUP-PROCESS-OBSERVATION" and observed.get("status") == "PASS",
                    "METRIC", "Missing explicit container counter report")
            atomic_json(spec["measurement_report"], observed)
        return result
    finally:
        # Kill the container even if the CLI times out; killing the CLI alone is insufficient.
        run([executable, "rm", "-f", container], timeout=30, max_output=65536)
