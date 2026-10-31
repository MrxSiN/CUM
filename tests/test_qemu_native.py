"""Opt-in isolated native compiler, worker boundary and finite behavior checks."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from host.bytehost.errors import HostError
from host.bytehost.process import isolated
from host.bytehost.storage import atomic_json, digest
from host.bytehost.worker import exchange

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("BYTEHOST_VM_TESTS") == "1" and os.environ.get("BYTEHOST_NATIVE_INTEGRATION") == "1",
                     "Real VM/native tools require explicit opt-in")
class QemuNativeTests(unittest.TestCase):
    def test_isolated_build_behavior_normalization_and_worker_boundary(self):
        vm = json.loads(Path(os.environ["BYTEHOST_VM_BINDING"]).read_text())
        native = Path(os.environ["BYTEHOST_NATIVE_DIRECTORY"])
        with tempfile.TemporaryDirectory(prefix="vm-native-") as temporary:
            root = Path(temporary)
            for name in ("tools", "checks", "bindings", "original", "protected", "reports", "returned"):
                (root / name).mkdir()
            for name in ("host", "tests"):
                shutil.copytree(ROOT / name, root / "checks" / name, ignore=shutil.ignore_patterns("__pycache__"))
            bbc = Path(os.environ["BYTEHOST_BBC_EXECUTABLE"])
            for name in ("bbc.exe", "xaxc.exe", "bbc-windows-x86_64.xax", "bbc-android-arm64.xax"):
                shutil.copyfile(bbc.parent / name, root / "tools" / name)
            workers = {}
            for name in ("echo", "fixed", "transform"):
                shutil.copyfile(native / (name + ".exe"), root / "tools" / (name + ".exe"))
                workers[name] = {"executable": "/tools/" + name + ".exe", "sha256": digest(native / (name + ".exe"))}
            fixtures = []
            for name, source in (("input.bf", b",+.[-]."), ("loop.bf", b"+++[.-]")):
                (root / "original" / name).write_bytes(source)
                protected, state, _ = exchange({"worker": {"executable": str(native / "transform.exe"),
                    "sha256": workers["transform"]["sha256"]}, "input_capacity_bytes": 4096,
                    "output_capacity_bytes": 65536, "timeout_seconds": 30}, source, b"\x02\x00")
                self.assertEqual(state, b"\x02\x00")
                (root / "protected" / name).write_bytes(protected)
                fixtures.append({"path": name, "input_hex": ["", "00", "01", "ff00"]})
            binding = {"compiler": {"executable": "/tools/bbc.exe", "sha256": digest(bbc)},
                       "original": "/original", "protected": "/protected", "fixtures": fixtures,
                       "compile_timeout_seconds": 180, "runtime_timeout_seconds": 60,
                       "max_log_bytes": 1048576, "max_runtime_output_bytes": 65536, "max_bfx_bytes": 16777216,
                       "reference_steps": 50000000, "workers": workers, "worker_input_capacity_bytes": 4096}
            binding['symbolic_analysis'] = {'verified_workspace_cells': 6, 'max_terms': 1024,
                                            'max_degree': 64, 'max_operations': 1000000}
            atomic_json(root / "bindings/check.json", binding)
            spec = {"backend": "qemu", "vm": vm, "image": "BYTEVM-IMAGE@sha256:" + vm["disk"]["sha256"],
                    "memory_bytes": 4294967296, "cpus": 2, "user": "1000:1000", "pids": 256,
                    "environment": {"HOME": "/reports", "WINEPREFIX": "/reports/wine", "WINEDEBUG": "-all"},
                    "argv": ["/usr/bin/python3.12", "/checks/tests/vm_native_check.py"], "workdir": "/checks",
                    "timeout_seconds": 1200, "max_output_bytes": 1048576,
                    "mounts": [{"source": str(root / name), "target": "/" + name, "readonly": name != "reports"}
                               for name in ("tools", "checks", "bindings", "original", "protected", "reports")],
                    "outputs": [{"guest": "/reports/" + name + ".json", "destination": str(root / "returned" / (name + ".json"))}
                                for name in ("behavior", "normalization", "boundary")]}
            try:
                result = isolated(spec)
            except HostError as error:
                self.fail(json.dumps(error.record()))
            records = {path.stem: json.loads(path.read_text()) for path in (root / "returned").iterdir()}
            self.assertEqual(records['behavior']['status'], 'PASS')
            self.assertEqual(records['boundary']['status'], 'PASS')
            self.assertEqual(records['normalization']['status'], 'FAIL')
            self.assertTrue(records['normalization']['same_io_projection'])
            if os.environ.get("BYTEHOST_VM_BUILD_EVIDENCE"):
                atomic_json(os.environ["BYTEHOST_VM_BUILD_EVIDENCE"], {
                    "format": "ISOLATED-NATIVE-FIXTURE-CHECKS", "status": "PASS", "reports": records,
                    "image_sha256": vm["disk"]["sha256"], "identity_mounts": [],
                    "network_interfaces": result["network_interfaces"], "uid": result["uid"],
                    "guest_wall_seconds": result["guest_wall_seconds"], "wall_seconds": result["wall_seconds"]})
