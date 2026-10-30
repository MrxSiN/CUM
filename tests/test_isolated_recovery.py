"""Draft generic capability-policy boundary tests. No container execution."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, digest, inventory
from host.bytehost.trusted_recovery import trusted_isolated
from host.bytehost.machine import _request


class IsolatedRecoveryTests(unittest.TestCase):
    def binding(self, directory):
        root = Path(directory)
        source, output = root / "release", root / "output"
        source.mkdir()
        (source / "release.json").write_bytes(b"synthetic")
        spec = {"image": "synthetic@sha256:pin", "argv": ["/runtime/entry"], "environment": {},
                "workdir": "/runtime", "forbidden_sources": [str(root / "original")],
                "mounts": [{"source": str(source), "target": "/release", "readonly": True},
                           {"source": str(output), "target": "/result", "readonly": False}]}
        policy = {"format": "PINNED-ISOLATED-CAPABILITIES",
                  **{key: spec[key] for key in ("image", "argv", "environment", "workdir")},
                  "mounts": {mount["target"]: dict(mount) for mount in spec["mounts"]}}
        policy["mounts"]["/release"]["inventory"] = inventory(source)
        path = root / "policy.json"
        atomic_json(path, policy)
        spec.update(policy_file=str(path), policy_sha256=digest(path))
        return spec

    def test_only_exact_independent_inputs_reach_isolation(self):
        with tempfile.TemporaryDirectory() as temporary:
            spec = self.binding(temporary)
            with patch("host.bytehost.trusted_recovery.isolated", return_value={"exit": 0}) as execute:
                trusted_isolated(spec)
                execute.assert_called_once_with(spec)

    def test_missing_changed_or_duplicate_capability_rejected(self):
        for mutation in ("missing", "duplicate", "argv", "environment", "readonly", "source", "pin", "bytes", "forbidden"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                spec = self.binding(temporary)
                if mutation == "missing": spec["mounts"].pop()
                elif mutation == "duplicate": spec["mounts"].append(copy.deepcopy(spec["mounts"][0]))
                elif mutation == "argv": spec["argv"] = ["/project/build"]
                elif mutation == "environment": spec["environment"]["PYTHONPATH"] = "/project"
                elif mutation == "readonly": spec["mounts"][0]["readonly"] = False
                elif mutation == "source": spec["mounts"][0]["source"] = str(Path(temporary) / "original")
                elif mutation == "pin": spec["policy_sha256"] = "0" * 64
                elif mutation == "bytes": (Path(temporary) / "release/release.json").write_bytes(b"changed")
                elif mutation == "forbidden": spec["forbidden_sources"] = [temporary]
                with patch("host.bytehost.trusted_recovery.isolated") as execute:
                    with self.assertRaises(HostError):
                        trusted_isolated(spec)
                    execute.assert_not_called()

    def test_integer_storage_has_no_inherited_compiler_ceiling(self):
        state = {"integers": [str(2 ** 128)], "stacks": [[]], "opaque": "00" * 16}
        spec = {"integer_limit": None, "profile": 2, "selector": 0}
        self.assertEqual(_request(1, 0, spec, state)[9], 0)
        spec["integer_limit"] = 4
        self.assertEqual(_request(1, 0, spec, state)[9], 1)
        spec["integer_limit"] = -1
        with self.assertRaises(HostError):
            _request(1, 0, spec, state)


if __name__ == "__main__":
    unittest.main()
