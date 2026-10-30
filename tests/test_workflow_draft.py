"""Deferred BF workflow checks; interpretation is never native evidence."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile

from host.bytehost.errors import HostError
from host.bytehost.storage import digest
from host.bytehost.vm import flow
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


def plan(name, request):
    result = execute((ROOT / "src" / name).read_bytes(), request, steps=100000000).output
    if not result or result[-1] or len(result) % 2 != 1:
        raise ValueError("BF refused plan")
    return list(zip(result[:-1:2], result[1:-1:2]))


class WorkflowDraftTests(unittest.TestCase):
    def test_prepare_clones_and_recovers_before_finalization(self):
        for mode in (1, 2):
            actual = plan("cum.bf", bytes([3, mode]))
            expected = [(11, 26), (12, 27), (13, 28), (14, 29), (15, 30),
                        (48, 64), (25, 65), (45, 66), (25, 67), (46, 68),
                        (25, 31), (46, 69), (25, 74), (44, 70), (19, 72), (7, 71), (8, 36)]
            start = actual.index(expected[0])
            self.assertEqual(actual[start:start + len(expected)], expected)
            self.assertLess(actual.index((14, 61)), actual.index((29, 10)))
            self.assertLess(actual.index((25, 73)), actual.index((14, 24)))
            self.assertLess(actual.index((47, 63)), start)
            self.assertEqual(actual[-2:], [(16, 38), (17, 39)])
            self.assertEqual((23, 40) in actual, mode == 1)
            self.assertIn((22, 70), actual)
            self.assertIn((22, 69), actual)

    def test_each_plan_operand_is_present(self):
        for name in ("public-job", "private-vault-job", "java-job", "kotlin-job", "xax-job"):
            job = json.loads((ROOT / "config" / (name + ".example.json")).read_text())
            for command in range(1, 9):
                for opcode, operand in plan("cum.bf", bytes([command, 1])):
                    if opcode != 22:
                        self.assertIn(str(operand), job["bindings"], (name, command, opcode))

    def test_clean_recovery_has_no_capture_or_transformation(self):
        self.assertEqual(plan("clean_recovery.bf", b"\x01\x01"),
                         [(14, 1), (15, 2), (6, 3), (7, 4), (4, 5), (12, 6)])
        publication = plan("maintenance.bf", b"\x04\x01")
        self.assertEqual(publication[-2:], [(46, 45), (25, 38)])
        backup = plan("maintenance.bf", b"\x01\x01")
        self.assertLess(backup.index((44, 44)), backup.index((13, 9)))

    def test_service_failure_never_reaches_finalize(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            executable = directory / "placeholder"
            executable.write_bytes(b"not native; process mocked")
            spec = {"planner": {"executable": str(executable), "sha256": digest(executable)},
                    "planner_input_bytes": 2, "planner_timeout_seconds": 1, "planner_output_bytes": 100,
                    "journal": str(directory / "flow.json"), "bindings": {"1": {}, "2": {}}}
            with patch("host.bytehost.vm.checked", return_value={"stdout": bytes([49, 1, 17, 2, 0])}), \
                 patch.dict("host.bytehost.vm.SERVICES", {49: lambda _: (_ for _ in ()).throw(HostError("INJECTED", "stop"))}), \
                 patch("host.bytehost.vm.publish_tree") as finalize:
                with self.assertRaises(HostError):
                    flow(spec, 3)
                finalize.assert_not_called()


if __name__ == "__main__":
    unittest.main()
