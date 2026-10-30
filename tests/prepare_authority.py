"""Independent synthetic-fixture reviewer; never production owner approval.

This tool executes no project code and authors no transformed source. Its separate
test identity signs only observations about the named disposable fixture.
"""
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from host.bytehost import crypto
from host.bytehost.errors import require
from host.bytehost.storage import atomic_json, digest, inventory, load, verify_tree


def main():
    action, binding_file = sys.argv[1:]
    binding = load(binding_file)
    root = Path(binding["root"])
    common = binding["crypto"]
    fields = dict(binding["review_fields"])
    require(fields["subject"] == "synthetic-byte-relay" and fields["production_approval"] is False,
            "REVIEW", "This authority admits only the disposable fixture")
    if action == "review":
        reports = {}
        for name, case in (("build", "build"), ("behavior", "behavior"),
                           ("normalization", "normalization"), ("budgets", "budgets")):
            record = load(root / ("reports/" + name + ".json"))
            require(record["status"] == "PASS" and record["case"] == case, "REVIEW", "A fixture check is missing")
            reports[name] = record
        require(load(root / "reports/machine-boundary.json")["status"] == "PASS", "REVIEW", "Host boundary check failed")
        require(load(root / "reports/budgets-resource.json")["status"] == "PASS", "REVIEW", "Measured memory is missing")
        for record in reports.values():
            require(record["source_files"] == reports["behavior"]["source_files"], "REVIEW", "Checks used different source bytes")
        require(reports["behavior"]["source_files"]["original"] == binding["fixture_sha256"],
                "REVIEW", "This is not the independently approved synthetic source")
        require(set(load(root / "reports/profile-budget.json")["decisions"]) == {1},
                "REVIEW", "A measured budget was not accepted")
        review = dict(fields, digests={"snapshot_manifest": digest(root / "scope.json"),
                                      "protected_mapping_report": digest(root / "reports/mapping.json")})
        atomic_json(root / "reviews.json", review)
        crypto.sign(dict(common, source=str(root / "reviews.json"), destination=str(root / "reviews.sig"),
                         identity=binding["review_identity"]))
    elif action == "policy":
        signature = dict(common, public_key=binding["release_public_key"], trusted_spki_sha256=binding["release_spki"])
        crypto.verify_signature(dict(signature, source=str(root / "clean-checkout/release.json"),
                                     signature=str(root / "clean-checkout/release.sig")))
        expected = inventory(root / "candidate", public=True)
        require(inventory(root / "clean-checkout", public=True) == expected, "INTEGRITY", "Clone differs from the independently signed candidate")
        exported = root / "clone-export"
        shutil.copytree(root / "clean-checkout", exported, ignore=shutil.ignore_patterns(".git"))
        require(inventory(exported, public=True) == expected, "INTEGRITY", "Recovery export differs")
        spec = binding["recovery"]
        verify_tree(root / "runtime", binding["runtime_inventory"])
        policy = {key: spec[key] for key in ("backend", "vm", "image", "argv", "workdir", "environment", "outputs")}
        policy.update(format="PINNED-ISOLATED-CAPABILITIES", mounts={mount["target"]: {
            "source": mount["source"], "readonly": mount["readonly"],
            **({"inventory": inventory(mount["source"])} if mount["readonly"] else {})} for mount in spec["mounts"]})
        atomic_json(spec["policy_file"], policy)
        crypto.sign(dict(common, source=spec["policy_file"], destination=binding["policy_signature_file"], identity=binding["review_identity"]))
    else:
        raise ValueError("Unknown fixture authority operation")


if __name__ == "__main__":
    main()
