"""The JSON CLI must preserve binary output from generic isolation services."""
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from host.bytehost.__main__ import main
from host.bytehost.errors import HostError


class ServiceOutputTests(unittest.TestCase):
    def test_binary_service_streams_are_explicit_hex(self):
        output = io.BytesIO()
        with patch('sys.argv', ['bytehost', 'service', '44', 'unused.json']), \
             patch('host.bytehost.__main__.load', return_value={}), \
             patch.dict('host.bytehost.__main__.SERVICES', {44: lambda _: {
                 'exit': 0, 'stdout': b'\x00\xff', 'stderr': b'\x80\r\n',
                 'resources': {'status': 'PASS'}}}), \
             patch('sys.stdout', SimpleNamespace(buffer=output)):
            main()
        self.assertEqual(json.loads(output.getvalue()), {'status': 'PASS', 'result': {
            'exit': 0, 'stdout_hex': '00ff', 'stderr_hex': '800d0a',
            'resources': {'status': 'PASS'}}})

    def test_conflicting_hex_field_is_rejected(self):
        with patch('sys.argv', ['bytehost', 'service', '44', 'unused.json']), \
             patch('host.bytehost.__main__.load', return_value={}), \
             patch.dict('host.bytehost.__main__.SERVICES', {44: lambda _: {
                 'stdout': b'\x00', 'stdout_hex': 'ff'}}), \
             self.assertRaises(HostError):
            main()


if __name__ == '__main__':
    unittest.main()
