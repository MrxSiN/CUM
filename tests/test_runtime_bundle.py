"""Deferred digest-pinned offline-distribution bundling checks."""
import tempfile
import unittest
from pathlib import Path

from host.bytehost.bundle import bundle
from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, digest, inventory, verify_tree


class RuntimeBundleTests(unittest.TestCase):
    def test_complete_distribution_and_shared_libraries_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            distribution = base / "distribution"
            (distribution / "lib").mkdir(parents=True)
            (distribution / "empty").mkdir()
            (distribution / "lib/shared.so").write_bytes(b"synthetic library")
            (distribution / "interpreter").write_bytes(b"synthetic executable")
            manifest = base / "approved.json"
            atomic_json(manifest, inventory(distribution))
            spec = {"files": [], "trees": [{"source": str(distribution), "path": "python",
                    "manifest": str(manifest), "manifest_sha256": digest(manifest)}],
                    "destination": str(base / "bundle"), "manifest": str(base / "bundled.json"), "max_bytes": 1000}
            result = bundle(spec)
            verify_tree(spec["destination"], result)
            self.assertEqual((base / "bundle/python/lib/shared.so").read_bytes(), b"synthetic library")
            self.assertTrue((base / "bundle/python/empty").is_dir())
            (distribution / "unapproved").write_bytes(b"extra")
            spec.update(destination=str(base / "second"), manifest=str(base / "second.json"))
            with self.assertRaises(HostError):
                bundle(spec)
            self.assertFalse((base / "second").exists())


if __name__ == "__main__":
    unittest.main()
