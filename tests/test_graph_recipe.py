"""Binary edit format tests; not a substitute for native edit/verify execution."""
import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.assembly import assemble
from host.bytehost.errors import HostError
from host.bytehost.storage import digest
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


class GraphRecipeTests(unittest.TestCase):
    def test_each_stage_assembles_one_guarded_mutation(self):
        source = (ROOT / "src/graphs/add_negate.bf").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            values = [b"R" * 32, b"F" * 32, b"\x00", b"\x02", b"\x00\x00\x01", b"T" * 32, b"\x00", b"\x01"]
            buffers = {}
            for index, value in enumerate(values):
                path = base / str(index)
                path.write_bytes(value)
                buffers[str(index)] = str(path)
            worker = base / "placeholder-native-worker"
            worker.write_bytes(b"not executed")
            for stage in range(4):
                request = bytes([2, 2 if stage == 3 else 1, 7, stage])
                recipe = execute(source, request).output
                spec = {"worker": {"executable": str(worker), "sha256": digest(worker)},
                        "request_hex": request.hex(), "request_bytes": 4, "timeout_seconds": 60,
                        "max_recipe_bytes": 65536, "max_output_bytes": 65536,
                        "destination": str(base / (str(stage) + ".edit")), "buffers": buffers}
                with patch("host.bytehost.assembly.checked", return_value={"stdout": recipe}):
                    assemble(spec)
                record = Path(spec["destination"]).read_bytes()
                self.assertTrue(record.startswith(b"XAXEDIT1" + values[0] + b"\x01"))
                self.assertEqual(record.count(values[1]), 1)
                self.assertEqual(record[41], (6, 6, 1, 4)[stage])

    def test_non_add_operation_is_refused(self):
        source = (ROOT / "src/graphs/add_negate.bf").read_bytes()
        for stage in range(4):
            for operation in (0, 1, 2, 3, 62, 255):
                if operation != (2 if stage == 3 else 1):
                    self.assertNotEqual(execute(source, bytes([2, operation, 7, stage])).output[-1], 0)

    def test_flow_queries_and_verifies_all_steps_before_replacement(self):
        result = execute((ROOT / "src/graphs/flow.bf").read_bytes(), b"\x01\x01").output
        self.assertEqual(result[-1], 0)
        pairs = list(zip(result[:-1:2], result[1:-1:2]))
        expected = []
        for stage in range(4):
            ids = (1, 2, 3, 4) if stage == 0 else tuple(range(11 + (stage - 1) * 4, 15 + (stage - 1) * 4))
            expected.extend(zip((10, 27, 10, 10), ids))
        self.assertEqual(pairs[:16], expected)
        self.assertEqual(pairs[16:18], [(30, 5), (31, 6)])

    def test_all_graph_workflow_templates_supply_every_operand(self):
        result = execute((ROOT / "src/graphs/flow.bf").read_bytes(), b"\x01\x01").output
        operands = [str(value) for value in result[1:-1:2]]
        checked = []
        def inspect(value):
            if isinstance(value, dict):
                planner = value.get("planner")
                if isinstance(planner, dict) and planner.get("executable", "").endswith("/flow.exe"):
                    self.assertTrue(set(operands) <= set(value["bindings"]))
                    for index in (2, 12, 16, 20):
                        self.assertEqual(value["bindings"][str(index)]["request_bytes"], 4)
                    checked.append(value)
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        for path in (ROOT / "config").glob("*.json"):
            inspect(json.loads(path.read_text()))
        self.assertGreaterEqual(len(checked), 7)


if __name__ == "__main__":
    unittest.main()
