"""Run the native BF recovery plan using tools inside the pinned guest image."""
import json
from pathlib import Path
import sys

sys.path.insert(0, "/runtime")
from host.bytehost.storage import digest, load, atomic_json
from host.bytehost.vm import flow
from host.bytehost.errors import HostError


if __name__ == "__main__":
    try:
        binding = load("/bindings/recovery.json")
        for number in ("1", "3"):
            binding["bindings"][number]["openssl"] = {"executable": "/usr/bin/openssl", "sha256": digest("/usr/bin/openssl")}
        binding["planner_launcher"] = {"executable": "/usr/lib/wine/wine64", "sha256": digest("/usr/lib/wine/wine64")}
        result = flow(binding, 1)
        assert result["status"] == "PASS"
        print(json.dumps({"status": "PASS", "plan_hex": result["plan_hex"]}))
    except HostError as error:
        sys.stderr.write(json.dumps(error.record()))
        raise SystemExit(1)
