"""Build only delivered public BF with standard tools and the Python stdlib.

This guest has no original/reference tree, credentials, CUM kernels or CUM host
runtime. It independently checks the documented Byte Relay fixture contract.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


if __name__ == "__main__":
    compiler_sha, source_sha = sys.argv[1:]
    compiler, source, wine = Path("/tools/bbc.exe"), Path("/release/main.bf"), "/usr/lib/wine/wine64"
    assert hashlib.sha256(compiler.read_bytes()).hexdigest() == compiler_sha
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
    observations = []
    for optimization in ("-O0", "-O1"):
        artifact = Path("/out/relay" + optimization + ".exe")
        built = subprocess.run([wine, str(compiler), "compile", "windows-x86_64", optimization, str(artifact)],
                               input=source.read_bytes(), capture_output=True, timeout=240)
        assert built.returncode == 0, built.stderr.decode(errors="replace")
        for data in (b"", b"\x00", b"\x01", b"\xff\x00"):
            with tempfile.TemporaryFile(buffering=0) as stream:
                stream.write(data)
                stream.seek(0)
                result = subprocess.run([wine, str(artifact)], stdin=stream, capture_output=True, timeout=120)
                consumed = stream.tell()
            assert result.returncode == 0 and result.stdout == bytes([((data[0] if data else 0) + 1) & 255])
            observations.append({"optimization": optimization, "input_hex": data.hex(), "output_hex": result.stdout.hex(),
                                 "stdin_file_offset": consumed, "binary_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()})
    Path("/out/public-build.json").write_text(json.dumps({"format": "PUBLIC-ONLY-BUILD-CHECK", "status": "PASS",
        "compiler_sha256": compiler_sha, "source_sha256": source_sha, "observations": observations,
        "private_cum_executables_mounted": False, "credentials_mounted": False, "originals_mounted": False,
        "tools": sorted(path.name for path in Path("/tools").iterdir())}))
