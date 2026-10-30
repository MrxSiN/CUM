"""Deferred real-tool tests, explicitly enabled with BYTEHOST_CRYPTO_TESTS=1.

Only disposable synthetic fixtures and temporary keys are used. Key generation
belongs to the established utility, never to a private homemade crypto scheme.
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from host.bytehost.crypto import authenticated_cms, envelope, sign, verify_signature
from host.bytehost.errors import HostError
from host.bytehost.process import checked
from host.bytehost.storage import digest


@unittest.skipUnless(os.environ.get("BYTEHOST_CRYPTO_TESTS") == "1", "NOT STARTED: explicit real-tool crypto test opt-in required")
class CryptoTests(unittest.TestCase):
    def setUp(self):
        executable = shutil.which("openssl")
        if not executable:
            self.skipTest("BLOCKED: OpenSSL unavailable")
        self.temp = tempfile.TemporaryDirectory(prefix="bytehost-disposable-crypto-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tool = {"executable": executable, "sha256": digest(executable)}
        self.common = {"openssl": self.tool, "timeout_seconds": 60, "max_log_bytes": 1048576,
                       "max_output_bytes": 1048576}
        self.source = self.root / "synthetic.bin"
        self.source.write_bytes(bytes(range(256)) + b"\x00fixture\r\n")
        for name in ("recipient", "wrong"):
            self.call("req", "-x509", "-newkey", "rsa:2048", "-noenc", "-days", "1",
                      "-subj", "/CN=DisposableByteHostTest", "-keyout", str(self.root / (name + ".key")),
                      "-out", str(self.root / (name + ".crt")))
        self.call("genpkey", "-algorithm", "ED25519", "-out", str(self.root / "signer.key"))
        self.call("pkey", "-in", str(self.root / "signer.key"), "-pubout", "-out", str(self.root / "signer.pub"))
        self.call("pkey", "-pubin", "-in", str(self.root / "signer.pub"), "-outform", "DER", "-out", str(self.root / "signer.der"))

    def call(self, *args):
        return checked([self.tool["executable"], *args], timeout=60, max_output=1048576)

    def encrypted(self):
        capsule = self.root / "capsule.cms"
        envelope(dict(self.common, source=str(self.source), destination=str(capsule),
                      recipients=[str(self.root / "recipient.crt")]))
        return capsule

    def decrypt_spec(self, capsule, name="recipient"):
        return dict(self.common, source=str(capsule), destination=str(self.root / "restored.bin"),
                    identity=str(self.root / (name + ".key")), certificate=str(self.root / (name + ".crt")))

    def test_exact_and_wrong_key(self):
        capsule = self.encrypted()
        authenticated_cms(capsule)
        with self.assertRaises(HostError):
            envelope(self.decrypt_spec(capsule, "wrong"), decrypt=True)
        self.assertFalse((self.root / "restored.bin").exists())
        envelope(self.decrypt_spec(capsule), decrypt=True)
        self.assertEqual((self.root / "restored.bin").read_bytes(), self.source.read_bytes())

    def test_corrupt_envelope(self):
        capsule = self.encrypted()
        changed = bytearray(capsule.read_bytes())
        changed[-1] ^= 1
        capsule.write_bytes(changed)
        with self.assertRaises(HostError):
            envelope(self.decrypt_spec(capsule), decrypt=True)
        self.assertFalse((self.root / "restored.bin").exists())

    def test_non_authenticated_format(self):
        path = self.root / "not-cms"
        path.write_bytes(b"\x30\x03\x02\x01\x00")
        with self.assertRaises(HostError):
            authenticated_cms(path)

    def test_signatures_and_independent_anchor(self):
        signature = self.root / "detached.sig"
        sign(dict(self.common, source=str(self.source), destination=str(signature), identity=str(self.root / "signer.key")))
        verify = dict(self.common, source=str(self.source), signature=str(signature),
                      public_key=str(self.root / "signer.pub"), trusted_spki_sha256=digest(self.root / "signer.der"))
        verify_signature(verify)
        with self.assertRaises(HostError):
            verify_signature(dict(verify, trusted_spki_sha256="0" * 64))
        self.source.write_bytes(b"modified")
        with self.assertRaises(HostError):
            verify_signature(verify)


if __name__ == "__main__":
    unittest.main()
