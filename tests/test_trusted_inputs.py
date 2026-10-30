import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.storage import digest
from host.bytehost.trusted import invoke
from host.bytehost.process import run


class TrustedInputTests(unittest.TestCase):
    def test_observed_stdin_cursor_is_physical_and_binary_safe(self):
        result = run([sys.executable, "-I", "-c", "import os; os.read(0, 1)"], stdin=b"\x00x")
        self.assertEqual(result["exit"], 0)
        self.assertEqual(result["stdin_file_offset"], 1)

    def test_changed_reviewer_script_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / "review.py"
            script.write_text("print('review')")
            spec = {"tool": {"executable": sys.executable, "sha256": digest(sys.executable)},
                    "argv": [str(script)], "inputs_sha256": {str(script): digest(script)},
                    "timeout_seconds": 1, "max_output_bytes": 4096}
            result = {"stdout": b"", "stderr": b"", "exit": 0, "wall_seconds": 0, "resources": {}}
            with patch("host.bytehost.trusted.checked", return_value=result) as execute:
                self.assertEqual(invoke(spec)["inputs_sha256"], spec["inputs_sha256"])
                execute.assert_called_once()
            script.write_text("print('changed')")
            with patch("host.bytehost.trusted.checked") as execute:
                with self.assertRaises(HostError) as rejected:
                    invoke(spec)
                self.assertEqual(rejected.exception.code, "TOOL_IDENTITY")
                execute.assert_not_called()
