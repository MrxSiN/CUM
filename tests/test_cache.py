import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.cache import store, retrieve
from host.bytehost.errors import HostError
from host.bytehost.storage import canonical


class CacheTests(unittest.TestCase):
    def binding(self, root):
        source, key = root / "source", root / "key"
        source.write_bytes(b"synthetic cache bytes")
        key.write_bytes(bytes(range(32)))
        return {"root": str(root / "cache"), "identity": {"fixture": "retry"},
                "authentication_key": str(key), "source": str(source), "max_bytes": 100}

    def test_failed_stores_leave_no_visible_entry_and_allow_a_valid_retry(self):
        for failure in ("budget", "record"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                spec = self.binding(root)
                name = hashlib.sha256(canonical(spec["identity"])).hexdigest()
                committed = Path(spec["root"]) / name
                if failure == "budget":
                    with self.assertRaises(HostError):
                        store(dict(spec, max_bytes=1))
                else:
                    def interrupted(path, value):
                        self.assertFalse(committed.exists(), "An incomplete entry became visible")
                        raise OSError("Synthetic interrupted metadata write")
                    with patch("host.bytehost.cache.atomic_json", side_effect=interrupted):
                        with self.assertRaises(OSError):
                            store(spec)
                self.assertFalse(committed.exists())
                self.assertEqual(list(Path(spec["root"]).glob(".stage-*")), [])
                store(spec)
                restored = root / "restored"
                retrieve(dict(spec, destination=str(restored)))
                self.assertEqual(restored.read_bytes(), Path(spec["source"]).read_bytes())

    def test_existing_entry_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec = self.binding(root)
            original = Path(spec["source"]).read_bytes()
            store(spec)
            Path(spec["source"]).write_bytes(b"changed")
            with self.assertRaises(HostError) as rejected:
                store(spec)
            self.assertEqual(rejected.exception.code, "EXISTS")
            restored = root / "restored"
            retrieve(dict(spec, destination=str(restored)))
            self.assertEqual(restored.read_bytes(), original)
