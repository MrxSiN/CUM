import io
import os
import stat
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.archive import extract, pack
from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, inventory, relative_name, verify_tree, new_stage, remove_stage
from host.bytehost.worker import seal, unseal


class StorageTests(unittest.TestCase):
    def test_windows_paths_and_collisions(self):
        for name in ("../x", "/x", "C:/x", "a\\b", "NUL", "a/CON.txt", "x.", "x ", "a//b", "a/./b", ".git/config", "a:b"):
            with self.assertRaises(HostError):
                relative_name(name)

    def test_inventory_and_mutations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "empty").mkdir()
            (root / "file").write_bytes(bytes(range(256)))
            record = inventory(root)
            verify_tree(root, record)
            (root / "extra").write_bytes(b"")
            with self.assertRaises(HostError):
                verify_tree(root, record)
            (root / "extra").unlink()
            (root / "file").write_bytes(b"changed")
            with self.assertRaises(HostError):
                verify_tree(root, record)

    def test_archive_exact_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "original"
            source.mkdir()
            (source / "empty").mkdir()
            (source / "binary").write_bytes(bytes(range(256)))
            (source / "source.bf").write_bytes(b"+++[.-]\r\n")
            manifest = base / "scope.json"
            atomic_json(manifest, inventory(source))
            capsule = base / "snapshot.tar"
            pack({"root": str(source), "manifest": str(manifest), "destination": str(capsule),
                  "max_archive_bytes": 1048576})
            restored = base / "restored"
            extract({"source": str(capsule), "destination": str(restored),
                     "limits": {"bytes": 1048576, "entries": 100, "metadata_bytes": 65536}})
            self.assertEqual(inventory(source), inventory(restored))

    def test_unsafe_tar_rejected_without_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            capsule = base / "unsafe.tar"
            with tarfile.open(capsule, "w") as archive:
                entry = tarfile.TarInfo("../escaped")
                entry.size = 1
                archive.addfile(entry, io.BytesIO(b"x"))
            with self.assertRaises(HostError):
                extract({"source": str(capsule), "destination": str(base / "restored"),
                         "limits": {"bytes": 1048576, "entries": 100, "metadata_bytes": 65536}})
            self.assertFalse((base / "escaped").exists())

    def test_failed_restore_removes_readonly_plaintext_and_retains_budget_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            source.mkdir()
            readonly = source / "a-readonly"
            readonly.write_bytes(b"synthetic plaintext")
            os.chmod(readonly, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            try:
                (source / "b-next").write_bytes(b"x")
                manifest, capsule = root / "scope.json", root / "snapshot.tar"
                atomic_json(manifest, inventory(source))
                pack({"root": str(source), "manifest": str(manifest), "destination": str(capsule),
                      "max_archive_bytes": 1048576})
                with self.assertRaises(HostError) as rejected:
                    extract({"source": str(capsule), "destination": str(root / "restored"),
                             "limits": {"bytes": 1048576, "entries": 1, "metadata_bytes": 65536}})
                self.assertEqual(rejected.exception.code, "RESOURCE_BUDGET")
                self.assertEqual(list(root.glob(".stage-*")), [])
                self.assertFalse((root / "restored").exists())
            finally:
                os.chmod(readonly, stat.S_IRUSR | stat.S_IWUSR)

    def test_cleanup_can_remove_restrictive_stage_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            stage = new_stage(root / "result")
            directory = stage / "nested"
            directory.mkdir()
            (directory / "file").write_bytes(b"synthetic")
            os.chmod(directory, 0)
            os.chmod(stage, 0)
            self.assertTrue(stage.absolute().is_relative_to(root))
            remove_stage(stage)
            self.assertFalse(stage.exists())

    def test_cleanup_failure_preserves_original_error_and_identifies_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            stage = new_stage(root / "result")
            self.assertTrue(stage.resolve().is_relative_to(root))
            original = HostError("INTEGRITY", "Synthetic restore rejection")
            with self.assertRaises(HostError) as rejected:
                try:
                    raise original
                finally:
                    with patch("host.bytehost.storage.shutil.rmtree", side_effect=OSError("Synthetic locked file")):
                        remove_stage(stage)
            self.assertIs(rejected.exception, original)
            self.assertIn(str(stage), " ".join(rejected.exception.__notes__))
            self.assertEqual(rejected.exception.record()["details"]["cleanup_failure"]["stage"], str(stage))

    def test_authenticated_state(self):
        key = bytes(range(32))
        body = {"operation": "opaque", "sequence": "12345678901234567890", "state": "00ff"}
        signed = seal(body, key)
        self.assertEqual(unseal(signed, key), body)
        for wrong in (bytes(32), key[::-1]):
            with self.assertRaises(HostError):
                unseal(signed, wrong)
        signed["body"]["sequence"] = "1"
        with self.assertRaises(HostError):
            unseal(signed, key)


if __name__ == "__main__":
    unittest.main()
