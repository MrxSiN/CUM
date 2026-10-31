"""Project-scoped recovery: BF routing, context rejection and real crypto."""
import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from host.bytehost import crypto
from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, digest, inventory, load, verify_tree
from host.bytehost.trusted import assert_filesystem
from host.bytehost.vm import flow
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]
INIT = [(48, 1), (41, 2), (25, 3), (25, 4), (25, 5), (12, 6), (13, 7), (14, 8), (19, 9), (17, 10), (12, 11)]
SEAL = [(48, 1), (14, 2), (19, 3), (3, 4), (4, 5), (5, 6), (12, 7), (13, 8), (14, 9), (6, 10), (7, 11), (3, 12), (12, 13)]
RESTORE = [(14, 21), (14, 23), (19, 24), (19, 22), (6, 25), (7, 26), (4, 27), (12, 28)]


def bind(template, replacements):
    """Bind literal example operands; the BF planner owns every operation."""
    if isinstance(template, dict):
        result = {bind(k, replacements): bind(v, replacements) for k, v in template.items()}
        for field in ('planner', 'tool', 'openssl', 'whoami'):
            if isinstance(result.get(field), dict) and 'executable' in result[field]:
                result[field]['sha256'] = digest(result[field]['executable'])
        return result
    if isinstance(template, list):
        return [bind(v, replacements) for v in template]
    if isinstance(template, str):
        for before, after in sorted(replacements.items(), key=lambda item: -len(item[0])):
            template = template.replace(before, str(after))
    return template


class ProjectIdentityTests(unittest.TestCase):
    def test_native_plan_contract_reference_and_invalid_requests(self):
        for name, valid in (('identity_flow', {1: INIT}), ('project_recovery', {1: SEAL, 2: RESTORE})):
            source = (ROOT / 'src' / (name + '.bf')).read_bytes()
            self.assertTrue(all(c in b'><+-.,[]\r\n\t ' for c in source))
            for command in (0, 1, 2, 3, 255):
                for mode in (0, 1, 2, 255):
                    out = execute(source, bytes([command, mode])).output
                    if command in valid and mode == 1:
                        self.assertEqual(out, bytes(x for pair in valid[command] for x in pair) + b'\x00')
                    else:
                        self.assertFalse(out)

    def test_disjoint_storage_refuses_equal_or_nested_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assert_filesystem({'disjoint_trees': [[str(root/'original'), str(root/'vault')]]})
            for left, right in ((root, root), (root, root/'keys'), (root/'keys', root)):
                with self.assertRaises(HostError):
                    assert_filesystem({'disjoint_trees': [[str(left), str(right)]]})

    def test_examples_have_all_operands_and_separate_context_checks(self):
        init = load(ROOT / 'config/identity-flow.example.json')
        recovery = load(ROOT / 'config/project-recovery.example.json')
        for spec, plans in ((init, (INIT,)), (recovery, (SEAL, RESTORE))):
            for plan in plans:
                self.assertTrue(all(str(operand) in spec['bindings'] for _, operand in plan))
        self.assertEqual(recovery['bindings']['22']['fields']['project_id'], recovery['bindings']['24']['fields']['project_id'])
        self.assertIn('recipient_certificate', recovery['bindings']['22']['digest_fields'])
        self.assertNotIn('snapshot', recovery['bindings']['7']['files'])


@unittest.skipUnless(os.environ.get('CUM_PROJECT_NATIVE') and os.environ.get('BYTEHOST_CRYPTO_TESTS') == '1',
                     'Explicit fresh BF builds and real cryptography required')
