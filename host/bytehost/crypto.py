"""Established OpenSSL CMS authenticated envelopes and Ed25519 signatures.

No keys are generated implicitly. Signer public key DER hash is an independently
supplied trust anchor, never read as authority from the downloaded package.
"""
import hashlib
import os
import tempfile
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_bytes, digest, no_links
from .trusted import invoke


def authenticated_cms(path):
    """Require DER ContentInfo with RFC 5083 authEnvelopedData content type.

    This only checks container identity. OpenSSL performs all authenticated
    decryption and cryptographic validation. No ciphertext body is materialized.
    """
    with Path(path).open("rb") as source:
        require(source.read(1) == b"\x30", "CMS_FORMAT", "Expected DER ContentInfo")
        first = source.read(1)
        require(first, "CMS_FORMAT", "Truncated DER length")
        value = first[0]
        if value & 128:
            count = value & 127
            require(count > 0 and count <= Path(path).stat().st_size,
                    "CMS_FORMAT", "Indefinite or invalid DER length")
            encoded = source.read(count)
            require(len(encoded) == count and encoded[0] != 0, "CMS_FORMAT", "Noncanonical DER length")
            size = int.from_bytes(encoded, "big")
            require(size >= 128, "CMS_FORMAT", "Noncanonical long DER length")
        else:
            size = value
        require(source.tell() + size == Path(path).stat().st_size, "CMS_FORMAT", "DER length mismatch")
        require(source.read(13) == bytes.fromhex("060b2a864886f70d0109100117"),
                "CMS_FORMAT", "Authenticated CMS envelope required")


def _temporary_output(destination, operation):
    destination = Path(destination).absolute()
    no_links(destination.parent)
    require(not destination.exists(), "EXISTS", "Cryptographic output destination exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".pending-", dir=destination.parent)
    os.close(fd)
    try:
        operation(name)
        os.link(name, destination)
    finally:
        os.unlink(name)


def envelope(spec, decrypt=False):
    executable = pinned_executable(spec["openssl"])
    source = str(Path(spec["source"]).absolute())
    no_links(source)
    def operation(output):
        if decrypt:
            authenticated_cms(source)
            argv = [executable, "cms", "-decrypt", "-binary", "-inform", "DER",
                    "-in", source, "-inkey", spec["identity"], "-recip", spec["certificate"], "-out", output]
        else:
            require(spec["recipients"], "RECIPIENT", "At least one recipient certificate required")
            argv = [executable, "cms", "-encrypt", "-binary", "-aes-256-gcm",
                    "-outform", "DER", "-in", source, "-out", output]
            if "key_wrap_cipher" in spec:
                argv.extend(["-wrap", spec["key_wrap_cipher"]])
            if "recipient_kdf" in spec:
                for recipient in spec["recipients"]:
                    argv.extend(["-recip", recipient])
                    argv.extend(["-recip_kdf", spec["recipient_kdf"]])
            else:
                argv.extend(spec["recipients"])
        invoke({"tool": spec["openssl"], "argv": argv[1:],
                "inputs_sha256": spec.get("inputs_sha256", {}),
                "clear_environment_prefixes": spec.get("clear_environment_prefixes", []),
                "environment": spec.get("environment", {}),
                "timeout_seconds": spec["timeout_seconds"], "max_output_bytes": spec["max_log_bytes"]})
        if not decrypt:
            authenticated_cms(output)
        require(Path(output).stat().st_size <= spec["max_output_bytes"], "RESOURCE_BUDGET", "Cryptographic output exceeds budget")
    _temporary_output(spec["destination"], operation)


def _public_identity(executable, public_key, spec):
    result = checked([executable, "pkey", "-pubin", "-in", public_key, "-outform", "DER"],
                     timeout=spec["timeout_seconds"], max_output=spec["max_log_bytes"])
    require(len(result["stdout"]) == 44 and result["stdout"].startswith(bytes.fromhex("302a300506032b6570032100")),
            "SIGNER_FORMAT", "Ed25519 SubjectPublicKeyInfo required")
    actual = hashlib.sha256(result["stdout"]).hexdigest()
    require(actual == spec["trusted_spki_sha256"], "TRUST_ANCHOR", "Signing identity is not independently trusted")


def sign(spec):
    executable = pinned_executable(spec["openssl"])
    def operation(output):
        checked([executable, "pkeyutl", "-sign", "-rawin", "-inkey", spec["identity"],
                 "-in", spec["source"], "-out", output],
                timeout=spec["timeout_seconds"], max_output=spec["max_log_bytes"])
    _temporary_output(spec["destination"], operation)


def verify_signature(spec):
    executable = pinned_executable(spec["openssl"])
    _public_identity(executable, spec["public_key"], spec)
    checked([executable, "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", spec["public_key"],
             "-in", spec["source"], "-sigfile", spec["signature"]],
            timeout=spec["timeout_seconds"], max_output=spec["max_log_bytes"])
