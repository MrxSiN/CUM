"""Deferred native BF machine/host compliance and continuation checks.

Run in the provisioned isolated check environment. The fixed worker and real
worker use the identical generic production host. No native result is inferred
from the reference interpreter.
"""
import argparse
import os
import tempfile
from pathlib import Path

from host.bytehost.errors import require
from host.bytehost.machine import transduce
from host.bytehost.storage import atomic_json, load
from tests.reference import execute


def verify(spec):
    observations = []
    with tempfile.TemporaryDirectory(prefix="native-byte-machine-check-") as temporary:
        root = Path(temporary)
        key = root / "synthetic-state-key"
        key.write_bytes(os.urandom(32))
        source = root / "input.bf"
        source.write_bytes(b"+++[>++<-]>.,.\x00")
        for label in ("fixed", "real"):
            binding = dict(spec[label], source=str(source), destination=str(root / (label + ".bf")),
                           journal=str(root / (label + ".state.json")), state_key=str(key))
            result = transduce(binding)
            output = Path(binding["destination"]).read_bytes()
            if label == "fixed":
                require(output == b"FIXED" * (source.stat().st_size + 2), "HOST_BOUNDARY", "Host transformed without real BF decisions")
            else:
                for data in (b"", b"\x00", b"\x01\xff"):
                    require(execute(source.read_bytes(), data).output == execute(output, data).output,
                            "SEMANTICS", "Native BF producer's output differs from independent semantics")
            require(result["events"] == source.stat().st_size + 2, "CONTINUATION", "Per-event native state handoff was incomplete")
            observations.append({"worker": label, **result})
    atomic_json(spec["report"], {"format": "NATIVE-MACHINE-BOUNDARY-CHECK", "status": "PASS",
                "environment": spec["environment"], "observations": observations,
                "scope": "native BF components through real generic host; protected source evaluated independently"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binding")
    arguments = parser.parse_args()
    verify(load(arguments.binding))
