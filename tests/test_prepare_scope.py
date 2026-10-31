"""Scoped prepare integration; stubbed unrelated services are not release evidence."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from host.bytehost import crypto
from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, canonical, digest, load
from host.bytehost.vm import SERVICES, assert_record, flow
from tests.test_workflow_draft import plan

ROOT=Path(__file__).resolve().parents[1]
PREFLIGHT=[(14,82),(19,83),(14,85),(19,86),(48,84)]


class PrepareScopeTests(unittest.TestCase):
    def test_public_identity_schema_refuses_extra_private_fields(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            record=Path(temporary)/'identity.json'
            spec={'source':str(record),'fields':{'format':'fixture','post_quantum':False},'exact_keys':['format','post_quantum','digests'],
                  'exact_digest_keys':['certificate','spki']}
            value={'format':'fixture','post_quantum':False,'digests':{'certificate':'a','spki':'b'}}
            atomic_json(record,value);assert_record(spec)
            for changed in (dict(value,private_key='must-not-be-exported'),dict(value,post_quantum=0),
                            dict(value,digests=dict(value['digests'],original_source='private-digest'))):
                atomic_json(record,changed,replace=True)
                with self.assertRaises(HostError):assert_record(spec)

    def test_prepare_authenticates_project_before_capture_and_exports_only_public_identity(self):
        for mode in (1,2):
            instructions=plan('cum.bf',bytes([3,mode]))
            start=instructions.index(PREFLIGHT[0])
            self.assertEqual(instructions[start:start+6],PREFLIGHT+[(29,10)])
            end=instructions.index((11,26))
            self.assertEqual(instructions[end-4:end],[(23,i) for i in range(87,91)])
            self.assertLess(instructions.index((24,80)),instructions.index((13,28)))

    def test_all_examples_bind_runtime_context_recipient_and_public_release(self):
        for name in ('public-job','private-vault-job','java-job','kotlin-job','xax-job'):
            job=load(ROOT/'config'/f'{name}.example.json');b=job['bindings']
            self.assertEqual(b['83']['equal_fields']['bindings_sha256']['file'],job['journal'])
            self.assertEqual(b['13']['recipients'],[b['14']['certificate']])
            self.assertEqual(b['14']['identity'],b['34']['identity'])
            self.assertIn('REPLACE_PROJECT',b['14']['identity'])
            self.assertEqual(b['27']['fields']['recovery_contract'],'PROJECT-SCOPED-CMS-RECOVERY')
            self.assertIn('digests',b['86']['exact_keys'])
            for number in ('30','33'):
                self.assertEqual(set(b[number]['files']),set(b['27']['files']))
            self.assertFalse(any('key.pem' in b[str(i)]['source'] for i in range(87,91)))

    def test_new_scoped_decoder_does_not_replace_historical_decoder(self):
        self.assertEqual(plan('clean_recovery.bf',b'\x01\x01'),[(14,1),(15,2),(6,3),(7,4),(4,5),(12,6)])
        self.assertEqual(plan('scoped_clean_recovery.bf',b'\x01\x01'),
                         [(14,1),(15,2),(14,7),(19,8),(19,9),(6,3),(7,4),(4,5),(12,6)])
        for name in ('clean-recovery','clean-recovery-vault'):
            job=load(ROOT/'config'/f'{name}.example.json')
            self.assertTrue(job['planner']['executable'].endswith('/scoped_clean_recovery.exe'))
            self.assertEqual(job['bindings']['9']['fields']['project_id'],job['bindings']['8']['fields']['project_id'])
        bundle=load(ROOT/'config/maintenance.example.json')['bindings']['39']['files']
        self.assertIn('scoped_clean_recovery.exe',[entry['path'] for entry in bundle])

    @unittest.skipUnless(os.environ.get('CUM_PREPARE_NATIVE') and os.environ.get('BYTEHOST_CRYPTO_TESTS')=='1',
                         'Explicit fresh scoped decoder and crypto tools required')
    def test_scoped_decoder_authenticates_fixture_and_recovers_exact_scope(self):
        from tests.test_crypto import CryptoTests
        from host.bytehost import archive
        from host.bytehost.storage import inventory,verify_tree
        from host.bytehost.vm import compose_record,write_inventory
        fixture=CryptoTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        root=fixture.root;release=root/'release';release.mkdir()
        fixture.call('req','-x509','-newkey','rsa:3072','-noenc','-days','1','-subj','/CN=ScopedDecoderFixture',
                     '-keyout',str(root/'project.key'),'-out',str(release/'recovery-recipient.cert.pem'))
        fixture.call('x509','-in',str(release/'recovery-recipient.cert.pem'),'-pubkey','-noout','-out',str(root/'project.pub'))
        fixture.call('pkey','-pubin','-in',str(root/'project.pub'),'-outform','DER','-out',str(release/'recovery-recipient.spki.der'))
        identity_fields={'format':'PROJECT-RECOVERY-IDENTITY','project_id':'decoder-fixture','recipient_scheme':'CLASSICAL-CMS-RSA-3072','post_quantum':False}
        identity_files={'certificate':str(release/'recovery-recipient.cert.pem'),'spki':str(release/'recovery-recipient.spki.der')}
        compose_record({'destination':str(release/'recovery-identity.json'),'fields':identity_fields,'files':identity_files})
        crypto.sign(dict(fixture.common,source=str(release/'recovery-identity.json'),destination=str(release/'recovery-identity.sig'),identity=str(root/'signer.key')))
        snapshot=root/'snapshot';snapshot.mkdir();(snapshot/'fixture.bin').write_bytes(bytes(range(256)))
        expected=inventory(snapshot);atomic_json(root/'scope.json',expected)
        archive.pack({'root':str(snapshot),'manifest':str(root/'scope.json'),'destination':str(root/'archive.tar'),'max_archive_bytes':1048576})
        crypto.envelope(dict(fixture.common,source=str(root/'archive.tar'),destination=str(release/'capsule.cms'),recipients=[str(release/'recovery-recipient.cert.pem')]))
        write_inventory({'root':str(release),'destination':str(release/'inventory.json'),'public':True,
                         'excludes':['inventory.json','release.json','release.sig','capsule.cms']})
        fields={'format':'SIGNED-PROTECTED-TREE-CMS','project_id':'decoder-fixture','release_identity':'unit-decoder',
                'recovery_contract':'PROJECT-SCOPED-CMS-RECOVERY','post_quantum':False,'fixture_only':True,'production_approval':False}
        files={'protected_inventory':str(release/'inventory.json'),'recovery_capsule':str(release/'capsule.cms'),
               'project_identity':str(release/'recovery-identity.json'),'recipient_certificate':str(release/'recovery-recipient.cert.pem')}
        compose_record({'destination':str(release/'release.json'),'fields':fields,'files':files})
        crypto.sign(dict(fixture.common,source=str(release/'release.json'),destination=str(release/'release.sig'),identity=str(root/'signer.key')))
        trust=dict(fixture.common,public_key=str(root/'signer.pub'),trusted_spki_sha256=digest(root/'signer.der'))
        artifact=Path(os.environ['CUM_PREPARE_NATIVE'])/'scoped_clean_recovery.exe'
        bindings={
            '1':dict(trust,source=str(release/'release.json'),signature=str(release/'release.sig')),
            '2':{'root':str(release),'inventory':str(release/'inventory.json'),'binding_record':str(release/'release.json'),'files':files,'expected_fields':fields},
            '3':dict(fixture.common,source=str(release/'capsule.cms'),destination=str(root/'out.tar'),identity=str(root/'project.key'),certificate=str(release/'recovery-recipient.cert.pem')),
            '4':{'source':str(root/'out.tar'),'destination':str(root/'restored'),'manifest':str(root/'restored-scope.json'),'limits':{'bytes':1048576,'entries':100,'metadata_bytes':65536}},
            '5':{'root':str(root/'restored'),'manifest':str(root/'restored-scope.json'),'destination':str(root/'repacked.tar'),'max_archive_bytes':1048576},
            '6':{'destination':str(root/'receipt.json'),'fields':{'format':'SCOPED-DECODER-FIXTURE','status':'PASS'},'files':{}},
            '7':dict(trust,source=str(release/'recovery-identity.json'),signature=str(release/'recovery-identity.sig')),
            '8':{'source':str(release/'recovery-identity.json'),'fields':identity_fields,'digest_fields':identity_files},
            '9':{'source':str(release/'release.json'),'fields':fields,'digest_fields':{k:files[k] for k in ('project_identity','recipient_certificate')}}}
        spec={'planner':{'executable':str(artifact),'sha256':digest(artifact)},'planner_input_bytes':2,
              'planner_timeout_seconds':30,'planner_output_bytes':4096,'journal':str(root/'flow.json'),'bindings':bindings}
        flow(spec,1);verify_tree(root/'restored',expected)
        bad=copy.deepcopy(spec);bad['journal']=str(root/'wrong-project-flow.json');bad['bindings']['9']['fields']=dict(fields,project_id='another-project')
        with patch('host.bytehost.crypto.envelope') as decrypt,self.assertRaises(HostError):flow(bad,1)
        decrypt.assert_not_called()

    @unittest.skipUnless(os.environ.get('CUM_PREPARE_NATIVE') and os.environ.get('BYTEHOST_CRYPTO_TESTS')=='1',
                         'Explicit fresh prepare build and crypto tools required')
    def test_native_prepare_executes_real_identity_preflight_and_rejects_operand_substitution(self):
        from tests.test_crypto import CryptoTests
        fixture=CryptoTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        root=fixture.root;vault=root/'vault';vault.mkdir()
        fixture.call('req','-x509','-newkey','rsa:3072','-noenc','-days','1','-subj','/CN=DisposableProject',
                     '-keyout',str(vault/'recovery.key.pem'),'-out',str(vault/'recovery.cert.pem'))
        fixture.call('x509','-in',str(vault/'recovery.cert.pem'),'-pubkey','-noout','-out',str(vault/'public.pem'))
        fixture.call('pkey','-pubin','-in',str(vault/'public.pem'),'-outform','DER','-out',str(vault/'recipient.spki.der'))
        identity={'format':'PROJECT-RECOVERY-IDENTITY','project_id':'scope-fixture','recipient_scheme':'CLASSICAL-CMS-RSA-3072','post_quantum':False,
                  'digests':{'certificate':digest(vault/'recovery.cert.pem'),'spki':digest(vault/'recipient.spki.der')}}
        atomic_json(vault/'identity.json',identity)
        signing=dict(fixture.common,identity=str(root/'signer.key'))
        crypto.sign(dict(signing,source=str(vault/'identity.json'),destination=str(vault/'identity.sig')))
        text=json.dumps(load(ROOT/'config/public-job.example.json'))
        replacements={
            'D:/GitHub/CUM/private/jobs/REPLACE_OPERATION':root.as_posix(),
            'D:/GitHub/CUM/private/identities/REPLACE_PROJECT':vault.as_posix(),'REPLACE_PROJECT':'scope-fixture'}
        for before,after in sorted(replacements.items(),key=lambda item:-len(item[0])):text=text.replace(before,after)
        job=json.loads(text)
        native=Path(os.environ['CUM_PREPARE_NATIVE'])/'cum.exe'
        job['planner']={'executable':str(native),'sha256':digest(native)}
        b=job['bindings']
        trust=dict(fixture.common,public_key=str(root/'signer.pub'),trusted_spki_sha256=digest(root/'signer.der'))
        for number in ('82','85'):
            b[number].update(trust)
        b['84']={'disjoint_trees':[[str(vault),str(root/'public')],[str(vault),str(root/'reference')]]}
        for number,binding in b.items():binding['_test_operand']=int(number)
        atomic_json(root/'job.json',job)
        context=dict(b['83']['fields'],job_sha256=digest(root/'job.json'),project_identity_sha256=digest(vault/'identity.json'),
                     recipient_certificate_sha256=digest(vault/'recovery.cert.pem'))
        context.update(bindings_sha256=hashlib.sha256(canonical(b)).hexdigest(),planner_sha256=digest(native),request_hex='0301')
        for key,obs in b['83']['equal_fields'].items():
            if key in context:continue
            value=job
            for field in obs['fields']:value=value[field]
            context[key]=value
        atomic_json(root/'project-prepare-context.json',context)
        crypto.sign(dict(signing,source=str(root/'project-prepare-context.json'),destination=str(root/'project-prepare-context.sig')))
        reached=[]
        def service(opcode,binding):
            number=binding['_test_operand']
            if number==10:
                reached.append('capture');raise HostError('PROBE_STOP','Stop before any project capture')
        # Retain the actual service references while routing unrelated operations to stubs.
        originals=dict(SERVICES)
        def route(opcode,binding):
            if binding['_test_operand'] in (82,83,84,85,86):return originals[opcode](binding)
            return service(opcode,binding)
        wrappers={opcode:(lambda binding,op=opcode:route(op,binding)) for opcode in SERVICES}
        with patch.dict(SERVICES,wrappers):
            with self.assertRaises(HostError) as stopped:flow(job,3)
        self.assertEqual(stopped.exception.code,'PROBE_STOP');self.assertEqual(reached,['capture'])
        Path(job['journal']).unlink();reached.clear()
        bad=copy.deepcopy(job);bad['bindings']['13']['recipients']=[str(root/'wrong.crt')]
        with patch.dict(SERVICES,wrappers):
            with self.assertRaises(HostError) as rejected:flow(bad,3)
        self.assertEqual(rejected.exception.code,'REVIEW_BINDING');self.assertFalse(reached)
