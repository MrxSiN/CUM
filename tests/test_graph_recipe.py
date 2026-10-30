"""Binary edit format tests; not a substitute for native edit/verify execution."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.assembly import assemble
from host.bytehost.errors import HostError
from host.bytehost.storage import digest
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


class GraphRecipeTests(unittest.TestCase):
    def test_four_guarded_mutations_are_assembled_by_bf(self):
        source = (ROOT / "src/graphs/add_negate.bf").read_bytes()
        recipe = execute(source, b"\x02\x01\x07").output
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            values = [b"R" * 32, b"F" * 32, b"\x00", b"\x00", b"\x00\x00\x01", b"T" * 32]
            buffers = {}
            for index, value in enumerate(values):
                path = base / str(index)
                path.write_bytes(value)
                buffers[str(index)] = str(path)
            worker = base / "placeholder-native-worker"
            worker.write_bytes(b"not executed")
            spec = {"worker": {"executable": str(worker), "sha256": digest(worker)},
                    "request_hex": "020107", "request_bytes": 3, "timeout_seconds": 60,
                    "max_recipe_bytes": 65536, "max_output_bytes": 65536,
                    "destination": str(base / "transaction.edit"), "buffers": buffers}
            with patch("host.bytehost.assembly.checked", return_value={"stdout": recipe}):
                assemble(spec)
            record = Path(spec["destination"]).read_bytes()
            self.assertTrue(record.startswith(b"XAXEDIT1" + values[0] + b"\x04"))
            self.assertTrue(record.endswith(b"\x02\x01\x00"))
            self.assertEqual(record.count(values[1]), 4)

    def test_non_add_operation_is_refused(self):
        source = (ROOT / "src/graphs/add_negate.bf").read_bytes()
        for operation in (0, 2, 3, 62, 255):
            self.assertNotEqual(execute(source, bytes([2, operation, 7])).output[-1], 0)


if __name__ == "__main__":
    unittest.main()
