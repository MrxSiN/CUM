"""Independent generic-host fault/continuation tests, using BF as the worker.

Process mocking here avoids claiming native execution. Mocked output is produced
by interpreting the actual BF source, never by a foreign-language camouflage pass.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.storage import digest, load
from host.bytehost.worker import map_file
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


class HostTests(unittest.TestCase):
    def setup_spec(self, temp, worker):
        root = Path(temp)
        source = root / "input"
        source.write_bytes(b"+++[.-]\x00,[-].")
        key = root / "state.key"
        key.write_bytes(bytes(range(32)))
        artifact = root / "worker-native-placeholder"
        artifact.write_bytes(b"test-only; never launched")
        return {"source": str(source), "destination": str(root / "output"),
                "journal": str(root / "checkpoint.json"), "state_key": str(key),
                "worker": {"executable": str(artifact), "sha256": digest(artifact)},
                "input_capacity_bytes": 65536, "output_capacity_bytes": 65536,
                "record_payload_bytes": 3, "initial_state_hex": "0200",
                "timeout_seconds": 60, "max_output_bytes": 1048576}, worker

    def runner(self, source, fail_after=None):
        calls = [0]
        def run(argv, *, stdin, **kwargs):
            calls[0] += 1
            if fail_after is not None and calls[0] > fail_after:
                raise HostError("INJECTED", "Synthetic interruption")
            return {"stdout": execute(source, stdin).output, "stderr": b"", "exit": 0, "wall_seconds": 0.0}
        return run

    def test_fixed_worker_host_does_not_transform(self):
        fixed = (ROOT / "tests/workers/fixed.bf").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            spec, _ = self.setup_spec(temp, fixed)
            with patch("host.bytehost.worker.checked", side_effect=self.runner(fixed)):
                result = map_file(spec)
            self.assertEqual(Path(spec["destination"]).read_bytes(), b"FIXED" * result["records"])

    def test_interruption_resume_and_uncommitted_tail(self):
        worker = (ROOT / "src/transform.bf").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            spec, _ = self.setup_spec(temp, worker)
            with patch("host.bytehost.worker.checked", side_effect=self.runner(worker, fail_after=2)):
                with self.assertRaises(HostError):
                    map_file(spec)
            partial = Path(spec["destination"] + ".partial")
            with partial.open("ab") as target:
                target.write(b"uncommitted tail")
            with patch("host.bytehost.worker.checked", side_effect=self.runner(worker)):
                map_file(spec)
            source = Path(spec["source"]).read_bytes()
            from host.bytehost.transport import worker_input, worker_output
            expected = worker_output(execute(worker, worker_input(b"\x02\x00", source)).output)[0]
            self.assertEqual(Path(spec["destination"]).read_bytes(), expected)
            self.assertTrue(load(spec["journal"])["body"]["complete"])

    def test_changed_input_cannot_resume(self):
        worker = (ROOT / "src/echo.bf").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            spec, _ = self.setup_spec(temp, worker)
            with patch("host.bytehost.worker.checked", side_effect=self.runner(worker, fail_after=1)):
                with self.assertRaises(HostError):
                    map_file(spec)
            Path(spec["source"]).write_bytes(b"different")
            with self.assertRaises(HostError):
                map_file(spec)


if __name__ == "__main__":
    unittest.main()
