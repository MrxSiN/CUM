import unittest
from pathlib import Path

from tests.reference import execute
from host.bytehost.transport import worker_input, worker_output
from host.bytehost.errors import HostError

ROOT = Path(__file__).resolve().parents[1]


class PolicyTests(unittest.TestCase):
    def core(self, name, data):
        return execute((ROOT / "src" / name).read_bytes(), data, steps=100000000).output

    def test_budget_no_unknown_success(self):
        self.assertEqual(self.core("budget_policy.bf", bytes([1, 1, 1, 1])), b"\x01")
        self.assertEqual(self.core("budget_policy.bf", bytes([1, 1, 2, 1])), b"\x00")
        self.assertEqual(self.core("budget_policy.bf", bytes([2, 1, 2, 1])), b"\x02")
        for request in (bytes([2, 0, 1, 1]), bytes([2, 1, 0, 1]), bytes([2, 1, 1, 0])):
            self.assertEqual(self.core("budget_policy.bf", request), b"\x00")

    def test_known_extensions_and_explicit_resources(self):
        for name, expected in ((b"folder/a.bf", 1), (b"graph.xax", 2), (b"Arithmetic.java", 3),
                               (b"Arithmetic.kt", 4), (b"README.md", 0), (b"a.bfx", 0)):
            result = self.core("discovery.bf", worker_input(b"\x00\x00", name))
            self.assertEqual(worker_output(result)[0], bytes([expected]))
        self.assertEqual(self.core("scope_policy.bf", bytes([0, 2, 1, 1])), b"\x01")
        self.assertEqual(self.core("scope_policy.bf", bytes([0, 1, 1, 1])), b"\x00")
        self.assertEqual(self.core("scope_policy.bf", bytes([1, 2, 1, 1])), b"\x00")
        self.assertEqual(self.core("scope_policy.bf", bytes([2, 4, 1, 1])), b"\x01")
        self.assertEqual(self.core("scope_policy.bf", bytes([3, 3, 2, 1])), b"\x01")
        self.assertEqual(self.core("project.bf", bytes([1, 4])), b"\x00\x00")

    def test_private_path_guard(self):
        for name in (b"private/source.bf", b"secret.KEY", b"originals.tar", b"identity.pem", b".env"):
            response = self.core("path_policy.bf", worker_input(b"\x00\x00", name))
            with self.assertRaises(HostError):
                worker_output(response)
        worker_output(self.core("path_policy.bf", worker_input(b"\x00\x00", b"capsule.cms")))

    def test_human_commands_are_bf_owned(self):
        for name, expected in ((b"doctor", 1), (b"toolchain inspect", 2), (b"prepare", 3),
                               (b"verify", 4), (b"recover", 5), (b"test-recovery", 6),
                               (b"benchmark", 7), (b"audit", 8)):
            response = self.core("command.bf", worker_input(b"\x01\x00", name))
            self.assertEqual(worker_output(response)[0], bytes([expected, 1]))
        with self.assertRaises(HostError):
            worker_output(self.core("command.bf", worker_input(b"\x01\x00", b"prepare anything")))

    def test_command_parser_rejects_prefixes_suffixes_and_changed_bytes(self):
        names = (b"doctor", b"toolchain inspect", b"prepare", b"verify", b"recover",
                 b"test-recovery", b"benchmark", b"audit")
        invalid = {b"", b"doctorrecover", b"test-doctor", b"audit" + b"\x00" * 256}
        for name in names:
            invalid.update(name[:index] for index in range(len(name)))
            invalid.update(name + suffix for suffix in (b"x", b"\x00", b"\xff"))
            for index in range(len(name)):
                invalid.add(name[:index] + bytes([name[index] ^ 128]) + name[index + 1:])
        for request in invalid:
            with self.subTest(request=request), self.assertRaises(HostError):
                worker_output(self.core("command.bf", worker_input(b"\x02\xff", request)))
        for identity, name in enumerate(names, 1):
            payload, state = worker_output(self.core("command.bf", worker_input(b"\x02\xff", name)))
            self.assertEqual(payload, bytes([identity, 2]))
            self.assertEqual(state, b"\x02\xff")


if __name__ == "__main__":
    unittest.main()