class ProjectRecoveryNativeTests(unittest.TestCase):
    def test_project_identity_fresh_envelopes_recipients_and_context_rejection(self):
        from tests.test_crypto import CryptoTests
        fixture = CryptoTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        root = fixture.root
        job = root/'operation'; job.mkdir()
        whoami = shutil.which('whoami') if os.name == 'nt' else '/usr/bin/true'
        sid = ''
        if os.name == 'nt':
            import csv, io
            from host.bytehost.process import checked
            observation = checked([whoami, '/user', '/fo', 'csv', '/nh'], timeout=30, max_output=65536)['stdout'].decode()
            sid = list(csv.reader(io.StringIO(observation)))[0][1].strip()
        replacements = {'REPLACE_PROJECT_ID': 'disposable-project-a', 'REPLACE_RELEASE_ID': 'release-one',
            'REPLACE_SIGNER_PIN': digest(root/'signer.der'), 'REPLACE_OWNER_SID': sid,
            'REPLACE_OPENSSL': fixture.tool['executable'], 'REPLACE_WHOAMI': whoami,
            'REPLACE_NATIVE': os.environ['CUM_PROJECT_NATIVE'], 'REPLACE_JOB': job.as_posix(),
            'REPLACE_VAULT': (root/'vault').as_posix(), 'REPLACE_PENDING': (root/'pending').as_posix(),
            'REPLACE_SIGNER': (root/'signer.key').as_posix(), 'REPLACE_SIGNER_PUBLIC': (root/'signer.pub').as_posix(),
            'REPLACE_ORIGINAL': (root/'reference').as_posix(), 'REPLACE_TARGET': (root/'target').as_posix()}
        spec = bind(load(ROOT/'config/identity-flow.example.json'), replacements)
        flow(spec, 1)
        self.assertTrue((root/'vault/recovery.key.pem').is_file())
        with self.assertRaises(HostError):
            flow(spec, 1)
        original = job/'snapshot'; original.mkdir()
        (original/'policy.bf').write_bytes(b'# retained comment\r\n,+.\r\n')
        (original/'binary').write_bytes(bytes(range(256)))
        (original/'empty').mkdir()
        expected = inventory(original)
        atomic_json(job/'scope.json', expected)
        seal = bind(load(ROOT/'config/project-recovery.example.json'), replacements)
        seal['bindings']['6']['recipients'].append(str(root/'recipient.crt'))
        seal['bindings']['7']['files']['additional_recipient_certificate'] = str(root/'recipient.crt')
        flow(seal, 1)
        capsule = job/'package/capsule.cms'
        second = root/'second.cms'
        crypto.envelope(dict(fixture.common, source=str(job/'originals.tar'), destination=str(second),
                             recipients=[str(root/'vault/recovery.cert.pem')]))
        self.assertTrue(capsule.read_bytes() != second.read_bytes(), 'Randomized envelopes unexpectedly identical')
        crypto.envelope(dict(fixture.common, source=str(capsule), destination=str(root/'collaborator.tar'),
                             identity=str(root/'recipient.key'), certificate=str(root/'recipient.crt')), decrypt=True)
        self.assertEqual(digest(root/'collaborator.tar'), digest(job/'originals.tar'))
        from host.bytehost.process import checked
        from tests.tools.cms_fixture import wrapped_keys_and_nonce
        samples = []
        for path in (capsule, second):
            keys, nonce = wrapped_keys_and_nonce(path.read_bytes())
            recovered_keys = []
            for wrapped in keys:
                if len(wrapped) != 3072//8:
                    continue
                cek = checked([fixture.tool['executable'], 'pkeyutl', '-decrypt', '-inkey',
                    str(root/'vault/recovery.key.pem'), '-pkeyopt', 'rsa_padding_mode:pkcs1'],
                    stdin=wrapped, timeout=30, max_output=4096)['stdout']
                self.assertTrue(len(cek) == 32, 'Expected a 256-bit content key')
                recovered_keys.append(cek)
            self.assertTrue(len(recovered_keys) == 1, 'Owner wrapping must be recoverable exactly once')
            samples.append((recovered_keys[0], nonce))
        self.assertTrue(samples[0][0] != samples[1][0], 'Release CEKs must differ')
        self.assertTrue(samples[0][1] != samples[1][1], 'Sample GCM nonces must differ')
        del samples
        with self.assertRaises(HostError):
            crypto.envelope(dict(fixture.common, source=str(capsule), destination=str(root/'wrong.tar'),
                                 identity=str(root/'wrong.key'), certificate=str(root/'wrong.crt')), decrypt=True)
        self.assertFalse((root/'wrong.tar').exists())
        self.assertTrue(original.resolve().is_relative_to(root.resolve()))
        shutil.rmtree(original)
        (job/'originals.tar').unlink()
        self.assertTrue((job/'internal').resolve().is_relative_to(root.resolve()))
        shutil.rmtree(job/'internal')
        (job/'internal.tar').unlink()
        recover = copy.deepcopy(seal); recover['journal'] = str(root/'recover-flow.json')
        flow(recover, 2)
        verify_tree(job/'recovered', expected)
        for label, edit in (
            ('project', lambda b: b['22']['fields'].update(project_id='another-project')),
            ('release', lambda b: b['22']['fields'].update(release_identity='another-release')),
            ('recipient', lambda b: b['22']['digest_fields'].update(recipient_certificate=str(root/'wrong.crt'))),
            ('identity-project', lambda b: b['24']['fields'].update(project_id='another-project'))):
            rejected = copy.deepcopy(recover); rejected['journal'] = str(root/(label+'-flow.json'))
            edit(rejected['bindings'])
            with patch('host.bytehost.crypto.envelope') as decrypt, self.assertRaises(HostError):
                flow(rejected, 2)
            decrypt.assert_not_called()
        for label, changed in (('truncated', capsule.read_bytes()[:-1]),
                               ('corrupt', capsule.read_bytes()[:-1] + bytes([capsule.read_bytes()[-1] ^ 1]))):
            mutation = root/(label+'.cms'); mutation.write_bytes(changed)
            with self.assertRaises(HostError):
                crypto.envelope(dict(fixture.common, source=str(mutation), destination=str(root/(label+'.tar')),
                    identity=str(root/'vault/recovery.key.pem'), certificate=str(root/'vault/recovery.cert.pem')), decrypt=True)
            self.assertFalse((root/(label+'.tar')).exists())


if __name__ == '__main__':
    unittest.main()
