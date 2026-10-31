import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.machine import transduce
from host.bytehost.storage import digest


class MachineDeadlineTests(unittest.TestCase):
    def test_remaining_deadline_bounds_handoffs_and_final_publication(self):
        for duration, handoff in ((0.2, False), (0.6, False), (0.4, True)):
            with self.subTest(duration=duration, handoff=handoff), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source, key = root / "input", root / "key"
                source.write_bytes(b"")
                key.write_bytes(bytes(range(32)))
                worker = {"executable": sys.executable, "sha256": digest(sys.executable)}
                spec = {"source": str(source), "destination": str(root / "output"),
                        "journal": str(root / "state"), "state_key": str(key), "worker": worker,
                        "integer_limit": None, "profile": 2, "selector": 0, "max_output_bytes": 100,
                        "max_storage_bytes": 100, "max_stack_entries": 100, "max_handoffs_per_event": 1,
                        "kernels": {"1": worker}, "max_operation_seconds": 1, "timeout_seconds": 60,
                        "max_response_bytes": 100, "checkpoint_events": 1}
                clock, timeouts = [0.0], []
                def invoke(*args, **kwargs):
                    timeouts.append((clock[0], kwargs["timeout"]))
                    clock[0] += duration
                    effects = bytes([11, 1]) if handoff and len(timeouts) == 2 else b""
                    return {"stdout": bytes([178]) + effects + bytes(17),
                            "wall_seconds": duration, "resources": {"status": "BLOCKED"}}
                with patch("host.bytehost.machine.time.perf_counter", side_effect=lambda: clock[0]), \
                     patch("host.bytehost.machine.checked", side_effect=invoke):
                    if duration == 0.2:
                        result = transduce(spec)
                        self.assertAlmostEqual(result["wall_seconds"], 0.4)
                        self.assertTrue(Path(spec["destination"]).exists())
                    else:
                        with self.assertRaises(HostError) as rejected:
                            transduce(spec)
                        self.assertEqual(rejected.exception.code, "RESOURCE_BUDGET")
                        self.assertFalse(Path(spec["destination"]).exists())
                for elapsed, timeout in timeouts:
                    self.assertGreater(timeout, 0)
                    self.assertLessEqual(timeout, 1 - elapsed)
                self.assertEqual(len(timeouts), 3 if handoff else 2)
