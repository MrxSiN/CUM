"""Independent CMS/ML-KEM capability probe; never selects a CUM crypto mode."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import shutil
import tempfile

from host.bytehost.process import checked, pinned_executable, run
from host.bytehost.securestore import create_private_directory
from host.bytehost.storage import atomic_json, digest


def probe(tool):
    executable = pinned_executable(tool)
    version = checked([executable, 'version', '-a'], timeout=30, max_output=65536)['stdout'].decode(errors='replace')
    result = {'format': 'CMS-MLKEM-CAPABILITY-PROBE', 'status': 'BLOCKED',
              'openssl_sha256': digest(executable), 'version': version,
              'primitive': 'NOT STARTED', 'cms_recipient': 'NOT STARTED',
              'independent_interoperability': 'NOT STARTED', 'production_pq_admitted': False, 'steps': []}
    with tempfile.TemporaryDirectory(prefix='cms-probe-') as temp:
        root = Path(temp)/'private'
        private = {'destination': str(root)}
        if os.name == 'nt':
            whoami = shutil.which('whoami')
            observation = checked([whoami, '/user', '/fo', 'csv', '/nh'], timeout=30, max_output=65536)['stdout'].decode()
            private.update(whoami={'executable': whoami, 'sha256': digest(whoami)},
                           owner_sid=list(csv.reader(io.StringIO(observation)))[0][1].strip())
        create_private_directory(private)

        def attempt(label, *argv):
            observed = run([executable, *argv], timeout=120, max_output=1048576)
            result['steps'].append({'operation': label, 'exit': observed['exit'],
                'stderr': observed['stderr'].decode(errors='replace')})
            return observed['exit'] == 0

        key, public, cert, ca, ca_cert = (root/name for name in ('kem.key', 'kem.pub', 'kem.crt', 'ca.key', 'ca.crt'))
        if not attempt('ML-KEM-1024 key generation', 'genpkey', '-algorithm', 'ML-KEM-1024', '-out', str(key)):
            result['primitive'] = 'BLOCKED'; return result
        result['primitive'] = 'PASS'
        for label, argv in (
            ('public key export', ['pkey', '-in', str(key), '-pubout', '-out', str(public)]),
            ('disposable signer', ['genpkey', '-algorithm', 'ED25519', '-out', str(ca)]),
            ('disposable CA certificate', ['req', '-new', '-x509', '-key', str(ca), '-subj', '/CN=ProbeCA', '-days', '1', '-out', str(ca_cert)]),
            ('KEM recipient certificate', ['x509', '-new', '-force_pubkey', str(public), '-CA', str(ca_cert), '-CAkey', str(ca),
                                          '-set_serial', '1', '-subj', '/CN=ProbeRecipient', '-days', '1', '-out', str(cert)])):
            if not attempt(label, *argv):
                result['cms_recipient'] = 'BLOCKED'; return result
        payload, capsule, recovered = (root/name for name in ('input.bin', 'capsule.cms', 'recovered.bin'))
        payload.write_bytes(bytes(range(256)))
        if not attempt('CMS AES-256-GCM KEM recipient encryption', 'cms', '-encrypt', '-binary', '-aes-256-gcm',
                       '-outform', 'DER', '-in', str(payload), '-out', str(capsule), '-recip', str(cert)):
            result['cms_recipient'] = 'BLOCKED'; return result
        if not attempt('CMS KEM recipient decryption', 'cms', '-decrypt', '-binary', '-inform', 'DER',
                       '-in', str(capsule), '-inkey', str(key), '-recip', str(cert), '-out', str(recovered)):
            result['cms_recipient'] = 'BLOCKED'; return result
        if recovered.read_bytes() != payload.read_bytes():
            result.update(status='FAIL', cms_recipient='FAIL'); return result
        result.update(status='PARTIAL', cms_recipient='PASS',
                      reason='One-backend roundtrip only; RFC algorithms and independent interoperability not established')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('binding'); parser.add_argument('report')
    args = parser.parse_args()
    result = probe(json.loads(Path(args.binding).read_text(encoding='utf-8')))
    assert result['production_pq_admitted'] is False
    atomic_json(args.report, result)
    print(json.dumps({'status': result['status'], 'primitive': result['primitive'], 'cms_recipient': result['cms_recipient']}))
