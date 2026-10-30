"""Generic one-job guest agent. Install in the independently pinned VM image.

The guest has no host mounts or network device. This agent only exchanges opaque
files, executes an argument vector as an unprivileged user, and returns outputs.
"""
import base64
import ctypes
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import resource
import signal
import struct
import subprocess
import tarfile
import tempfile
import time

MAGIC = b"BYTEVM\x00\x01"


def exact(stream, length):
    data = bytearray()
    while len(data) < length:
        block = stream.read(length - len(data))
        if not block:
            raise ValueError("Truncated VM packet")
        data.extend(block)
    return bytes(data)


def receive(stream, limit):
    if exact(stream, 8) != MAGIC:
        raise ValueError("Unknown VM packet")
    length = struct.unpack(">Q", exact(stream, 8))[0]
    if length > limit:
        raise ValueError("VM packet budget exceeded")
    checksum, data = exact(stream, 32), exact(stream, length)
    if hashlib.sha256(data).digest() != checksum:
        raise ValueError("VM packet checksum mismatch")
    return json.loads(data)


def send(stream, value):
    data = json.dumps(value, separators=(",", ":"), allow_nan=False).encode()
    remaining = memoryview(MAGIC + struct.pack(">Q", len(data)) + hashlib.sha256(data).digest() + data)
    while remaining:
        written = stream.write(remaining)
        if not written:
            raise ValueError("Closed VM output")
        remaining = remaining[written:]
    stream.flush()


def target_path(value):
    path = PurePosixPath(value)
    if not path.is_absolute() or str(path) != value or ".." in path.parts or len(path.parts) < 2:
        raise ValueError("Invalid guest mount")
    if path.parts[1] in ("dev", "proc", "sys", "etc", "usr", "bin", "sbin", "lib", "lib64", "opt", "root", "boot", "run", "tmp", "home"):
        raise ValueError("Mount would cover the guest runtime")
    return Path(value)


def execute(job):
    mounts = job["mounts"]
    roots = [target_path(item["target"]) for item in mounts]
    if any(left == right or left in right.parents or right in left.parents
           for i, left in enumerate(roots) for right in roots[i + 1:]):
        raise ValueError("Overlapping guest mounts")
    archive = base64.b64decode(job["input_tar"], validate=True)
    for root in roots:
        root.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        seen = set()
        for member in source:
            path = PurePosixPath(member.name)
            if (str(path) != member.name or path.is_absolute() or ".." in path.parts or
                    "\\" in member.name or member.name in seen or not (member.isdir() or member.isfile())):
                raise ValueError("Unsafe input archive")
            seen.add(member.name)
            index = int(path.parts[0])
            if not 0 <= index < len(roots) or len(path.parts) < 2:
                raise ValueError("Unknown input mount")
            destination = roots[index].joinpath(*path.parts[1:])
            destination.parent.mkdir(parents=True, exist_ok=True)
            if member.isdir():
                destination.mkdir(exist_ok=True)
            else:
                with source.extractfile(member) as body, destination.open("xb") as output:
                    while block := body.read(1024 * 1024):
                        output.write(block)
                os.chmod(destination, 0o444 | (member.mode & 0o111))
    uid, gid = (int(value) for value in job["user"].split(":"))
    if uid <= 0 or gid <= 0:
        raise ValueError("Root jobs are unsupported")
    for mount, root in zip(mounts, roots):
        for path in [root, *root.rglob("*")]:
            if path.is_dir():
                os.chmod(path, 0o755)
            if not mount["readonly"]:
                os.chown(path, uid, gid)
                os.chmod(path, 0o755 if path.is_dir() else 0o644 | (path.stat().st_mode & 0o111))
    def restrict():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_NPROC, (job["pids"], job["pids"]))
        resource.setrlimit(resource.RLIMIT_FSIZE, (job["max_artifact_bytes"], job["max_artifact_bytes"]))
        if ctypes.CDLL(None).prctl(38, 1, 0, 0, 0) != 0:
            raise RuntimeError("Could not establish no-new-privileges")
        os.setgroups([])
        os.setgid(gid)
        os.setuid(uid)
    environment = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "HOME": "/tmp", "LANG": "C.UTF-8"}
    environment.update(job["environment"])
    started = time.monotonic()
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        child = subprocess.Popen(job["argv"], cwd=job["workdir"], env=environment, stdin=subprocess.DEVNULL,
                                 stdout=stdout, stderr=stderr, preexec_fn=restrict)
        try:
            while child.poll() is None:
                if time.monotonic() - started > job["timeout_seconds"]:
                    raise TimeoutError("Guest job exceeded time budget")
                if max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > job["max_output_bytes"]:
                    raise ValueError("Guest process output budget exceeded")
                time.sleep(0.02)
        finally:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
        if max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > job["max_output_bytes"]:
            raise ValueError("Guest process output budget exceeded")
        stdout.seek(0)
        stderr.seek(0)
        result = {"exit": child.returncode, "stdout": base64.b64encode(stdout.read()).decode(),
                  "stderr": base64.b64encode(stderr.read()).decode(), "wall_seconds": time.monotonic() - started,
                  "network_interfaces": sorted(os.listdir("/sys/class/net")), "uid": uid}
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as output:
        if child.returncode == 0:
            for index, item in enumerate(job["outputs"]):
                path = Path(item["guest"])
                if not any(not mount["readonly"] and root in path.parents for mount, root in zip(mounts, roots)):
                    raise ValueError("Output is outside declared writable mounts")
                if any(parent.is_symlink() for parent in [path, *path.parents]) or not path.is_file():
                    raise ValueError("Output must be a regular confined file")
                output.add(path, arcname=str(index), recursive=False)
                if buffer.tell() > job["max_archive_bytes"]:
                    raise ValueError("Guest archive budget exceeded")
    if buffer.tell() > job["max_archive_bytes"]:
        raise ValueError("Guest archive budget exceeded")
    result["output_tar"] = base64.b64encode(buffer.getvalue()).decode()
    return result


def main():
    device = Path("/dev/virtio-ports/bytevm")
    while not device.exists():
        time.sleep(0.2)
    nonce, budget = Path("/sys/class/dmi/id/product_serial").read_text().strip().split(":")
    with device.open("r+b", buffering=0) as stream:
        send(stream, {"status": "READY", "nonce": nonce})
        try:
            job = receive(stream, int(budget))
            if job.pop("nonce") != nonce:
                raise ValueError("VM nonce mismatch")
            response = {"status": "PASS", "result": execute(job)}
        except Exception as error:
            response = {"status": "FAIL", "error": type(error).__name__, "message": str(error)}
        send(stream, response)


if __name__ == "__main__":
    main()
