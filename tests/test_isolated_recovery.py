"""Draft generic capability-policy boundary tests. No container execution."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, digest, inventory
from host.bytehost.trusted_recovery import trusted_isolated
from host.bytehost.machine import _request


class IsolatedRecoveryTests(unittest.TestCase):
    def test_retained_entry_preserves_structured_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary) / "runtime"
            runtime.mkdir()
            shutil.copytree("host", runtime / "host", ignore=shutil.ignore_patterns("__pycache__", "runtime_entry.py"))
            shutil.copyfile("host/runtime_entry.py", runtime / "runtime_entry.py")
            result = subprocess.run([sys.executable, "-I", str(runtime / "runtime_entry.py"),
                                     "flow", str(Path(temporary) / "missing.json"), "--command", "1"], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["status"], "FAIL")
            self.assertEqual(result.stdout, b"")

    def binding(self, directory):
        root = Path(directory)
        source, output = root / "release", root / "output"
        source.mkdir()
        (source / "release.json").write_bytes(b"synthetic")
        spec = {"image": "synthetic@sha256:pin", "argv": ["/runtime/entry"], "environment": {},
                "engine": {"executable": sys.executable, "sha256": digest(sys.executable)},
                "workdir": "/runtime", "forbidden_sources": [str(root / "original")],
                "mounts": [{"source": str(source), "target": "/release", "readonly": True},
                           {"source": str(output), "target": "/result", "readonly": False}]}
        policy = {"format": "PINNED-ISOLATED-CAPABILITIES",
                  **{key: spec[key] for key in ("image", "argv", "environment", "workdir", "engine")},
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

    def test_signed_policy_authenticates_the_actual_policy_before_capabilities(self):
        with tempfile.TemporaryDirectory() as temporary:
            spec = self.binding(temporary)
            spec.pop("policy_sha256")
            spec["policy_signature"] = {"source": "unrelated-file", "public_key": "independent-anchor"}
            with patch("host.bytehost.trusted_recovery.verify_signature") as verify, \
                 patch("host.bytehost.trusted_recovery.isolated", return_value={"exit": 0}) as execute:
                trusted_isolated(spec)
                self.assertEqual(verify.call_args.args[0]["source"], spec["policy_file"])
                execute.assert_called_once()
            spec["policy_sha256"] = "0" * 64
            with self.assertRaises(HostError):
                trusted_isolated(spec)

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

    def test_docker_engine_requires_an_independent_policy_pin(self):
        for mutation in (None, "executable", "sha256", "missing_policy_pin", "missing_engine"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                spec = self.binding(temporary)
                if mutation in ("executable", "sha256"):
                    spec["engine"][mutation] = "unapproved"
                elif mutation == "missing_policy_pin":
                    path = Path(spec["policy_file"])
                    policy = json.loads(path.read_text())
                    policy.pop("engine")
                    atomic_json(path, policy, replace=True)
                    spec["policy_sha256"] = digest(path)
                elif mutation == "missing_engine":
                    spec.pop("engine")
                with patch("host.bytehost.trusted_recovery.isolated", return_value={"exit": 0}) as execute:
                    if mutation is None:
                        trusted_isolated(spec)
                        execute.assert_called_once()
                    else:
                        with self.assertRaises(HostError) as rejected:
                            trusted_isolated(spec)
                        self.assertEqual(rejected.exception.code, "ISOLATION")
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

    def test_vm_backend_image_and_outputs_are_independently_pinned(self):
        for mutation in (None, "backend", "vm", "outputs"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                spec = self.binding(temporary)
                path = Path(spec["policy_file"])
                policy = json.loads(path.read_text())
                additions = {"backend": "qemu", "vm": {"disk": {"sha256": "synthetic"}},
                             "outputs": [{"guest": "/result/archive", "destination": str(Path(temporary) / "returned")}]}
                spec.update(copy.deepcopy(additions))
                policy.update(additions)
                atomic_json(path, policy, replace=True)
                spec["policy_sha256"] = digest(path)
                if mutation == "backend": spec["backend"] = "docker"
                elif mutation == "vm": spec["vm"]["disk"]["sha256"] = "changed"
                elif mutation == "outputs": spec["outputs"][0]["destination"] += "-changed"
                with patch("host.bytehost.trusted_recovery.isolated", return_value={"exit": 0}) as execute:
                    if mutation is None:
                        trusted_isolated(spec)
                        execute.assert_called_once()
                    else:
                        with self.assertRaises(HostError):
                            trusted_isolated(spec)
                        execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
