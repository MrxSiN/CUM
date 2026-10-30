import io
import unittest

from host.bytehost.errors import HostError
from host.bytehost.transport import frame, read_frame, varint, worker_input


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.header = {"operation": "opaque-test", "request": "r", "sequence": "0", "state": "00ff"}

    def read(self, value):
        return read_frame(io.BytesIO(value), max_header=4096, max_payload=4096)

    def test_binary_and_empty(self):
        for value in (b"", b"\x00", bytes(range(256))):
            header, actual = self.read(frame(self.header, value))
            self.assertEqual(actual, value)
            self.assertEqual(header["payload_bytes"], str(len(value)))

    def test_every_truncation_is_rejected(self):
        encoded = frame(self.header, b"\x00hello\xff")
        for index in range(len(encoded)):
            with self.assertRaises(HostError):
                self.read(encoded[:index])

    def test_tampering_and_trailing(self):
        encoded = frame(self.header, b"\x00hello\xff")
        for index in range(len(encoded)):
            mutated = bytearray(encoded)
            mutated[index] ^= 1
            with self.assertRaises((HostError, ValueError, UnicodeError)):
                self.read(mutated)
        with self.assertRaises(HostError):
            self.read(encoded + b"\x00")

    def test_pair_encoding(self):
        self.assertEqual(worker_input(b"\x02\x00", b"\x00\x01"), b"\x02\x00\x01\x00\x01\x01\x00")

    def test_varint_not_fixed_width(self):
        for value in (0, 127, 128, 65536, 2 ** 128):
            self.assertIsInstance(varint(value), bytes)

    def test_negotiated_budget(self):
        with self.assertRaises(HostError):
            read_frame(io.BytesIO(frame(self.header, b"a" * 4097)), max_header=4096, max_payload=4096)


if __name__ == "__main__":
    unittest.main()
