"""Cold package checks for an already authenticated, independently trusted bundle.

Use a separate trusted recovery image. No original project/development directories
or installed private CUM modules may be available to this check.
"""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


def verify(spec):
    package = Path(spec["package"])
    environment = {key: value for key, value in os.environ.items() if key not in
                   ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE")}
    def run(command, data=b"", launcher=None):
        prefix = [str(package / launcher)] if launcher else []
        result = subprocess.run([*prefix, *command], input=data, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=package, env=environment,
                                timeout=spec["timeout_seconds"], check=False)
        if result.returncode:
            raise RuntimeError("Packaged runtime failed: " + result.stderr.decode("utf-8", "replace"))
        return result.stdout
    for relative, expected in spec["required_sha256"].items():
        actual = hashlib.sha256((package / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError("Packaged file differs from independently approved identity")
    run([str(package / spec["python"]), "-I", str(package / "runtime_entry.py"), "--help"])
    actual = run([str(package / spec["planner"])], bytes.fromhex(spec["planner_request_hex"]),
                 spec.get("planner_launcher"))
    if actual != bytes.fromhex(spec["planner_response_hex"]):
        raise RuntimeError("Packaged BF planner did not emit its expected recovery plan")
    run([str(package / spec["openssl"]), "version"])
    report = {"format": "COLD-RUNTIME-CHECK", "status": "PASS",
              "scope": "packaged interpreter/modules/native BF planner/OpenSSL; full signed recovery is a separate BF flow"}
    if spec.get("report"):
        target = Path(spec["report"])
        with target.open("x", encoding="utf-8") as output:
            json.dump(report, output, sort_keys=True)
            output.write("\n")
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binding")
    arguments = parser.parse_args()
    verify(json.loads(Path(arguments.binding).read_text(encoding="utf-8")))
