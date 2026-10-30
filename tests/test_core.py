"""Draft core checks. Reference execution does not establish native execution."""
import unittest
from pathlib import Path

from host.bytehost.transport import worker_input, worker_output
from host.bytehost.errors import HostError
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


def core(name, data):
    return execute((ROOT / "src" / name).read_bytes(), data, steps=100000000).output


def transform(source, profile=2, seed=0):
    response = core("transform.bf", worker_input(bytes((profile, seed)), source))
    return worker_output(response)[0]


class CoreTests(unittest.TestCase):
    def test_all_sources_are_only_eight_commands(self):
        for path in (ROOT / "src").rglob("*.bf"):
            self.assertTrue(set(path.read_bytes()) <= set(b"><+-.,[]\r\n\t "))

    def test_echo_binary_zero_and_full_byte_range(self):
        source = bytes(range(256))
        actual = core("echo.bf", worker_input(b"\x00\xff", source))
        self.assertEqual(worker_output(actual), (source, b"\x00\xff"))

    def test_empty(self):
        self.assertEqual(transform(b""), b"")

    def test_filter(self):
        source = b"comment\x00+-.[],<>\xff"
        response = core("filter.bf", worker_input(b"\x00\x00", source))
        self.assertEqual(worker_output(response)[0], b"+-.[],<>")

    def test_byte_arithmetic_exhaustive(self):
        # Every initial cell value, both arithmetic operations and all profiles.
        for profile in range(1, 5):
            for seed in (0, 1, 255):
                for value in range(256):
                    for operation in (b"+", b"-"):
                        source = b"," + operation + b"."
                        protected = transform(source, profile, seed)
                        original_result = execute(source, bytes((value,)))
                        result = execute(protected, bytes((value,)))
                        self.assertEqual(result.output, original_result.output)
                        self.assertEqual(result.consumed, original_result.consumed)
                        self.assertEqual(result.pointer, 0)
                        self.assertEqual(result.tape[0], original_result.tape[0])
                        self.assertTrue(all(v == 0 for v in result.tape[1:]))

    def test_loops_wrapping_eof_and_binary_input(self):
        for source in (b"+++[.-]", b"-.[-].", b",[.-],.", b"[[-]]", b".,.,."):
            for data in (b"", b"\x00", b"\x01", b"\xff\x00"):
                for profile in (1, 2, 3):
                    self.assertEqual(execute(source, data).output,
                                     execute(transform(source, profile), data).output)

    def test_chunk_boundary_equivalence(self):
        source = b"+++[.-]ignored\x00,[-]."
        expected = transform(source)
        for width in (1, 2, 3, 5, 11):
            actual = b"".join(transform(source[i:i + width]) for i in range(0, len(source), width))
            self.assertEqual(actual, expected)

    def test_pointers_are_rejected_even_in_skipped_loop(self):
        for source in (b">", b"<", b"[>]", b"word > word"):
            with self.assertRaises(HostError):
                transform(source)

    def test_unknown_profile(self):
        for profile in (0, 5, 255):
            with self.assertRaises(HostError):
                transform(b"+", profile)

    def test_predicate_requires_every_gate(self):
        self.assertEqual(core("gates.bf", b"\x01" * 16), b"\x01")
        for index in range(16):
            for value in (0, 2, 255):
                data = bytearray(b"\x01" * 16)
                data[index] = value
                self.assertEqual(core("gates.bf", data), b"\x00")
        self.assertEqual(core("gates.bf", b"\x01" * 15), b"\x00")

    def test_planner_unknown_and_modes(self):
        for command in range(1, 9):
            result = core("cum.bf", bytes((command, 1)))
            self.assertEqual(result[-1], 0)
            self.assertEqual(len(result) % 2, 1)
        self.assertEqual(core("cum.bf", b"\xff\x01"), b"\x01")
        self.assertEqual(core("cum.bf", b"\x03\x00"), b"\x01")

    def test_prepare_gate_precedes_finalization(self):
        result = core("cum.bf", b"\x03\x01")
        plan = list(zip(result[:-1:2], result[1:-1:2]))
        self.assertEqual(plan[-2:], [(16, 38), (17, 39)])
        self.assertEqual(sum(op == 22 for op, _ in plan), 16)

    def test_adapter_denials(self):
        for language in range(1, 6):
            self.assertEqual(core("adapters.bf", bytes((language,))), b"\x00")
        for language in (0, 6, 255):
            self.assertNotEqual(core("adapters.bf", bytes((language,))), b"\x00")


if __name__ == "__main__":
    unittest.main()
