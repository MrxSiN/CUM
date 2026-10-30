"""Independent build fixture executed inside the generic VM, without identities."""
from pathlib import Path
import sys

sys.path.insert(0, "/checks")
from host.bytehost.storage import digest, load
from tests.native_checks import verify
from host.bytehost.errors import HostError
import json


if __name__ == "__main__":
    spec = load("/bindings/check.json")
    spec["launcher"] = {"executable": "/usr/lib/wine/wine64", "sha256": digest("/usr/lib/wine/wine64")}
    try:
        for case in ("behavior", "normalization", "boundary"):
            spec["report"] = "/reports/" + case + ".json"
            verify(spec, case)
    except HostError as error:
        sys.stderr.write(json.dumps(error.record()))
        raise SystemExit(1)
