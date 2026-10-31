"""Optional standards-library interoperability candidate, never PQ release approval."""
import os
from pathlib import Path
import unittest

from host.bytehost.errors import HostError
from host.bytehost.process import checked
from host.bytehost.storage import digest
from host.bytehost.trusted import invoke


def java_cms(*args):
    dependencies=[Path(value) for value in os.environ['CUM_PQ_CLASSPATH'].split(os.pathsep)]
    if not all(path.is_file() for path in dependencies):
        raise ValueError('Use pinned JARs, not open class directories')
    return invoke({'tool':{'executable':os.environ['CUM_PQ_JAVA'],'sha256':digest(os.environ['CUM_PQ_JAVA'])},
        'argv':['-Xmx256m','-cp',os.environ['CUM_PQ_CLASSPATH'],'StandardCms',*map(str,args)],
        'inputs_sha256':{str(path):digest(path) for path in dependencies},
        'clear_environment_prefixes':['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH'],
        'timeout_seconds':60,'max_output_bytes':1048576})


@unittest.skipUnless(os.environ.get('CUM_PQ_CLASSPATH') and os.environ.get('BYTEHOST_CRYPTO_TESTS')=='1',
                     'Pinned Bouncy Castle/JVM candidate must be built explicitly')
class PqCmsTests(unittest.TestCase):
    def test_authentication_and_openssl_key_interchange(self):
        from tests.test_crypto import CryptoTests
        fixture=CryptoTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        root=fixture.root
        for label in ('owner','wrong'):
            fixture.call('genpkey','-algorithm','ML-KEM-1024','-out',str(root/(label+'.key')))
            fixture.call('pkey','-in',str(root/(label+'.key')),'-pubout','-out',str(root/(label+'.pub')))
        fixture.call('x509','-new','-force_pubkey',str(root/'owner.pub'),'-CA',str(root/'recipient.crt'),'-CAkey',str(root/'recipient.key'),
            '-set_serial','1','-subj','/CN=DisposableKem','-days','1','-out',str(root/'owner.crt'))
        run=java_cms
        for index,data in enumerate((b'',bytes(range(256))+b'\r\n')):
            source=root/f'input-{index}';source.write_bytes(data)
            capsule=root/f'capsule-{index}';output=root/f'output-{index}'
            run('encrypt',root/'owner.crt',source,capsule)
            run('decrypt',root/'owner.key',capsule,output)
            self.assertEqual(output.read_bytes(),data)
            for mutation,body in [('truncated',capsule.read_bytes()[:-1]),
                                  ('corrupt',capsule.read_bytes()[:-1]+bytes([capsule.read_bytes()[-1]^1]))]:
                changed=root/f'{mutation}-{index}';changed.write_bytes(body)
                rejected=root/f'rejected-{mutation}-{index}'
                with self.assertRaises(HostError):run('decrypt',root/'owner.key',changed,rejected)
                self.assertFalse(rejected.exists())
            with self.assertRaises(HostError):run('decrypt',root/'wrong.key',capsule,root/f'wrong-{index}')
            self.assertFalse((root/f'wrong-{index}').exists())
            with self.assertRaises(HostError):run('decrypt',root/'owner.key',capsule,output)
            self.assertEqual(output.read_bytes(),data)
