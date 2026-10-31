"""The OS bootstrap verifies the frozen tree before running bundled code."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from host.bytehost.storage import atomic_json, digest, inventory


@unittest.skipUnless(os.name == 'nt', 'Windows offline bootstrap')
class OfflineBootstrapTests(unittest.TestCase):
    def test_independent_pin_and_exact_tree_are_required(self):
        shell = Path(os.environ['SYSTEMROOT']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
        verifier = Path(__file__).resolve().parents[1] / 'host/verify_bundle.ps1'
        with tempfile.TemporaryDirectory(prefix='offline-bootstrap-') as temporary:
            base = Path(temporary)
            tree = base / 'tree'
            tree.mkdir()
            (tree / 'empty').mkdir()
            source = tree / 'binary'
            source.write_bytes(b'\x00\xff\r\n')
            manifest = base / 'inventory.json'
            atomic_json(manifest, inventory(tree))
            def verify(pin=None):
                return subprocess.run([str(shell), '-NoProfile', '-NonInteractive', '-File', str(verifier),
                    '-TreeRoot', str(tree), '-InventoryPath', str(manifest),
                    '-InventorySha256', pin or digest(manifest)], capture_output=True, timeout=30)
            baseline = verify()
            self.assertEqual(baseline.returncode, 0, baseline.stderr.decode(errors='replace'))
            self.assertNotEqual(verify('0' * 64).returncode, 0)
            source.write_bytes(b'\x00\xff\rX')
            self.assertNotEqual(verify().returncode, 0)
            source.write_bytes(b'\x00\xff\r\n')
            extra = tree / 'extra'
            extra.write_bytes(b'not inventoried')
            self.assertNotEqual(verify().returncode, 0)
            extra.unlink()
            source.unlink()
            self.assertNotEqual(verify().returncode, 0)
            for entry in ({'path': '../escape', 'type': 'directory', 'mode': 511},
                          {'path': 'e\u0301', 'type': 'directory', 'mode': 511},
                          {'path': 'empty', 'type': 'DIRECTORY', 'mode': 511}):
                atomic_json(manifest, {'format': 'BYTE-TREE-SHA256-NFC', 'excludes': [], 'entries': [entry]}, replace=True)
                self.assertNotEqual(verify().returncode, 0)


if __name__ == '__main__':
    unittest.main()
