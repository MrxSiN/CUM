"""Independent OpenSSL/BC full CMS checks using disposable public synthetic data."""
import copy
import os
from pathlib import Path
import tempfile
import unittest

from host.bytehost.crypto import _temporary_output, authenticated_cms
from host.bytehost.errors import HostError
from host.bytehost.storage import atomic_json, load
from host.bytehost.trusted import invoke
from tests.test_pq_cms import java_cms


@unittest.skipUnless(os.environ.get('CUM_PQ_INTEROP_BINDING') and os.environ.get('CUM_PQ_CLASSPATH')
                     and os.environ.get('BYTEHOST_CRYPTO_TESTS')=='1',
                     'Explicit authenticated/pinned independent CMS backend required')
class PqInteropTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='disposable-pq-interop-')
        self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name)
        self.binding=load(os.environ['CUM_PQ_INTEROP_BINDING'])
        self.receipts=[]
        self.ssl('genpkey','-algorithm','ED25519','-out',self.root/'ca.key')
        self.ssl('req','-new','-x509','-key',self.root/'ca.key','-subj','/CN=DisposableCMSCA',
                 '-days','1','-out',self.root/'ca.crt')
        for name in ('owner','other'):
            self.identity(name,'ML-KEM-1024')

    def ssl(self,*args):
        spec=copy.deepcopy(self.binding)
        spec['argv']=list(map(str,args))
        spec.pop('report',None)
        receipt=invoke(spec)
        self.receipts.append({'operation':str(args[0]),'wall_seconds':receipt['wall_seconds'],
                              'resources':receipt['resources']})
        return receipt

    def identity(self,name,algorithm):
        self.ssl('genpkey','-algorithm',algorithm,'-out',self.root/(name+'.key'))
        self.ssl('pkey','-in',self.root/(name+'.key'),'-pubout','-out',self.root/(name+'.pub'))
        self.ssl('x509','-new','-force_pubkey',self.root/(name+'.pub'),'-CA',self.root/'ca.crt',
                 '-CAkey',self.root/'ca.key','-set_serial',str(len(self.receipts)),
                 '-subj','/CN=DisposableKEMRecipient','-days','1','-out',self.root/(name+'.crt'))

    def encrypt(self,source,output,recipients=('owner',),cipher='-aes-256-gcm'):
        def operation(pending):
            args=['cms','-encrypt','-binary',cipher,'-outform','DER','-in',str(source),'-out',pending,
                  '-aes256-wrap']
            for name in recipients:
                args.extend(['-recip',str(self.root/(name+'.crt')),'-recip_kdf','HKDF-SHA256'])
            self.ssl(*args)
            authenticated_cms(pending)
        _temporary_output(output,operation)

    def decrypt(self,source,output,name='owner'):
        authenticated_cms(source)
        _temporary_output(output,lambda pending:self.ssl('cms','-decrypt','-binary','-inform','DER',
            '-in',source,'-recip',self.root/(name+'.crt'),'-inkey',self.root/(name+'.key'),'-out',pending))

    def test_bidirectional_full_cms_and_fresh_envelopes(self):
        payloads=(b'',bytes(range(256))+b'\x00\r\n',bytes(range(256))*4096)
        for index,data in enumerate(payloads):
            source=self.root/f'input-{index}';source.write_bytes(data)
            java_capsule=self.root/f'java-{index}.cms'
            java_cms('encrypt',self.root/'owner.crt',source,java_capsule)
            recovered=self.root/f'openssl-restored-{index}'
            self.decrypt(java_capsule,recovered)
            self.assertEqual(recovered.read_bytes(),data)
            openssl_capsule=self.root/f'openssl-{index}.cms'
            self.encrypt(source,openssl_capsule)
            recovered=self.root/f'java-restored-{index}'
            java_cms('decrypt',self.root/'owner.key',openssl_capsule,recovered)
            self.assertEqual(recovered.read_bytes(),data)
            second=self.root/f'openssl-second-{index}.cms'
            self.encrypt(source,second)
            self.assertNotEqual(openssl_capsule.read_bytes(),second.read_bytes())
        if os.environ.get('CUM_PQ_INTEROP_REPORT'):
            atomic_json(os.environ['CUM_PQ_INTEROP_REPORT'],{'format':'CROSS-LIBRARY-CMS-TEST',
                'status':'PASS','directions':['BC encrypt / OpenSSL decrypt','OpenSSL encrypt / BC decrypt'],
                'payload_bytes':list(map(len,payloads)),'fresh_ciphertexts_differ':True,'receipts':self.receipts,
                'production_release_accepted':False})

    def test_cross_library_wrong_identity_and_hostile_capsules_never_publish(self):
        source=self.root/'input';source.write_bytes(bytes(range(256)))
        for producer in ('java','openssl'):
            capsule=self.root/(producer+'.cms')
            if producer=='java':java_cms('encrypt',self.root/'owner.crt',source,capsule)
            else:self.encrypt(source,capsule)
            body=capsule.read_bytes()
            for label,content in [('wrong',body),('truncated',body[:-1]),
                                  ('corrupt',body[:-1]+bytes([body[-1]^1]))]:
                changed=self.root/(producer+'-'+label+'.cms');changed.write_bytes(content)
                output=self.root/(producer+'-'+label+'-plaintext')
                identity='other' if label=='wrong' else 'owner'
                with self.subTest(producer=producer,mutation=label):
                    with self.assertRaises(HostError):
                        if producer=='java':self.decrypt(changed,output,identity)
                        else:java_cms('decrypt',self.root/(identity+'.key'),changed,output)
                    self.assertFalse(output.exists())
            existing=self.root/(producer+'-existing');existing.write_bytes(b'KEEP')
            with self.assertRaises((HostError,FileExistsError)):
                if producer=='java':self.decrypt(capsule,existing)
                else:java_cms('decrypt',self.root/'owner.key',capsule,existing)
            self.assertEqual(existing.read_bytes(),b'KEEP')
        self.assertFalse(list(self.root.glob('.pending-*')))

    def test_multiple_recipients_and_suite_rejection(self):
        source=self.root/'input';source.write_bytes(b'Synthetic multi-recipient fixture')
        capsule=self.root/'multi.cms';self.encrypt(source,capsule,('owner','other'))
        for name in ('owner','other'):
            output=self.root/(name+'-java')
            java_cms('decrypt',self.root/(name+'.key'),capsule,output)
            self.assertEqual(output.read_bytes(),source.read_bytes())
        for label,recipients,cipher in [('aes128',('owner',),'-aes-128-gcm'),
                                       ('kem768',('weak',),'-aes-256-gcm')]:
            if label=='kem768':self.identity('weak','ML-KEM-768')
            changed=self.root/(label+'.cms');self.encrypt(source,changed,recipients,cipher)
            output=self.root/(label+'-plaintext')
            with self.assertRaises(HostError):java_cms('decrypt',self.root/'owner.key',changed,output)
            self.assertFalse(output.exists())
