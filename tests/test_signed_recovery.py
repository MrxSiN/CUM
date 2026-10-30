"""Opt-in native Windows signed-clone recovery integration using synthetic data.

Original trees are removed before a separate recovery process starts. This is
not a sandbox, a production release, or a complete offline runtime backup drill.
"""
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

from host.bytehost import archive, crypto, git_transport
from host.bytehost.bundle import bundle
from host.bytehost.metadata import directory_blob
from host.bytehost.process import checked, run
from host.bytehost.scope import capture_directory
from host.bytehost.storage import atomic_json, digest, inventory, verify_tree
from host.bytehost.vm import compose_record, write_inventory
from host.bytehost.worker import map_file
from tests import test_crypto

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt" and os.environ.get("BYTEHOST_NATIVE_INTEGRATION") == "1",
                     "Native signed recovery requires explicit Windows/tool opt-in")
class SignedRecoveryTests(unittest.TestCase):
    def test_signed_clone_restores_scope_and_rejects_tampering(self):
        fixture = test_crypto.CryptoTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        base = fixture.root
        native = Path(os.environ["BYTEHOST_NATIVE_DIRECTORY"])

        def worker(name):
            path = native / (name + ".exe")
            return {"executable": str(path), "sha256": digest(path)}

        original = base / "original"
        original.mkdir()
        (original / "main.bf").write_bytes(b"+++[.-]\r\n")
        (original / "data.bin").write_bytes(bytes(range(256)))
        (original / "empty").mkdir()
        snapshot, scope = base / "snapshot", base / "scope.json"
        expected = capture_directory({"root": str(original), "paths": ["main.bf", "data.bin", "empty"],
                    "destination": str(snapshot), "manifest": str(scope), "max_bytes": 1048576, "max_entries": 100})
        (original / "main.bf").write_bytes(b"changed after capture")
        plaintext, capsule = base / "originals.tar", base / "capsule.cms"
        archive.pack({"root": str(snapshot), "manifest": str(scope), "destination": str(plaintext), "max_archive_bytes": 1048576})
        crypto.envelope(dict(fixture.common, source=str(plaintext), destination=str(capsule),
                             recipients=[str(base / "recipient.crt")]))
        internal = base / "internal.tar"
        crypto.envelope(dict(fixture.common, source=str(capsule), destination=str(internal),
                             identity=str(base / "recipient.key"), certificate=str(base / "recipient.crt")), decrypt=True)
        limits = {"bytes": 1048576, "entries": 100, "metadata_bytes": 65536}
        archive.extract({"source": str(internal), "destination": str(base / "internal"), "limits": limits})
        verify_tree(base / "internal", expected)

        release = base / "release"
        release.mkdir()
        (release / "empty").mkdir()
        state_key = base / "state.key"
        state_key.write_bytes(os.urandom(32))
        map_file({"source": str(snapshot / "main.bf"), "destination": str(release / "main.bf"),
                  "worker": worker("transform"), "journal": str(base / "mapping.json"), "state_key": str(state_key),
                  "input_capacity_bytes": 4096, "output_capacity_bytes": 65536, "record_payload_bytes": 3,
                  "initial_state_hex": "0200", "timeout_seconds": 30, "max_output_bytes": 1048576})
        shutil.copyfile(snapshot / "data.bin", release / "data.bin")
        shutil.copyfile(capsule, release / "capsule.cms")
        directory_blob({"root": str(release), "worker": worker("git_attributes"), "timeout_seconds": 30,
                        "max_response_bytes": 4096, "max_file_bytes": 1048576, "executable_paths": []})
        write_inventory({"root": str(release), "destination": str(release / "inventory.json"), "public": True,
                         "excludes": ["inventory.json", "release.json", "release.sig", "capsule.cms"]})
        fields = {"format": "SIGNED-PROTECTED-TREE-CMS", "release_identity": "synthetic-integration",
                  "recovery_mode": "public-capsule"}
        compose_record({"destination": str(release / "release.json"), "fields": fields,
                        "files": {"protected_inventory": str(release / "inventory.json"), "recovery_capsule": str(release / "capsule.cms")}})
        crypto.sign(dict(fixture.common, source=str(release / "release.json"), destination=str(release / "release.sig"),
                         identity=str(base / "signer.key")))

        git = shutil.which("git")
        self.assertIsNotNone(git)
        hooks, scratch, template = (base / name for name in ("hooks", "scratch", "template"))
        for path in (hooks, scratch, template):
            path.mkdir()
        environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
        environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                           GIT_AUTHOR_NAME="Synthetic", GIT_AUTHOR_EMAIL="test@example.invalid",
                           GIT_COMMITTER_NAME="Synthetic", GIT_COMMITTER_EMAIL="test@example.invalid")

        def git_call(*arguments):
            return checked([git, "-c", "core.hooksPath=" + str(hooks), "-C", str(release), *arguments],
                           env=environment, timeout=30, max_output=1048576)

        git_call("init", "--template=" + str(template), "-b", "main")
        private_records = base / "private-records.json"
        atomic_json(private_records, {"entries": [{"approval_byte": 1, "disposition_byte": 1,
                                                  "sha256": digest(snapshot / "main.bf")}]})
        git_spec = {"git": {"executable": git, "sha256": digest(git)}, "repository": str(release),
                    "inventory": str(release / "inventory.json"), "extra_paths": ["inventory.json", "release.json", "release.sig", "capsule.cms"],
                    "empty_hooks_directory": str(hooks), "scratch_directory": str(scratch), "environment": environment,
                    "timeout_seconds": 30, "max_metadata_bytes": 1048576, "max_object_bytes": 1048576,
                    "private_records": str(private_records), "record_list_field": "entries", "digest_field": "sha256",
                    "selection_fields": ["approval_byte", "disposition_byte"], "selector": worker("private_select"),
                    "predicate": worker("leak_policy"), "max_objects": 100, "facts_per_record": 8,
                    "predicate_input_capacity": 4096, "report": str(base / "git-audit.json")}
        git_transport.stage(git_spec)
        git_call("-c", "commit.gpgSign=false", "commit", "-m", "synthetic signed fixture")
        git_transport.audit(git_spec)
        clone = base / "clone"
        git_call("clone", "--no-local", "--no-hardlinks", "--template=" + str(template), str(release), str(clone))

        runtime = base / "runtime"
        files = [{"source": str(path), "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}
                 for path in (ROOT / "host").rglob("*.py") if path.name != "runtime_entry.py"]
        files.extend([{"source": str(ROOT / "host/runtime_entry.py"), "path": "runtime_entry.py", "sha256": digest(ROOT / "host/runtime_entry.py")},
                      {"source": worker("clean_recovery")["executable"], "path": "clean_recovery.exe", "sha256": worker("clean_recovery")["sha256"]}])
        bundle({"files": files, "destination": str(runtime), "manifest": str(base / "runtime.json"), "max_bytes": 16777216})
        for path in (original, snapshot, base / "internal"):
            self.assertTrue(path.resolve().is_relative_to(base.resolve()))
            shutil.rmtree(path)
        plaintext.unlink()
        internal.unlink()

        def recovery(label):
            output = base / label
            output.mkdir()
            bindings = {
                "1": dict(fixture.common, source=str(clone / "release.json"), signature=str(clone / "release.sig"),
                          public_key=str(base / "signer.pub"), trusted_spki_sha256=digest(base / "signer.der")),
                "2": {"root": str(clone), "inventory": str(clone / "inventory.json"), "binding_record": str(clone / "release.json"),
                      "expected_fields": fields, "files": {"protected_inventory": str(clone / "inventory.json"), "recovery_capsule": str(clone / "capsule.cms")}},
                "3": dict(fixture.common, source=str(clone / "capsule.cms"), destination=str(output / "originals.tar"),
                          identity=str(base / "recipient.key"), certificate=str(base / "recipient.crt")),
                "4": {"source": str(output / "originals.tar"), "destination": str(output / "restored"), "manifest": str(output / "scope.json"), "limits": limits},
                "5": {"root": str(output / "restored"), "manifest": str(output / "scope.json"), "destination": str(output / "result.tar"), "max_archive_bytes": 1048576},
                "6": {"destination": str(output / "receipt.json"), "fields": {"format": "SYNTHETIC-SIGNED-RECOVERY"},
                      "files": {"result": str(output / "result.tar"), "release": str(clone / "release.json")}}}
            planner = runtime / "clean_recovery.exe"
            binding = {"planner": {"executable": str(planner), "sha256": digest(planner)}, "planner_input_bytes": 2,
                       "planner_timeout_seconds": 30, "planner_output_bytes": 4096, "journal": str(output / "flow.json"), "bindings": bindings}
            atomic_json(output / "binding.json", binding)
            result = run([sys.executable, "-I", str(runtime / "runtime_entry.py"), "flow", str(output / "binding.json"), "--command", "1"],
                         cwd=output, timeout=60, max_output=1048576)
            return output, result

        output, result = recovery("recovered")
        self.assertEqual(result["exit"], 0, result["stderr"].decode("utf-8", "replace"))
        verify_tree(output / "restored", expected)
        self.assertEqual(json.loads((output / "flow.json").read_text())["status"], "PASS")
        for name in ("release.sig", "capsule.cms"):
            path = clone / name
            original_bytes = path.read_bytes()
            changed = bytearray(original_bytes)
            changed[-1] ^= 1
            path.write_bytes(changed)
            rejected, result = recovery("reject-" + name)
            self.assertNotEqual(result["exit"], 0)
            self.assertFalse((rejected / "restored").exists())
            path.write_bytes(original_bytes)
        (clone / "unapproved").write_bytes(b"extra")
        rejected, result = recovery("reject-extra")
        self.assertNotEqual(result["exit"], 0)
        self.assertFalse((rejected / "restored").exists())


if __name__ == "__main__":
    unittest.main()
