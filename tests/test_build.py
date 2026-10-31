import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.build import build
from host.bytehost.errors import HostError
from host.bytehost.storage import digest, load


class BuildTests(unittest.TestCase):
    def test_report_binds_compiler_input_and_rejects_a_concurrent_source_edit(self):
        for changed in (False, True):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / "input.bf"
                original = b",+."
                source.write_bytes(original)
                spec = {"compiler": {"executable": sys.executable, "sha256": digest(sys.executable)},
                        "target": "windows-x86_64", "optimization": "-O1",
                        "output_directory": str(root / "build"), "sources": [str(source)],
                        "timeout_seconds": 1, "max_log_bytes": 4096, "report": str(root / "report.json")}
                def compiler(argv, *, stdin, **kwargs):
                    self.assertEqual(stdin, original)
                    Path(argv[-1]).write_bytes(b"synthetic native artifact")
                    if changed:
                        source.write_bytes(b",-.")
                    return {"wall_seconds": 0}
                with patch("host.bytehost.build.checked", side_effect=compiler):
                    if changed:
                        with self.assertRaises(HostError) as rejected:
                            build(spec)
                        self.assertEqual(rejected.exception.code, "CHANGED")
                        self.assertFalse(Path(spec["report"]).exists())
                    else:
                        build(spec)
                        record = load(spec["report"])["records"][0]
                        self.assertEqual(record["source_sha256"], hashlib.sha256(original).hexdigest())
                        self.assertEqual(record["artifact_sha256"], digest(root / "build/input.exe"))
