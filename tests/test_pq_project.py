"""PQ project identity/recovery uses BF orchestration and standard cryptographic services."""
import copy
import csv
import io
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from host.bytehost import crypto
from host.bytehost.errors import HostError
from host.bytehost.process import checked
from host.bytehost.storage import atomic_json,digest,inventory,load,verify_tree
from host.bytehost.vm import flow
from tests.reference import execute
from tests.test_project_identity import bind
from tests.test_pq_cms import java_cms

ROOT=Path(__file__).resolve().parents[1]
SCHEME='CMS-ML-KEM-1024-HKDF-SHA256-AES256-WRAP'
INIT=[(48,1),(14,14),(19,15),(41,2),(25,3),(25,4),(25,12),(25,5),(12,6),(13,7),(14,8),(19,9),(17,10),(12,11)]


class PqProjectContractTests(unittest.TestCase):
    def test_bf_plan_rejects_unknown_commands_and_requires_compatibility_before_keys(self):
        source=(ROOT/'src/pq_identity_flow.bf').read_bytes()
        self.assertTrue(all(c in b'><+-.,[]\r\n\t ' for c in source))
        expected=bytes([x for pair in INIT for x in pair]+[0])
        for command in (0,1,2,3,255):
            for mode in (0,1,2,255):
                self.assertEqual(execute(source,bytes([command,mode])).output,
                                 expected if (command,mode)==(1,1) else b'')

    def test_examples_bind_pq_suite_runtime_pins_and_signed_context_without_changing_classical(self):
        self.assertEqual(bind({'inputs_sha256':{'REPLACE_PATH':'REPLACE_PIN'}},
                              {'REPLACE_PATH':'actual-path','REPLACE_PIN':'actual-pin'}),
                         {'inputs_sha256':{'actual-path':'actual-pin'}})
        init=load(ROOT/'config/pq-identity-flow.example.json')
        recovery=load(ROOT/'config/pq-project-recovery.example.json')
        self.assertTrue(all(str(operand) in init['bindings'] for _,operand in INIT))
        self.assertEqual(init['bindings']['6']['fields']['recipient_scheme'],SCHEME)
        self.assertIs(init['bindings']['6']['fields']['post_quantum'],True)
        for index in ('6','10','25'):
            self.assertEqual(len(recovery['bindings'][index]['inputs_sha256']),2)
            self.assertEqual(recovery['bindings'][index]['environment']['OPENSSL_CONF'],'NUL')
        self.assertEqual(recovery['bindings']['6']['recipient_kdf'],'HKDF-SHA256')
        self.assertEqual(recovery['bindings']['6']['key_wrap_cipher'],'AES-256-WRAP')
        self.assertIs(recovery['bindings']['22']['fields']['post_quantum'],True)
        self.assertIs(load(ROOT/'config/project-recovery.example.json')['bindings']['22']['fields']['post_quantum'],False)
        self.assertEqual(load(ROOT/'config/public-job.example.json')['bindings']['83']['fields']['recipient_scheme'],
                         'CLASSICAL-CMS-RSA-3072')

    def test_changed_crypto_runtime_input_refuses_before_process_and_cleans_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.write_bytes(b'Synthetic')
            runtime=root/'runtime';runtime.write_bytes(b'Changed')
            spec={'openssl':{'executable':sys.executable,'sha256':digest(sys.executable)},
                'inputs_sha256':{str(runtime):'0'*64},'source':str(source),'destination':str(root/'output'),
                'recipients':['unused.crt'],'timeout_seconds':30,'max_log_bytes':65536,'max_output_bytes':65536}
            with patch('host.bytehost.trusted.checked') as process,self.assertRaises(HostError):
                crypto.envelope(spec)
            process.assert_not_called()
            self.assertFalse((root/'output').exists())
            self.assertFalse(list(root.glob('.pending-*')))


@unittest.skipUnless(os.environ.get('CUM_PQ_PROJECT_NATIVE') and os.environ.get('CUM_PQ_INTEROP_BINDING')
                     and os.environ.get('CUM_PQ_COMPATIBILITY_RECORD') and os.environ.get('BYTEHOST_CRYPTO_TESTS')=='1',
                     'Fresh native BF planners, pinned independent CMS tool and executed compatibility record required')
