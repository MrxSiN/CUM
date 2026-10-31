"""Amended release-policy checks; mocks never establish native or AI evidence."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, digest
from host.bytehost.vm import assert_record, byte_assertion, flow
from tests.reference import execute
from tests.test_workflow_draft import plan
from tests.tools.normalize import normalize

ROOT = Path(__file__).resolve().parents[1]


def cases():
    for profile in range(1, 5):
        for claim in (0, 1):
            valid = bytes([profile, claim] + [1] * 10)
            yield valid, b"\x01"
            for index in range(2, 12):
                for state in (0, 2, 3, 4, 5):
                    value = bytearray(valid)
                    value[index] = state
                    needed = index < 5 or profile in (2, 3) or claim == 1
                    yield bytes(value), (b"\x02" if state == 2 else b"\x03") if needed else b"\x01"
    for index, value in ((0, 0), (0, 5), (1, 2), (1, 255), *[(i, 6) for i in range(2, 12)]):
        request = bytearray([2, 0] + [1] * 10)
        request[index] = value
        yield bytes(request), b"\x02"
    yield bytes([2, 0, 0, 2] + [1] * 8), b"\x02"


class ResistanceTests(unittest.TestCase):
    def test_bf_profile_policy_unknowns_failures_and_nonclaims(self):
        source = (ROOT / "src/resistance_policy.bf").read_bytes()
        for request, expected in cases():
            with self.subTest(request=request.hex()):
                self.assertEqual(execute(source, request, steps=10000000).output, expected)

    def test_observed_bytes_are_complete_and_strictly_typed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tool = root / "tool"
            tool.write_bytes(b"placeholder; process mocked")
            record = root / "observation.json"
            spec = {"worker": {"executable": str(tool), "sha256": digest(tool)},
                    "input_fields": [{"file": str(record), "fields": ["value"]}],
                    "input_bytes": 1, "expected_hex": "01", "timeout_seconds": 1, "max_output_bytes": 10}
            atomic_json(record, {"value": 255})
            with patch("host.bytehost.vm.checked", return_value={"stdout": b"\x01"}) as run:
                byte_assertion(spec)
                self.assertEqual(run.call_args.kwargs["stdin"], b"\xff")
            for value in (True, "1", None, -1, 256, 1.0):
                atomic_json(record, {"value": value}, replace=True)
                with patch("host.bytehost.vm.checked") as run, self.assertRaises(HostError):
                    byte_assertion(spec)
                run.assert_not_called()
            atomic_json(record, {"value": 1}, replace=True)
            for invalid in (dict(spec, input_bytes=2), dict(spec, input_hex="01")):
                with patch("host.bytehost.vm.checked") as run, self.assertRaises(HostError):
                    byte_assertion(invalid)
                run.assert_not_called()
            with patch("host.bytehost.vm.checked", return_value={"stdout": b"\x03"}), self.assertRaises(HostError):
                byte_assertion(spec)

    def test_comparison_and_digest_bindings_reject_stale_or_mismatched_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact, plan_file, review = [root / name for name in ("artifact", "plan.json", "review.json")]
            artifact.write_bytes(b"frozen candidate")
            atomic_json(plan_file, {"profile": 2})
            atomic_json(review, {"profile": 2, "artifact_sha256": digest(artifact)})
            spec = {"source": str(review), "fields": {},
                    "file_digests": {"artifact_sha256": str(artifact)},
                    "equal_fields": {"profile": {"file": str(plan_file), "fields": ["profile"]}}}
            assert_record(spec)
            atomic_json(plan_file, {"profile": 1}, replace=True)
            with self.assertRaises(HostError):
                assert_record(spec)
            atomic_json(plan_file, {"profile": 2}, replace=True)
            artifact.write_bytes(b"changed candidate")
            with self.assertRaises(HostError):
                assert_record(spec)

    def test_failed_resistance_gate_stops_before_signing(self):
        source = (ROOT / "src/cum.bf").read_bytes()
        response = execute(source, bytes([3, 1]), steps=100000000).output
        instructions = plan("cum.bf", bytes([3, 1]))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tool = root / "planner"
            tool.write_bytes(b"placeholder")
            spec = {"planner": {"executable": str(tool), "sha256": digest(tool)},
                    "planner_input_bytes": 2, "planner_timeout_seconds": 1, "planner_output_bytes": 4096,
                    "journal": str(root / "flow.json"),
                    "bindings": {str(operand): {"operand": operand} for opcode, operand in instructions if opcode != 22}}
            calls = []
            def service(binding):
                calls.append(binding["operand"])
                if binding["operand"] == 80:
                    raise HostError("BYTE_ASSERTION", "Blocked by BF resistance policy")
            from host.bytehost.vm import SERVICES
            with patch("host.bytehost.vm.checked", return_value={"stdout": response}), \
                 patch.dict(SERVICES, {opcode: service for opcode in SERVICES}):
                with self.assertRaises(HostError):
                    flow(spec, 3)
            self.assertIn(80, calls)
            self.assertNotIn(27, calls)
            self.assertNotIn(28, calls)
            self.assertNotIn(39, calls)

    def test_examples_bind_private_evidence_and_public_claims(self):
        build = json.loads((ROOT / "config/build.example.json").read_text())
        for name in ("cum", "maintenance", "resistance_policy"):
            self.assertIn("D:/GitHub/CUM/src/" + name + ".bf", build["sources"])
        for name in ("public-job", "private-vault-job", "java-job", "kotlin-job", "xax-job"):
            job = json.loads((ROOT / "config" / (name + ".example.json")).read_text())
            bindings = job["bindings"]
            self.assertEqual(bindings["75"]["source"], bindings["76"]["source"])
            for key in ("bindings_sha256", "planner_sha256", "request_hex"):
                self.assertEqual(bindings["76"]["equal_fields"][key],
                                 {"file": job["journal"], "fields": [key]})
            self.assertEqual(bindings["78"]["source"], bindings["79"]["source"])
            self.assertEqual(len(bindings["80"]["input_fields"]), 12)
            self.assertEqual(bindings["79"]["file_digests"]["protected_inventory_sha256"], bindings["26"]["destination"])
            for key in ("plan_sha256", "criteria_sha256", "job_sha256"):
                self.assertEqual(bindings["79"]["equal_fields"][key]["file"], bindings["81"]["destination"])
            self.assertFalse(any("sha256" in key for key in bindings["27"]["observed_fields"]))

    def test_affine_loop_attack_retains_bounds_and_rejects_unsafe_reductions(self):
        self.assertEqual(normalize(b"[->+<]"), normalize(b"[+>-<]"))
        self.assertEqual(normalize(b"[---]"), [["clear"]])
        self.assertNotEqual(normalize(b"[--]"), [["clear"]])
        self.assertNotEqual(normalize(b"[->+<]"), normalize(b"[->+><<]"))
        self.assertNotEqual(normalize(b"[->+<]"), normalize(b"[->+>><<<]"))
        self.assertEqual(normalize(b"[.,]"), [["loop", [["output"], ["input"]]]])
        for counter in (b"+", b"+++", b"-"):
            source = b",[" + counter + b">++<]>."
            form = normalize(source)[1]
            self.assertEqual(form[0], "affine")
            coefficient = form[1][0][1]
            for value in range(256):
                self.assertEqual(execute(source, bytes([value])).output,
                                 bytes([(coefficient * value) % 256]))
        self.assertEqual(normalize(b"[<+>-]")[0][2], [-1, 0])
        execute(b",[<+>-]", b"\x00")
        with self.assertRaises(IndexError):
            execute(b",[<+>-]", b"\x01")
        for source in (b"[", b"]"):
            with self.assertRaises(ValueError):
                normalize(source)

    @unittest.skipUnless(os.environ.get("CUM_AMENDMENT_NATIVE"), "Explicit freshly built native artifact directory required")
    def test_native_policy_and_planners(self):
        from host.bytehost.process import checked
        root = Path(os.environ["CUM_AMENDMENT_NATIVE"])
        for request, expected in cases():
            result = checked([str(root / "resistance_policy.exe")], stdin=request, timeout=5, max_output=16)
            self.assertEqual(result["stdout"], expected)
        for name, requests in (("cum", (bytes([3, mode]) for mode in (1, 2))),
                               ("maintenance", (bytes([4, 1]),))):
            for request in requests:
                result = checked([str(root / (name + ".exe"))], stdin=request, timeout=5, max_output=4096)
                expected = execute((ROOT / "src" / (name + ".bf")).read_bytes(), request, steps=100000000).output
                self.assertEqual(result["stdout"], expected)

    @unittest.skipUnless(os.environ.get("CUM_AMENDMENT_NATIVE") and os.environ.get("BYTEHOST_CRYPTO_TESTS") == "1",
                         "Fresh native policy and real-tool crypto opt-in required")
    def test_signed_fixture_native_admission_and_missing_evaluation(self):
        from host.bytehost import crypto
        from tests.test_crypto import CryptoTests
        fixture = CryptoTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        record = fixture.root / "admission.json"
        native = Path(os.environ["CUM_AMENDMENT_NATIVE"]) / "resistance_policy.exe"
        spec = {"worker": {"executable": str(native), "sha256": digest(native)},
                "input_fields": [{"file": str(record), "fields": ["facts", i]} for i in range(12)],
                "input_bytes": 12, "expected_hex": "01", "timeout_seconds": 5, "max_output_bytes": 16}
        for profile in (1, 2):
            atomic_json(record, {"fixture_only": True, "facts": [profile, 0, 1, 1, 1] + [0] * 7}, replace=profile == 2)
            signature = fixture.root / (str(profile) + ".sig")
            crypto.sign(dict(fixture.common, source=str(record), destination=str(signature),
                             identity=str(fixture.root / "signer.key")))
            verify = dict(fixture.common, source=str(record), signature=str(signature),
                          public_key=str(fixture.root / "signer.pub"),
                          trusted_spki_sha256=digest(fixture.root / "signer.der"))
            crypto.verify_signature(verify)
            if profile == 1:
                byte_assertion(spec)
            else:
                with self.assertRaises(HostError):
                    byte_assertion(spec)
        record.write_bytes(record.read_bytes() + b" ")
        with self.assertRaises(HostError):
            crypto.verify_signature(verify)


if __name__ == "__main__":
    unittest.main()
