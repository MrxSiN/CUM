import unittest
from pathlib import Path

from tests.machine_reference import transduce
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


class AdapterDraftTests(unittest.TestCase):
    def test_multi_cell_balanced_loops(self):
        programs = [b"+++[>++<-]>.", b"++[>++[>+<-]<-]>>.", b">,<- >.+.", b"[>+<]"]
        for original in programs:
            for profile in (1, 2, 3, 4):
                protected, state = transduce("bf_layout", original, profile)
                for data in (b"", b"\x00", b"\xff"):
                    self.assertEqual(execute(original, data).output, execute(protected, data).output)

    def test_movement_preconditions(self):
        for source in (b"<", b"[>]", b"+[<]", b"[", b"]"):
            with self.assertRaises(ValueError):
                transduce("bf_layout", source)
        with self.assertRaises(ValueError):
            transduce("bf_layout", b">" * 5, limit=4)

    def test_linear_virtualization(self):
        for original in (b"", b"+.+.", b",+.,-.", b"-.[-]"):
            if b"[" in original:
                with self.assertRaises(ValueError):
                    transduce("bf_virtualize", original, 3)
                continue
            protected, _ = transduce("bf_virtualize", original, 3)
            for data in (b"", b"\x00", b"\xff\x01"):
                before, after = execute(original, data), execute(protected, data)
                self.assertEqual(before.output, after.output)
                self.assertEqual(before.pointer, after.pointer)
                self.assertEqual(before.tape[0], after.tape[0])
                self.assertTrue(all(value == 0 for value in after.tape[1:]))

    def test_java_and_kotlin_real_emission(self):
        for language, extension in (("java", "java"), ("kotlin", "kt")):
            source = (ROOT / "tests/projects" / language / ("Arithmetic." + extension)).read_bytes()
            for profile in (1, 2, 3, 4):
                protected, _ = transduce(language + "_int_module", source, profile)
                self.assertIn(b"combine", protected)
                self.assertIn(b"carry", protected)
                self.assertNotEqual(source, protected)
            with self.assertRaises(ValueError):
                transduce(language + "_int_module", source + b"unexpected")


if __name__ == "__main__":
    unittest.main()
