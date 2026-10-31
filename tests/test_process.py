import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.process import run, to_file


class ProcessTreeTests(unittest.TestCase):
    def test_missing_executable_still_reports_a_launch_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(HostError) as rejected:
                run([str(Path(temporary) / "missing-executable")], timeout=1)
            self.assertEqual(rejected.exception.code, "PROCESS_START")

    def test_descendants_stop_on_timeout_output_rejection_and_parent_exit(self):
        for mode in ("run-timeout", "file-timeout", "run-output", "file-output", "exit"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                ready, marker = root / "ready", root / "survived"
                child = ("from pathlib import Path;import time;"
                         f"Path({str(ready)!r}).write_text('ready');time.sleep(1.5);"
                         f"Path({str(marker)!r}).write_text('survived')")
                parent = ("import subprocess,sys,time;from pathlib import Path;"
                          f"subprocess.Popen([sys.executable,'-I','-c',{child!r}]);"
                          f"ready=Path({str(ready)!r})\n"
                          "while not ready.exists(): time.sleep(0.01)\n")
                if "output" in mode:
                    parent += "sys.stdout.write('x'*4096);sys.stdout.flush();time.sleep(30)"
                elif "timeout" in mode:
                    parent += "time.sleep(30)"
                argv = [sys.executable, "-I", "-c", parent]
                startup_deadline = time.monotonic() + 30
                def clock():
                    if time.monotonic() >= startup_deadline:
                        raise AssertionError("The descendant did not start within the test guard")
                    # Exercise timeout after readiness, independently of emulator startup cost.
                    return 2.0 if "timeout" in mode and ready.exists() else 0.0
                with patch("host.bytehost.process.time.perf_counter", side_effect=clock):
                    if mode == "exit":
                        self.assertEqual(run(argv, timeout=1, max_output=32)["exit"], 0)
                    else:
                        with self.assertRaises(HostError) as rejected:
                            if mode.startswith("file"):
                                to_file(argv, root / "stdout", timeout=1, max_bytes=32)
                            else:
                                run(argv, timeout=1, max_output=32)
                        self.assertEqual(rejected.exception.code, "TIMEOUT" if "timeout" in mode else "OUTPUT_BUDGET")
                self.assertTrue(ready.exists(), "The descendant must actually have started")
                time.sleep(1.7)
                self.assertFalse(marker.exists(), "A descendant outlived its process operation")