class PqProjectNativeTests(unittest.TestCase):
    def test_native_identity_and_signed_recovery_with_independent_decryption(self):
        from tests.test_crypto import CryptoTests
        fixture=CryptoTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        root=fixture.root;job=root/'job';job.mkdir()
        pq=load(os.environ['CUM_PQ_INTEROP_BINDING'])
        libraries={Path(k).name:(k,v) for k,v in pq['inputs_sha256'].items()}
        evidence=root/'interop.json'
        evidence.write_bytes(Path(os.environ['CUM_PQ_COMPATIBILITY_RECORD']).read_bytes())
        crypto.sign(dict(fixture.common,source=str(evidence),destination=str(root/'interop.sig'),identity=str(root/'signer.key')))
        whoami=shutil.which('whoami')
        sid=list(csv.reader(io.StringIO(checked([whoami,'/user','/fo','csv','/nh'],timeout=30,max_output=65536)['stdout'].decode())))[0][1].strip()
        replacements={'REPLACE_NATIVE':os.environ['CUM_PQ_PROJECT_NATIVE'],'REPLACE_OPENSSL':fixture.tool['executable'],
            'REPLACE_JOB':job.as_posix(),'REPLACE_PENDING':(root/'pending').as_posix(),'REPLACE_VAULT':(root/'vault').as_posix(),
            'REPLACE_ORIGINAL':(root/'reference').as_posix(),'REPLACE_TARGET':(root/'target').as_posix(),
            'REPLACE_WHOAMI':whoami,'REPLACE_OWNER_SID':sid,'REPLACE_PROJECT_ID':'disposable-pq-project',
            'REPLACE_RELEASE_ID':'synthetic-pq-release','REPLACE_SIGNER':(root/'signer.key').as_posix(),
            'REPLACE_SIGNER_PUBLIC':(root/'signer.pub').as_posix(),'REPLACE_SIGNER_PIN':digest(root/'signer.der'),
            'REPLACE_PQ_OPENSSL':pq['tool']['executable'],'REPLACE_PQ_CRYPTO_DLL':libraries['libcrypto-3-x64.dll'][0],
            'REPLACE_PQ_CRYPTO_PIN':libraries['libcrypto-3-x64.dll'][1],'REPLACE_PQ_SSL_DLL':libraries['libssl-3-x64.dll'][0],
            'REPLACE_PQ_SSL_PIN':libraries['libssl-3-x64.dll'][1],
            'REPLACE_EMPTY_MODULES':pq['environment']['OPENSSL_MODULES'],
            'REPLACE_INTEROP_EVIDENCE':str(evidence),'REPLACE_INTEROP_SIGNATURE':str(root/'interop.sig')}
        init=bind(load(ROOT/'config/pq-identity-flow.example.json'),replacements)
        rejected=copy.deepcopy(init);rejected['journal']=str(root/'rejected-init.json')
        rejected['bindings']['15']['digest_fields']['libcrypto']=fixture.tool['executable']
        with self.assertRaises(HostError):flow(rejected,1)
        self.assertFalse((root/'pending').exists());self.assertFalse((root/'vault').exists())
        flow(init,1)
        identity=load(root/'vault/identity.json')
        self.assertEqual(identity['recipient_scheme'],SCHEME)
        self.assertIs(identity['post_quantum'],True)
        snapshot=job/'snapshot';snapshot.mkdir()
        (snapshot/'policy.bf').write_bytes(b'# Retained comment\r\n,+.\r\n')
        (snapshot/'binary').write_bytes(bytes(range(256)))
        (snapshot/'empty').mkdir()
        expected=inventory(snapshot);atomic_json(job/'scope.json',expected)
        seal=bind(load(ROOT/'config/pq-project-recovery.example.json'),replacements)
        flow(seal,1)
        java_cms('decrypt',root/'vault/recovery.key.pem',job/'package/capsule.cms',root/'independent.tar')
        self.assertEqual(digest(root/'independent.tar'),digest(job/'originals.tar'))
        self.assertIs(load(job/'package/capsule.json')['post_quantum'],True)
        self.assertFalse(any('key' in p.name for p in (job/'package').iterdir()))
        for path in (snapshot,job/'internal'):
            self.assertTrue(path.resolve().is_relative_to(root.resolve()))
            shutil.rmtree(path)
        (job/'originals.tar').unlink();(job/'internal.tar').unlink();(root/'independent.tar').unlink()
        clone=root/'clone';shutil.copytree(job/'package',clone)
        recover=copy.deepcopy(seal);recover['journal']=str(root/'recover.json')
        for operand in recover['bindings'].values():
            for field in ('source','signature'):
                if field in operand:operand[field]=operand[field].replace((job/'package').as_posix(),clone.as_posix())
            for field in ('digest_fields',):
                if field in operand:
                    operand[field]={k:v.replace((job/'package').as_posix(),clone.as_posix()) for k,v in operand[field].items()}
        flow(recover,2)
        verify_tree(job/'recovered',expected)
        for label,changes in [('project',{'project_id':'wrong'}),('scope',{'post_quantum':False})]:
            bad=copy.deepcopy(recover);bad['journal']=str(root/(label+'.json'))
            bad['bindings']['22']['fields'].update(changes)
            with patch('host.bytehost.crypto.envelope') as decrypt,self.assertRaises(HostError):flow(bad,2)
            decrypt.assert_not_called()
