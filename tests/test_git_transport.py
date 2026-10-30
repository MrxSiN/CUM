"""Draft exact-byte commit/clone and history privacy tests using real local Git.

BF predicates run in the independent interpreter; no native BF claim follows.
"""
import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost import git_transport
from host.bytehost.errors import HostError
from host.bytehost.process import checked
from host.bytehost.storage import atomic_json, digest, inventory, verify_tree
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Git unavailable")
class GitTransportTests(unittest.TestCase):
    def setup_repository(self, temporary):
        base = Path(temporary)
        repository = base / "release"
        repository.mkdir()
        (base / "hooks").mkdir()
        (base / "scratch").mkdir()
        (base / "template").mkdir()
        git = shutil.which("git")
        env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="Synthetic",
                   GIT_AUTHOR_EMAIL="test@example.invalid", GIT_COMMITTER_NAME="Synthetic",
                   GIT_COMMITTER_EMAIL="test@example.invalid")
        def run(*arguments):
            return checked([git, "-c", "core.hooksPath=" + str(base / "hooks"), "-C", str(repository), *arguments],
                           env=env, max_output=1048576)
        run("init", "--template=" + str(base / "template"), "-b", "main")
        (repository / "binary").write_bytes(b"\x00\xff\r\n\n")
        (repository / ".gitattributes").write_bytes(b"* -text -filter -ident\n")
        manifest = repository / "inventory.json"
        record = inventory(repository, ["inventory.json"], public=True)
        atomic_json(manifest, record)
        atomic_json(base / "private.json", {"entries": [{"approval_byte": 1, "disposition_byte": 1,
                    "sha256": hashlib.sha256(b"private original").hexdigest()}]})
        spec = {"git": {"executable": git, "sha256": digest(git)}, "repository": str(repository),
                "inventory": str(manifest), "extra_paths": ["inventory.json"],
                "empty_hooks_directory": str(base / "hooks"), "scratch_directory": str(base / "scratch"),
                "environment": env, "timeout_seconds": 30, "max_metadata_bytes": 1048576,
                "max_object_bytes": 1048576, "private_records": str(base / "private.json"),
                "record_list_field": "entries", "digest_field": "sha256",
                "selection_fields": ["approval_byte", "disposition_byte"],
                "max_objects": 100, "facts_per_record": 2, "predicate_input_capacity": 100,
                "report": str(base / "audit.json")}
        for key, name in (("selector", "private_select"), ("predicate", "leak_policy")):
            placeholder = base / name
            placeholder.write_bytes(b"not native; invocation interpreted in test only")
            spec[key] = {"executable": str(placeholder), "sha256": digest(placeholder)}
        return base, repository, spec, run

    def run_predicates(self, argv, **kwargs):
        if Path(argv[0]).name in ("private_select", "leak_policy"):
            source = ROOT / "src" / (Path(argv[0]).name + ".bf")
            return {"stdout": execute(source.read_bytes(), kwargs["stdin"]).output}
        return checked(argv, **kwargs)

    def test_binary_commit_and_real_clone_match_portable_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base, repository, spec, run = self.setup_repository(temporary)
            git_transport.stage(spec)
            run("-c", "commit.gpgSign=false", "commit", "-m", "synthetic release")
            with patch("host.bytehost.git_transport.checked", side_effect=self.run_predicates):
                git_transport.audit(spec)
            clone = base / "clone"
            run("clone", "--no-local", "--no-hardlinks", str(repository), str(clone))
            verify_tree(clone, inventory(repository, ["inventory.json"], public=True))
            self.assertEqual((clone / "binary").read_bytes(), b"\x00\xff\r\n\n")

    def test_removed_private_source_still_rejected_in_history(self):
        with tempfile.TemporaryDirectory() as temporary:
            base, repository, spec, run = self.setup_repository(temporary)
            leaked = repository / "old"
            leaked.write_bytes(b"private original")
            run("add", "old")
            run("-c", "commit.gpgSign=false", "commit", "-m", "historical leak")
            run("rm", "old")
            git_transport.stage(spec)
            run("-c", "commit.gpgSign=false", "commit", "-m", "removed original")
            with patch("host.bytehost.git_transport.checked", side_effect=self.run_predicates):
                with self.assertRaises(HostError) as failure:
                    git_transport.audit(spec)
            self.assertEqual(failure.exception.code, "CONFIDENTIALITY")


if __name__ == "__main__":
    unittest.main()
