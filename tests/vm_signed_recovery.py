"""Guest-side fixture driver; the native BF planner chooses recovery operations."""
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import sys


def main():
    def tool(path):
        return {"executable": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}

    binding = json.loads(Path("/bindings/recovery.json").read_text())
    openssl, wine = tool("/usr/bin/openssl"), tool("/usr/lib/wine/wine64")
    for operand in ("1", "3"):
        binding["bindings"][operand]["openssl"] = openssl
    binding["planner_launcher"] = wine
    binding["planner_timeout_seconds"] = 120
    Path("/results/binding.json").write_text(json.dumps(binding))
    result = subprocess.run([sys.executable, "-I", "/runtime/runtime_entry.py", "flow",
                             "/results/binding.json", "--command", "1"], capture_output=True, timeout=240)
    sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)
    flow = json.loads(Path("/results/flow.json").read_text())
    assert flow["status"] == "PASS"
    rejections = []
    for name in ("release.sig", "capsule.cms", "extra"):
        root = Path("/results/reject-" + name)
        shutil.copytree("/clone", root / "clone")
        (root / "output").mkdir()
        path = root / "clone" / (name if name != "extra" else "unapproved")
        if name == "extra":
            path.write_bytes(b"extra")
        else:
            changed = bytearray(path.read_bytes())
            changed[-1] ^= 1
            path.chmod(0o600)
            path.write_bytes(changed)

        def relocate(value):
            if isinstance(value, dict):
                return {key: relocate(item) for key, item in value.items()}
            if isinstance(value, list):
                return [relocate(item) for item in value]
            if isinstance(value, str):
                for before, after in (("/clone", str(root / "clone")), ("/results", str(root / "output"))):
                    if value == before or value.startswith(before + "/"):
                        return after + value[len(before):]
            return value

        negative_binding = root / "binding.json"
        negative_binding.write_text(json.dumps(relocate(binding)))
        rejected = subprocess.run([sys.executable, "-I", "/runtime/runtime_entry.py", "flow",
                                  str(negative_binding), "--command", "1"], capture_output=True, timeout=120)
        assert rejected.returncode != 0 and not (root / "output/restored").exists()
        error = json.loads(rejected.stderr)
        assert error["status"] == "FAIL" and error["error"] == ("PROCESS_EXIT" if name == "release.sig" else "INTEGRITY")
        rejections.append({"mutation": name, "exit": rejected.returncode, "error": error["error"], "restored": False})
    Path("/results/checks.json").write_text(json.dumps({"rejections": rejections}))
    Path("/results/tools.json").write_text(json.dumps({"openssl": openssl, "wine": wine,
        "python": tool(str(Path(sys.executable).resolve())),
        "openssl_version": subprocess.check_output([openssl["executable"], "version"]).decode().strip(),
        "wine_version": subprocess.check_output([wine["executable"], "--version"]).decode().strip()}))


if __name__ == "__main__":
    main()
