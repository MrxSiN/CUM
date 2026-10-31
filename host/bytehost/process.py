"""Generic argument-vector process transport and network-disabled isolation."""
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from .errors import HostError, require
from .storage import digest, no_links
from .resources import ResourceSample


class _WindowsJob:
    def __init__(self):
        import ctypes as c
        from ctypes import wintypes as w
        self.c = c
        self.kernel = k = c.WinDLL("kernel32", use_last_error=True)
        class Basic(c.Structure):
            _fields_ = [("process_time", c.c_longlong), ("job_time", c.c_longlong),
                        ("flags", w.DWORD), ("minimum_working_set", c.c_size_t),
                        ("maximum_working_set", c.c_size_t), ("process_limit", w.DWORD),
                        ("affinity", c.c_size_t), ("priority", w.DWORD), ("scheduling", w.DWORD)]
        class Extended(c.Structure):
            _fields_ = [("basic", Basic), ("io", c.c_ulonglong * 6),
                        ("memory", c.c_size_t * 4)]
        class Thread(c.Structure):
            _fields_ = [("size", w.DWORD), ("usage", w.DWORD), ("tid", w.DWORD),
                        ("pid", w.DWORD), ("priority", w.LONG), ("delta", w.LONG), ("flags", w.DWORD)]
        class Accounting(c.Structure):
            _fields_ = [("times", c.c_longlong * 4), ("faults", w.DWORD),
                        ("total", w.DWORD), ("active", w.DWORD), ("terminated", w.DWORD)]
        self.Thread, self.Accounting = Thread, Accounting
        for name, result, arguments in (
            ("CreateJobObjectW", w.HANDLE, [c.c_void_p, w.LPCWSTR]),
            ("SetInformationJobObject", w.BOOL, [w.HANDLE, c.c_int, c.c_void_p, w.DWORD]),
            ("AssignProcessToJobObject", w.BOOL, [w.HANDLE, w.HANDLE]),
            ("TerminateJobObject", w.BOOL, [w.HANDLE, w.UINT]),
            ("QueryInformationJobObject", w.BOOL, [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p]),
            ("CreateToolhelp32Snapshot", w.HANDLE, [w.DWORD, w.DWORD]),
            ("Thread32First", w.BOOL, [w.HANDLE, c.POINTER(Thread)]),
            ("Thread32Next", w.BOOL, [w.HANDLE, c.POINTER(Thread)]),
            ("OpenThread", w.HANDLE, [w.DWORD, w.BOOL, w.DWORD]),
            ("ResumeThread", w.DWORD, [w.HANDLE]),
            ("CloseHandle", w.BOOL, [w.HANDLE]),
        ):
            function = getattr(k, name)
            function.restype, function.argtypes = result, arguments
        self.handle = k.CreateJobObjectW(None, None)
        self.check(self.handle)
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; no breakaway.
        if not k.SetInformationJobObject(self.handle, 9, c.byref(limits), c.sizeof(limits)):
            error = c.get_last_error()
            k.CloseHandle(self.handle)
            raise c.WinError(error)

    def check(self, success):
        if not success:
            raise self.c.WinError(self.c.get_last_error())

    def attach_and_resume(self, child):
        c, k = self.c, self.kernel
        self.check(k.AssignProcessToJobObject(self.handle, int(child._handle)))
        # Popen closes the primary thread handle; find it while the child is suspended.
        snapshot = k.CreateToolhelp32Snapshot(4, 0)
        self.check(snapshot != c.c_void_p(-1).value)
        try:
            entry = self.Thread()
            entry.size = c.sizeof(entry)
            found = k.Thread32First(snapshot, c.byref(entry))
            while found:
                if entry.pid == child.pid:
                    thread = k.OpenThread(2, False, entry.tid)
                    self.check(thread)
                    try:
                        self.check(k.ResumeThread(thread) != 0xffffffff)
                    finally:
                        k.CloseHandle(thread)
                    return
                found = k.Thread32Next(snapshot, c.byref(entry))
            raise HostError("PROCESS_TREE", "Suspended process thread was not found")
        finally:
            k.CloseHandle(snapshot)

    def close(self):
        c, k = self.c, self.kernel
        try:
            self.check(k.TerminateJobObject(self.handle, 1))
            deadline = time.monotonic() + 5
            counts = self.Accounting()
            while True:
                self.check(k.QueryInformationJobObject(self.handle, 1, c.byref(counts), c.sizeof(counts), None))
                if counts.active == 0:
                    break
                require(time.monotonic() < deadline, "PROCESS_TREE", "Process tree did not terminate")
                time.sleep(0.001)
        finally:
            k.CloseHandle(self.handle)


def _spawn(argv, **kwargs):
    if os.name != "nt":
        return subprocess.Popen(argv, start_new_session=True, **kwargs)
    job = _WindowsJob()
    child = None
    try:
        child = subprocess.Popen(argv, creationflags=0x4 | subprocess.CREATE_NO_WINDOW, **kwargs)
        job.attach_and_resume(child)
        child._bytehost_job = job
        return child
    except BaseException:
        if child is not None:
            child.kill()
            child.wait()
        job.close()
        raise


def _stop_tree(child):
    try:
        if os.name == "nt":
            child._bytehost_job.close()
        else:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    finally:
        child.wait()


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
            child = _spawn(argv, stdin=input_file, stdout=output, stderr=error,
                                     cwd=cwd, env=env, shell=False)
            counters = ResourceSample(child.pid)
        except OSError as exc:
            raise HostError("PROCESS_START", "Could not launch process", executable=argv[0], reason=str(exc)) from exc
        try:
            while child.poll() is None:
                if time.perf_counter() - started > timeout:
                    raise HostError("TIMEOUT", "Process exceeded time budget")
                if os.fstat(output.fileno()).st_size > max_output or os.fstat(error.fileno()).st_size > max_output:
                    raise HostError("OUTPUT_BUDGET", "Process exceeded output budget")
                time.sleep(0.01)
        finally:
            try:
                _stop_tree(child)
            finally:
                resources = counters.finish()
        require(os.fstat(output.fileno()).st_size <= max_output and
                os.fstat(error.fileno()).st_size <= max_output,
                "OUTPUT_BUDGET", "Process exceeded output budget")
        output.seek(0)
        error.seek(0)
        stdout, stderr = output.read(), error.read()
        input_offset = input_file.tell()
    return {"exit": child.returncode, "stdout": stdout, "stderr": stderr,
            "stdin_file_offset": input_offset,
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
        child = _spawn(argv, stdin=subprocess.DEVNULL, stdout=output,
                                 stderr=error, cwd=cwd, env=env, shell=False)
        try:
            while child.poll() is None:
                require(time.perf_counter() - started <= timeout, "TIMEOUT", "Process exceeded time budget")
                require(os.fstat(output.fileno()).st_size <= max_bytes and
                        os.fstat(error.fileno()).st_size <= max_bytes,
                        "OUTPUT_BUDGET", "Process exceeded output budget")
                time.sleep(0.01)
        finally:
            _stop_tree(child)
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
