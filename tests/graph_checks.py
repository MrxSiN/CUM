"""Independent native XAX verification/build/runtime and PE code comparison."""
import argparse
import struct
import tempfile
from pathlib import Path

from host.bytehost.errors import require
from host.bytehost.process import checked, pinned_executable
from host.bytehost.storage import atomic_json, load, digest


def code_section(path):
    data = Path(path).read_bytes()
    require(data[:2] == b"MZ" and len(data) >= 64, "PE", "Expected Windows image")
    pe = struct.unpack_from("<I", data, 60)[0]
    require(data[pe:pe + 4] == b"PE\0\0", "PE", "Invalid PE signature")
    count = struct.unpack_from("<H", data, pe + 6)[0]
    size = struct.unpack_from("<H", data, pe + 20)[0]
    start = pe + 24 + size
    for index in range(count):
        header = start + index * 40
        require(header + 40 <= len(data), "PE", "Truncated section table")
        if data[header:header + 8].rstrip(b"\0") == b".text":
            length, offset = struct.unpack_from("<II", data, header + 16)
            require(offset + length <= len(data), "PE", "Truncated code section")
            return data[offset:offset + length]
    require(False, "PE", "No executable code section observed")


def verify(spec):
    compiler = pinned_executable(spec["compiler"])
    compiler_launcher = spec.get("compiler_launcher", spec.get("launcher"))
    runtime_launcher = spec.get("runtime_launcher", spec.get("launcher"))
    prefix = [pinned_executable(compiler_launcher), compiler] if compiler_launcher else [compiler]
    observations, artifacts, runtime_samples = [], [], []
    with tempfile.TemporaryDirectory(prefix="independent-xax-") as temporary:
        for label in ("original", "protected"):
            source = Path(spec[label])
            stem = str(Path(temporary) / label)
            checked([*prefix, "verify", str(source), stem + ".diag"], timeout=spec["timeout_seconds"], max_output=1048576)
            checked([*prefix, "resolve", str(source), stem + ".snapshot"], timeout=spec["timeout_seconds"], max_output=1048576)
            build = checked([*prefix, "build", stem + ".snapshot", stem + ".exe", stem + ".provenance"],
                            timeout=spec["timeout_seconds"], max_output=1048576)
            artifacts.append(Path(stem + ".exe"))
            observations.append({"side": label, "source_sha256": digest(source),
                                 "build_wall_seconds": build["wall_seconds"], "resources": build["resources"]})
        require(digest(spec["original"]) != digest(spec["protected"]), "STRUCTURAL", "Canonical stores are unchanged")
        if spec["require_native_code_change"]:
            require(code_section(artifacts[0]) != code_section(artifacts[1]), "NORMALIZATION", "Native backend erased graph changes")
        require(spec["inputs_hex"], "FIXTURE", "Actual behavior inputs required")
        for value in spec["inputs_hex"]:
            results = []
            for artifact in artifacts:
                argv = [str(artifact)]
                if runtime_launcher:
                    argv.insert(0, pinned_executable(runtime_launcher))
                results.append(checked(argv, stdin=bytes.fromhex(value), timeout=spec["runtime_timeout_seconds"], max_output=65536))
            require(results[0]["stdout"] == results[1]["stdout"], "SEMANTICS", "Native XAX behavior differs")
            runtime_samples.append(results[1]["wall_seconds"])
        metrics = {"source_expansion_ratio": Path(spec["protected"]).stat().st_size / max(1, Path(spec["original"]).stat().st_size),
                   "max_binary_bytes": artifacts[1].stat().st_size, "max_runtime_seconds": max(runtime_samples)}
    atomic_json(spec["report"], {"format": "INDEPENDENT-XAX-CHECK", "status": "PASS", "observations": observations,
                "compiler_sha256": spec["compiler"]["sha256"],
                "metrics": metrics, "native_authority": "Pinned XAX native verify/resolve/build commands; no SDK build fallback"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binding")
    arguments = parser.parse_args()
    verify(load(arguments.binding))
