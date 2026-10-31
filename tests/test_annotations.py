"""Independent dialect and continuation checks for the BF-authored filter."""
from pathlib import Path
import os
import tempfile
import unittest

from host.bytehost.errors import HostError
from host.bytehost.transport import worker_input, worker_output
from host.bytehost.storage import digest
from host.bytehost.worker import map_file
from tests.reference import execute


class AnnotationTests(unittest.TestCase):
    def apply(self, data, state=b'\x01\x00'):
        return worker_output(execute(Path('src/annotated_filter.bf').read_bytes(),
            worker_input(state, data), steps=100000000).output)

    def test_full_line_comments_win_over_command_punctuation_at_every_split(self):
        data = '# note > < + - . , [ ] Unicode é\r\n\t # [,]\n  , + .\r#tail'.encode()
        for split in range(len(data) + 1):
            first, state = self.apply(data[:split])
            second, state = self.apply(data[split:], state)
            self.assertEqual(first + second, b',+.')
            self.assertEqual(state, b'\x01\x02')

    def test_leading_space_and_record_boundaries_preserve_the_line_state(self):
        state = b'\x01\x00'
        output = bytearray()
        for byte in b' \t#.,[]\r\n,+.\n  #last':
            body, state = self.apply(bytes([byte]), state)
            output.extend(body)
        self.assertEqual(output, b',+.')
        self.assertEqual(self.apply(b'')[0], b'')
        self.assertEqual(self.apply(b'#\x00\xff<,>\n,+.')[0], b',+.')

    def test_inline_annotations_unknown_code_and_bad_state_fail_closed(self):
        for data, state in ((b'+ #inline', b'\x01\x00'), (b'word', b'\x01\x00'),
                            (b'\x00', b'\x01\x00'), (b'\xef\xbb\xbf+', b'\x01\x00'),
                            (b'\xff', b'\x01\x00'), (b'+', b'\x00\x00'), (b'+', b'\x01\x03')):
            with self.assertRaises(HostError): self.apply(data, state)

    def test_planner_orders_filter_before_layout_and_annotations(self):
        source = Path('src/annotated_flow.bf').read_bytes()
        self.assertEqual(execute(source, b'\x00\x02').output, bytes([28,47,0]))
        self.assertEqual(execute(source, b'\x01\x02').output, bytes([9,5,26,1,9,2,12,4,0]))
        for request in (b'\x02\x02', b'\x01\x00'):
            self.assertNotEqual(execute(source, request).output[-1], 0)


@unittest.skipUnless(os.environ.get('BYTEHOST_NATIVE_INTEGRATION') == '1', 'Native annotated workers require explicit opt-in')
class NativeAnnotationTests(unittest.TestCase):
    def test_native_mapping_preserves_line_state_and_does_not_publish_rejected_code(self):
        worker = Path(os.environ['BYTEHOST_NATIVE_DIRECTORY']) / 'annotated_filter.exe'
        with tempfile.TemporaryDirectory(prefix='native-annotations-') as temporary:
            root = Path(temporary)
            key = root / 'checkpoint.key'
            key.write_bytes(os.urandom(32))
            source = root / 'input.bf'
            source.write_bytes(b' \t# .,[\x00\xff]\r\n,+.\n#tail')
            base = {'worker': {'executable': str(worker), 'sha256': digest(worker)},
                    'source': str(source), 'state_key': str(key), 'initial_state_hex': '0100',
                    'input_capacity_bytes': 4096, 'output_capacity_bytes': 65536,
                    'max_output_bytes': 1048576, 'timeout_seconds': 30}
            for width in (1, 7, 31):
                output = root / ('out-' + str(width))
                map_file(dict(base, destination=str(output), journal=str(root / ('state-' + str(width))), record_payload_bytes=width))
                self.assertEqual(output.read_bytes(), b',+.')
            source.write_bytes(b'+\n#valid\n+#inline')
            rejected = root / 'rejected'
            with self.assertRaises(HostError):
                map_file(dict(base, destination=str(rejected), journal=str(root / 'bad-state'), record_payload_bytes=1))
            self.assertFalse(rejected.exists())


if __name__ == '__main__': unittest.main()
