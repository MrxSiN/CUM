"""Pinned, disposable QEMU VM execution without guest networking or host shares."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import tarfile
import tempfile
import time

from .errors import HostError, require
from .process import checked, pinned_executable
from .storage import atomic_bytes, atomic_json, canonical, digest, no_links
from .resources import ResourceSample
from pathlib import PurePosixPath

MAGIC = b"BYTEVM\x00\x01"


def packet(value):
    data = canonical(value)
    return MAGIC + struct.pack(">Q", len(data)) + hashlib.sha256(data).digest() + data


def receive(stream, limit, *, deadline=None):
    def exact(count):
        output = bytearray()
        while len(output) < count:
            if deadline is not None:
                remaining = deadline - time.monotonic()
                require(remaining > 0, "TIMEOUT", "VM response exceeded its wall deadline")
                stream.settimeout(remaining)
            try:
                block = stream.recv(count - len(output))
            except OSError as error:
                raise HostError("TIMEOUT" if isinstance(error, TimeoutError) else "VM_TRANSPORT",
                                "VM response transport failed", reason=str(error)) from error
            require(block, "VM_TRUNCATED", "Guest closed an incomplete response")
            output.extend(block)
        return bytes(output)
    require(exact(8) == MAGIC, "FORMAT", "Unknown VM response")
    length = struct.unpack(">Q", exact(8))[0]
    require(length <= limit, "OUTPUT_BUDGET", "Guest packet exceeds declared budget")
    checksum, data = exact(32), exact(length)
    require(hashlib.sha256(data).digest() == checksum, "INTEGRITY", "Guest packet checksum mismatch")
    return json.loads(data)


def isolated(spec):
    vm = spec["vm"]
    executable, image_tool = pinned_executable(vm["qemu"]), pinned_executable(vm["qemu_img"])
    image = Path(vm["disk"]["file"]).absolute()
    no_links(image)
    require(digest(image) == vm["disk"]["sha256"] and spec["image"] == "BYTEVM-IMAGE@sha256:" + vm["disk"]["sha256"],
            "IMAGE", "VM image differs from its independent pin")
    image_info = json.loads(checked([image_tool, "info", "--output=json", str(image)], timeout=30)["stdout"])
    require(image_info["format"] == "qcow2" and not image_info.get("backing-filename") and
            not image_info.get("format-specific", {}).get("data", {}).get("data-file"),
            "IMAGE", "VM images must be self-contained QCOW2 files")
    scratch = Path(vm["scratch_directory"]).absolute()
    no_links(scratch)
    require("," not in str(image) and "," not in str(scratch), "PATH", "Ambiguous QEMU storage path")
    scratch.mkdir(parents=True, exist_ok=True)
    require(type(spec["memory_bytes"]) is int and spec["memory_bytes"] >= 128 * 1024 * 1024 and
            type(spec["cpus"]) is int and spec["cpus"] > 0, "BUDGET", "Invalid VM resource budgets")
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w") as output:
        for index, mount in enumerate(spec["mounts"]):
            source = Path(mount["source"]).absolute()
            no_links(source)
            if mount.get("create"):
                require(not mount["readonly"], "MOUNT", "Only writable inputs may be created")
                source.mkdir(parents=True, exist_ok=True)
            require(source.is_dir(), "MOUNT", "VM mount sources must be explicit directories")
            for directory, dirs, files in os.walk(source, followlinks=False):
                for name in sorted(dirs + files):
                    path = Path(directory) / name
                    no_links(path)
                    require(path.is_file() or path.is_dir(), "TYPE", "Unsupported VM input type")
                    output.add(path, arcname=str(index) + "/" + path.relative_to(source).as_posix(), recursive=False)
                    require(archive.tell() <= vm["max_archive_bytes"], "INPUT_CAPACITY", "VM input exceeds its explicit archive budget")
    require(archive.tell() <= vm["max_archive_bytes"], "INPUT_CAPACITY", "VM input exceeds its explicit archive budget")
    for item in spec.get("outputs", []):
        path = PurePosixPath(item["guest"])
        require(path.is_absolute() and str(path) == item["guest"] and ".." not in path.parts,
                "PATH", "Invalid guest output path")
    job = {key: spec[key] for key in ("argv", "workdir", "user", "pids", "environment", "timeout_seconds", "max_output_bytes")}
    job.update(mounts=[{"target": item["target"], "readonly": item["readonly"]} for item in spec["mounts"]],
               input_tar=base64.b64encode(archive.getvalue()).decode(), outputs=[{"guest": item["guest"]} for item in spec.get("outputs", [])],
               max_archive_bytes=vm["max_archive_bytes"], max_artifact_bytes=vm["max_artifact_bytes"], nonce=os.urandom(32).hex())
    request = packet(job)
    require(len(request) <= vm["max_packet_bytes"], "INPUT_CAPACITY", "VM request exceeds its explicit packet budget")
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="bytevm-", dir=scratch) as temporary:
        directory = Path(temporary).absolute()
        require(directory.is_relative_to(scratch), "PATH", "VM scratch escaped its controlled root")
        overlay = directory / "job.qcow2"
        checked([image_tool, "create", "-f", "qcow2", "-F", "qcow2", "-b", str(image), str(overlay)], timeout=30)
        argv = [executable, "-accel", "tcg,thread=multi", "-cpu", "max", "-m", str(spec["memory_bytes"] // 1048576),
                "-smp", str(spec["cpus"]), "-display", "none", "-monitor", "none", "-nic", "none", "-no-reboot",
                "-serial", "file:" + str(directory / "console.log"),
                "-drive", "file=" + str(overlay) + ",if=virtio,format=qcow2",
                "-device", "virtio-serial-pci", "-chardev", "socket,id=control,host=127.0.0.1,port=" + str(port) + ",server=on,wait=off",
                "-device", "virtserialport,chardev=control,name=bytevm",
                "-smbios", "type=1,serial=" + job["nonce"] + ":" + str(vm["max_packet_bytes"])]
        with (directory / "stderr.log").open("wb") as error:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=error,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            counters = ResourceSample(child.pid)
            counters_finished = False
            try:
                deadline = started + vm["boot_timeout_seconds"]
                while True:
                    require(child.poll() is None, "VM_BOOT", "QEMU exited before accepting a job")
                    try:
                        stream = socket.create_connection(("127.0.0.1", port), timeout=1)
                        break
                    except OSError:
                        require(time.monotonic() < deadline, "TIMEOUT", "VM transport did not become available")
                        time.sleep(0.1)
                with stream:
                    stream.settimeout(max(1, deadline - time.monotonic()))
                    ready = receive(stream, 4096, deadline=deadline)
                    require(ready == {"status": "READY", "nonce": job["nonce"]}, "VM_BOOT", "Guest readiness identity differs")
                    stream.settimeout(spec["timeout_seconds"] + 10)
                    response_deadline = time.monotonic() + spec["timeout_seconds"] + 10
                    stream.sendall(request)
                    response = receive(stream, vm["max_packet_bytes"], deadline=response_deadline)
                require(response.get("status") == "PASS", "VM_JOB", "Guest rejected the job", response=response)
                result = response["result"]
                require(result["network_interfaces"] == ["lo"], "ISOLATION", "Guest unexpectedly has a network interface")
                require(result["exit"] == 0, "PROCESS_EXIT", "Isolated guest process rejected operation",
                        exit=result["exit"], stderr=base64.b64decode(result["stderr"]).decode("utf-8", "replace"))
                encoded = base64.b64decode(result.pop("output_tar"), validate=True)
                require(len(encoded) <= vm["max_archive_bytes"], "OUTPUT_BUDGET", "Guest artifact archive exceeds budget")
                outputs = []
                with tarfile.open(fileobj=io.BytesIO(encoded), mode="r:") as returned:
                    for index, member in enumerate(returned):
                        require(index < len(spec.get("outputs", [])) and member.name == str(index) and member.isfile(),
                                "FORMAT", "Unexpected returned artifact")
                        body = returned.extractfile(member).read()
                        require(len(body) == member.size, "VM_TRUNCATED", "Incomplete returned artifact")
                        outputs.append(body)
                require(len(outputs) == len(spec.get("outputs", [])), "FORMAT", "Missing declared output artifact")
                for item, body in zip(spec.get("outputs", []), outputs):
                    destination = Path(item["destination"]).absolute()
                    no_links(destination.parent)
                    atomic_bytes(destination, body, replace=item.get("replace", False))
                result.update(stdout=base64.b64decode(result["stdout"], validate=True),
                              stderr=base64.b64decode(result["stderr"], validate=True),
                              guest_wall_seconds=result["wall_seconds"], wall_seconds=time.monotonic() - started,
                              isolation="QEMU TCG, disposable disk overlay, no guest NIC or host filesystem shares")
                result["resources"] = counters.finish()
                counters_finished = True
                if spec.get("measurement_report"):
                    require(result["resources"]["status"] == "PASS", "METRIC", "VM process counters are unavailable")
                    atomic_json(spec["measurement_report"], {"format": "QEMU-PROCESS-OBSERVATION", "status": "PASS",
                                "scope": "Entire host QEMU process including guest and emulation overhead",
                                "peak_memory_bytes": result["resources"]["peak_working_set_bytes"],
                                "resources": result["resources"], "wall_seconds": result["wall_seconds"]})
                return result
            finally:
                if not counters_finished:
                    counters.finish()
                if child.poll() is None:
                    child.kill()
                child.wait()
