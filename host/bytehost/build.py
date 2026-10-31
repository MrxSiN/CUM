"""Generic BBC native compilation driver, outside restricted compiler repos.

Only invokes the existing compiler interface. There is no BF parser, BFX emitter,
XAX store generator or interpreter fallback here.
"""
import argparse
import hashlib
from pathlib import Path

from .errors import HostError, require
from .process import checked, pinned_executable
from .storage import atomic_json, digest, load


def build(spec):
    executable = pinned_executable(spec["compiler"])
    output = Path(spec["output_directory"]).absolute()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for source_name in spec["sources"]:
        source = Path(source_name).absolute()
        artifact = output / (source.stem + (".exe" if spec["target"] == "windows-x86_64" else ""))
        require(not artifact.exists(), "EXISTS", "Native artifact destination exists")
        data = source.read_bytes()
        source_sha256 = hashlib.sha256(data).hexdigest()
        result = checked([executable, "compile", spec["target"], spec["optimization"], str(artifact)],
                         stdin=data, timeout=spec["timeout_seconds"],
                         max_output=spec["max_log_bytes"])
        require(artifact.is_file(), "COMPILER_OUTPUT", "Compiler succeeded without native artifact")
        require(digest(source) == source_sha256, "CHANGED", "Source changed during compilation")
        records.append({"source": str(source), "source_sha256": source_sha256,
                        "artifact": str(artifact), "artifact_sha256": digest(artifact),
                        "compiler_sha256": digest(executable), "target": spec["target"],
                        "optimization": spec["optimization"], "wall_seconds": result["wall_seconds"],
                        "native_execution": "NOT STARTED"})
    atomic_json(spec["report"], {"format": "BYTE-NATIVE-BUILD", "records": records})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invoke pinned BBC on explicit Brainfuck sources")
    parser.add_argument("binding")
    arguments = parser.parse_args()
    try:
        build(load(arguments.binding))
    except HostError as exc:
        raise SystemExit(str(exc.record()))
