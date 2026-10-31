"""BF-authored annotations and restricted markup presentation retain semantics."""
from html import unescape
from pathlib import Path
import unittest

from host.bytehost.errors import HostError
from host.bytehost.transport import worker_input, worker_output
from tests.reference import execute
from tests.prepare_checks import Document


class PresentationTests(unittest.TestCase):
    def apply(self, mode, data, state=0):
        source = Path("src/presentation.bf").read_bytes()
        result = execute(source, worker_input(bytes([mode, state]), data), steps=100000000).output
        return worker_output(result)

    def test_comments_have_no_commands_and_are_emitted_once_across_records(self):
        first, state = self.apply(1, b",+")
        second, state = self.apply(1, b".", state[1])
        comments = first[:-2]
        self.assertTrue(all(line.startswith(b'# ') for line in comments.splitlines()))
        self.assertTrue(set(comments).isdisjoint(b"><+-.,[]"))
        self.assertIn(b"Accumulator transition", comments)
        self.assertEqual(second, b".")
        self.assertEqual(bytes(c for c in first + second if c in b"><+-.,[]"), b",+.")

    def test_markup_roundtrip_across_every_split_preserves_structure_and_text(self):
        source = b"<h1>Byte Relay</h1>\n<p>One octet.</p>"
        expected = Document(source.decode())
        for split in range(len(source) + 1):
            first, state = self.apply(2, source[:split])
            second, state = self.apply(2, source[split:], state[1])
            output = first + second
            actual = Document(output.decode())
            self.assertEqual(actual.tags, expected.tags)
            self.assertEqual(actual.text, expected.text)
            self.assertNotEqual(output, source)
            self.assertEqual(state, b"\x02\x00")

    def test_unsupported_entities_nonascii_and_modes_reject(self):
        for mode, data in ((2, b"&amp;"), (2, b"\xff"), (0, b"text"), (3, b"text")):
            with self.assertRaises(HostError):
                self.apply(mode, data)
