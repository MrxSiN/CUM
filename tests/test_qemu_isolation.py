"""Generic VM transport faults and opt-in real isolation boundary checks."""
import json
import io
import os
from pathlib import Path
import socket
import sys
import tempfile
import types
import time
import unittest
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.process import isolated
from host.bytehost.qemu_isolation import packet, receive
from host.providers.bytevm_seed import seed
if os.name == "nt":
    # Only exercise platform-neutral framing here; real guest execution is separate.
    with patch.dict(sys.modules, {"resource": types.ModuleType("resource")}):
        from host.providers import bytevm_agent
else:
    from host.providers import bytevm_agent


class VmPacketTests(unittest.TestCase):
    def test_guest_partial_writes_complete_large_binary_safe_responses(self):
        class PartialWriter(io.BytesIO):
            def write(self, value):
                return super().write(value[:7])
        value = {"binary": "\x00\xff" * 65536}
        stream = PartialWriter()
        bytevm_agent.send(stream, value)
        stream.seek(0)
        self.assertEqual(bytevm_agent.receive(stream, 1048576), value)

    def test_provisioning_seed_binds_the_current_generic_agent(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "seed"
            seed(destination)
            config = json.loads((destination / "user-data").read_text().split("\n", 1)[1])
            self.assertEqual(config["write_files"][0]["content"],
                             Path("host/providers/bytevm_agent.py").read_text())
            self.assertEqual(config["packages"], ["python3", "openssl", "wine64", "git"])
            self.assertIn(["touch", "/etc/cloud/cloud-init.disabled"], config["runcmd"])
            with self.assertRaises(FileExistsError):
                seed(destination)

    def exchange(self, data, limit=4096):
        left, right = socket.socketpair()
        with left, right:
            left.sendall(data)
            left.shutdown(socket.SHUT_WR)
            return receive(right, limit)

    def test_binary_safe_complete_packet_and_every_truncation(self):
        value = {"zero": "\x00", "bytes": list(range(256))}
        encoded = packet(value)
        self.assertEqual(self.exchange(encoded), value)
        for length in range(len(encoded)):
            with self.assertRaises(HostError):
                self.exchange(encoded[:length])

    def test_tampering_and_explicit_packet_budget(self):
        encoded = bytearray(packet({"nonce": "opaque"}))
        encoded[-1] ^= 1
        with self.assertRaises(HostError):
            self.exchange(encoded)
        with self.assertRaises(HostError):
            self.exchange(packet({"nonce": "opaque"}), limit=1)

    def test_wall_deadline_is_not_extended_by_partial_reads(self):
        left, right = socket.socketpair()
        with left, right:
            left.sendall(packet({"nonce": "opaque"}))
            with self.assertRaises(HostError) as rejection:
                receive(right, 4096, deadline=time.monotonic() - 1)
            self.assertEqual(rejection.exception.code, "TIMEOUT")


@unittest.skipUnless(os.environ.get("BYTEHOST_VM_TESTS") == "1", "Real VM test requires an independently pinned image")
class QemuIsolationTests(unittest.TestCase):
    def test_no_network_readonly_inputs_confined_outputs_and_no_host_share(self):
        vm = json.loads(Path(os.environ["BYTEHOST_VM_BINDING"]).read_text())
        with tempfile.TemporaryDirectory(prefix="vm-boundary-") as temporary:
            root = Path(temporary)
            source, output = root / "input", root / "output"
            source.mkdir()
            output.mkdir()
            data = bytes(range(256)) * 1024
            (source / "binary").write_bytes(data)
            (root / "host-only-secret").write_bytes(b"synthetic unmounted secret")
            code = """import json,os,socket
from pathlib import Path
assert os.getuid()==1000
assert sorted(os.listdir('/sys/class/net'))==['lo']
assert Path('/inputs/binary').read_bytes()==bytes(range(256))*1024
try:
    Path('/inputs/binary').write_bytes(b'changed')
except PermissionError:
    pass
else:
    raise AssertionError('Readonly input was writable')
assert not Path('/mnt/c').exists() and not Path('/mnt/d').exists()
s=socket.socket();s.settimeout(1)
try:
    s.connect(('192.0.2.1',443))
except OSError:
    pass
else:
    raise AssertionError('Guest reached a network endpoint')
finally:
    s.close()
Path('/outputs/result').write_bytes(bytes(range(256))*1024)
print(json.dumps({'status':'PASS','uid':os.getuid(),'interfaces':os.listdir('/sys/class/net')}))
"""
            spec = {"backend": "qemu", "vm": vm, "image": "BYTEVM-IMAGE@sha256:" + vm["disk"]["sha256"],
                    "memory_bytes": 4294967296, "cpus": 2, "user": "1000:1000", "pids": 64,
                    "environment": {}, "argv": ["/usr/bin/python3", "-c", code], "workdir": "/inputs",
                    "timeout_seconds": 30, "max_output_bytes": 1048576,
                    "mounts": [{"source": str(source), "target": "/inputs", "readonly": True},
                               {"source": str(output), "target": "/outputs", "readonly": False}],
                    "outputs": [{"guest": "/outputs/result", "destination": str(root / "result")} ]}
            result = isolated(spec)
            self.assertEqual(result["exit"], 0)
            self.assertEqual(result["network_interfaces"], ["lo"])
            self.assertEqual((source / "binary").read_bytes(), data)
            self.assertEqual((root / "result").read_bytes(), data)
            spec["outputs"][0]["guest"] = "/outputs/../etc/shadow"
            with self.assertRaises(HostError) as rejection:
                isolated(spec)
            self.assertEqual(rejection.exception.code, "PATH")
