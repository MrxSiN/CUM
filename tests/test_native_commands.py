"""Opt-in native parser and real generic app-to-BF routing regression."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from host.bytehost.process import run
from host.bytehost.storage import digest
from host.bytehost.transport import worker_input, worker_output


@unittest.skipUnless(os.environ.get("BYTEHOST_NATIVE_INTEGRATION") == "1", "Native commands require compiled BF workers")
class NativeCommandTests(unittest.TestCase):
    def test_exact_commands_modes_and_rejected_binary_suffixes(self):
        executable = Path(os.environ["BYTEHOST_NATIVE_DIRECTORY"]) / "command.exe"
        names = (b"doctor", b"toolchain inspect", b"prepare", b"verify", b"recover", b"test-recovery", b"benchmark", b"audit")
        for identity, name in enumerate(names, 1):
            result = run([str(executable)], stdin=worker_input(b"\x02\xff", name), timeout=30)
            self.assertEqual(result["exit"], 0)
            self.assertEqual(worker_output(result["stdout"]), (bytes([identity, 2]), b"\x02\xff"))
        for name in (b"", b"doctorrecover", b"test-doctor", b"toolchain", b"audit\x00", b"prepare" + b"x" * 256):
            result = run([str(executable)], stdin=worker_input(b"\x01\x00", name), timeout=30)
            self.assertNotEqual(result["stdout"][-1], 0)

    def test_app_routes_native_parser_result_to_native_snapshot_planner(self):
        native = Path(os.environ["BYTEHOST_NATIVE_DIRECTORY"])
        def tool(name):
            path = native / (name + ".exe")
            return {"executable": str(path), "sha256": digest(path)}
        with tempfile.TemporaryDirectory(prefix="native-command-route-") as temporary:
            root = Path(temporary)
            source = root / "input"
            source.mkdir()
            data = b"synthetic\x00\xff\r\n"
            (source / "file").write_bytes(data)
            # The generic host sees opaque command 2; snapshot.bf chooses Windows capture.
            spec = {"planner": tool("snapshot"), "planner_input_bytes": 2, "planner_timeout_seconds": 30,
                    "planner_output_bytes": 4096, "journal": str(root / "flow.json"),
                    "command_worker": {"worker": tool("command"), "input_capacity_bytes": 4096,
                                       "output_capacity_bytes": 4096, "timeout_seconds": 30},
                    "bindings": {"11": {"root": str(source), "paths": ["file"], "destination": str(root / "captured"),
                                        "manifest": str(root / "scope.json"), "max_entries": 10, "max_bytes": 4096}}}
            binding = root / "binding.json"
            binding.write_text(json.dumps(spec))
            result = run([sys.executable, "-m", "host.bytehost", "app", str(binding), "toolchain", "inspect"], timeout=30)
            self.assertEqual(result["exit"], 0, result["stderr"])
            self.assertEqual((root / "captured/file").read_bytes(), data)
            journal = json.loads((root / "flow.json").read_text())
            self.assertEqual(journal["request_hex"], "0201")
            self.assertEqual(journal["plan_hex"], "200b00")
