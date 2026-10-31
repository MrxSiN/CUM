"""Shared-state BF semantics and explicit workflow checks, independent of its emitter."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from host.bytehost.errors import HostError
from host.bytehost.machine import transduce as native_transduce, _request
from host.bytehost.process import checked
from host.bytehost.storage import atomic_json, digest, inventory, load
from host.bytehost.vm import flow
from tests.machine_reference import transduce as reference_transduce
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]
SHARE_KERNELS = {201 + i: 'bf_share_' + name for i, name in
                 enumerate(('start', 'input', 'output', 'open', 'close', 'finish'))}


def transduce(name, data, profile=2, selector=0, limit=1000000):
    return reference_transduce(name, data, profile, selector, limit, kernels=SHARE_KERNELS)


class SharedStateTests(unittest.TestCase):
    def test_outputs_state_consumption_and_seed_diversification(self):
        programs = (b'', b'+.,-.,+.', b',[.-]', b',[[.-]]', b'+++[-].')
        for source in programs:
            outputs = []
            for seed in (0, 17, 255):
                protected, state = transduce('bf_share', source, 2, seed)
                outputs.append(protected)
                self.assertEqual(state['opaque'], '02' + '00' * 15)
                inputs = (b'', b'\x00', b'\x01', b'\x03') if b'[' in source else (b'', b'\x00', b'\x01\xff', b'\xff\x00')
                for data in inputs:
                    before = execute(source, data)
                    after = execute(protected, data, steps=100000000)
                    self.assertEqual(after.output, before.output)
                    self.assertEqual(after.consumed, before.consumed)
                    self.assertEqual(after.pointer, 0)
                    self.assertEqual(after.tape[0], before.tape[0])
                    self.assertFalse(any(after.tape[1:]))
            self.assertEqual(len(set(outputs)), 3)

    def test_runtime_key_is_live_and_input_dependent(self):
        protected, _ = transduce('bf_share', b',.', 2, 17)
        commands = bytes(c for c in protected if c in b'><+-.,[]')
        through_output = commands[:commands.index(b'.') + 1]
        keys = []
        for value in (0, 1, 127, 255):
            state = execute(through_output, bytes([value]), steps=100000000)
            self.assertEqual(state.output, bytes([value]))
            self.assertEqual((state.tape[0] + state.tape[1]) % 256, value)
            self.assertEqual(state.tape[1], (17 * 17 + value + 1) % 256)
            keys.append(state.tape[1])
        self.assertEqual(len(set(keys)), 4)

    def test_unsupported_source_profiles_and_depth_budget_are_rejected(self):
        for source in (b'<', b'>', b'[>]', b'[', b']', b',.[', b'[]]'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                transduce('bf_share', source)
        for profile in (0, 1, 3, 4, 255):
            with self.assertRaises(ValueError):
                transduce('bf_share', b',.', profile)
        with self.assertRaises(ValueError):
            transduce('bf_share', b'[[.]]', 2, limit=1)

    def test_malformed_event_and_lifecycle_rejected(self):
        source = (ROOT / 'src/machines/bf_share.bf').read_bytes()
        spec = {'profile': 2, 'selector': 0, 'integer_limit': None}
        state = {'opaque': '00' * 16, 'integers': ['0'] * 4, 'stacks': [[] for _ in range(4)]}
        valid = _request(0, 0, spec, state)
        for index, value in ((0, 0), (1, 3), (3, 1), (5, 2), (6, 1), (10, 1), (11, 1)):
            request = bytearray(valid); request[index] = value
            with self.subTest(index=index):
                self.assertNotEqual(execute(source, request, steps=100000000).output[-1], 0)
        self.assertNotEqual(execute(source, _request(1, 43, spec, state), steps=100000000).output[-1], 0)
        for number, name in SHARE_KERNELS.items():
            action = number - 200
            opaque = bytes([2 if action == 6 else 1, action % 6 + 1] + [0] * 14)
            state['opaque'] = opaque.hex()
            helper = (ROOT / 'src/machines' / (name + '.bf')).read_bytes()
            self.assertNotEqual(execute(helper, _request(1, 44, spec, state), steps=100000000).output[-1], 0)

    def test_example_reuses_bf_filter_machine_presentation_flow(self):
        spec = load(ROOT / 'config/share-flow.example.json')
        self.assertEqual(spec['planner']['executable'].split('/')[-1], 'annotated_flow.exe')
        self.assertTrue(spec['bindings']['1']['machine']['worker']['executable'].endswith('/bf_share.exe'))
        self.assertEqual(spec['bindings']['1']['machine']['profile'], 2)
        self.assertEqual(set(spec['bindings']['1']['machine']['kernels']), {str(k) for k in SHARE_KERNELS})
        source = (ROOT / 'src/annotated_flow.bf').read_bytes()
        self.assertEqual(execute(source, b'\x01\x02').output, bytes([9, 5, 26, 1, 9, 2, 12, 4, 0]))
        criteria = load(ROOT / 'config/resistance-criteria.example.json')
        self.assertNotIn('minimum_protected_to_baseline_cost_increase', criteria['predeclared_thresholds'])
        self.assertEqual(set(criteria['budgets_per_arm']), {'attempts', 'messages_per_attempt', 'oracle_queries', 'context_bytes'})


@unittest.skipUnless(os.environ.get('CUM_SHARE_NATIVE'), 'Fresh native shared-state and workflow workers required')
class SharedStateNativeTests(unittest.TestCase):
    def machine(self, root, name, source, seed=17):
        path = Path(os.environ['CUM_SHARE_NATIVE']) / 'bf_share.exe'
        kernels = {str(number): {'executable': str(path.parent / (name + '.exe')),
                                'sha256': digest(path.parent / (name + '.exe'))}
                   for number, name in SHARE_KERNELS.items()}
        return {'worker': {'executable': str(path), 'sha256': digest(path)}, 'kernels': kernels, 'profile': 2,
                'selector': seed, 'integer_limit': None, 'state_key': str(root / 'state.key'),
                'max_output_bytes': 1048576, 'max_storage_bytes': 1048576, 'max_stack_entries': 10000,
                'max_response_bytes': 65536, 'max_handoffs_per_event': 1, 'max_operation_seconds': 300,
                'checkpoint_events': 1, 'timeout_seconds': 30, 'source': str(source),
                'destination': str(root / (name + '.bf')), 'journal': str(root / (name + '.json'))}

    def test_native_kernel_parity_interruption_and_resume(self):
        with tempfile.TemporaryDirectory(prefix='shared-native-') as temp:
            root = Path(temp); (root / 'state.key').write_bytes(bytes(range(32)))
            source = root / 'source.bf'; source.write_bytes(b',[.,]')
            spec = self.machine(root, 'resumed', source)
            actual_checked = checked
            calls = 0
            def interrupt(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise HostError('INJECTED', 'Interrupted between committed BF events')
                return actual_checked(*args, **kwargs)
            with patch('host.bytehost.machine.checked', side_effect=interrupt), self.assertRaises(HostError):
                native_transduce(spec)
            self.assertFalse(Path(spec['destination']).exists())
            native_transduce(spec)
            expected, _ = transduce('bf_share', source.read_bytes(), 2, 17)
            self.assertEqual(Path(spec['destination']).read_bytes(), expected)
            with self.assertRaises(HostError):
                native_transduce(spec)

    def test_generated_programs_build_and_run(self):
        compiler = os.environ['CUM_SHARE_BBC']
        records = []
        with tempfile.TemporaryDirectory(prefix='share-program-') as temp:
            root = Path(temp); (root / 'state.key').write_bytes(bytes(range(32)))
            original = root / 'original.bf'; original.write_bytes(b',[.,]')
            baseline = root / 'original.exe'
            checked([compiler, 'compile', 'windows-x86_64', '-O1', str(baseline)], stdin=original.read_bytes(), timeout=120, max_output=1048576)
            for seed in (0, 17, 255):
                spec = self.machine(root, 'protected-' + str(seed), original, seed)
                transformed = native_transduce(spec)
                artifact = root / ('protected-' + str(seed) + '.exe')
                compiled = checked([compiler, 'compile', 'windows-x86_64', '-O1', str(artifact)], stdin=Path(spec['destination']).read_bytes(), timeout=120, max_output=1048576)
                samples = []
                for data in (b'', b'\x00', bytes(range(1, 256)) + b'\x00', b'\xff\x01\x80\x00\xff'):
                    before = checked([str(baseline)], stdin=data, timeout=10, max_output=1048576)
                    after = checked([str(artifact)], stdin=data, timeout=10, max_output=1048576)
                    self.assertEqual(after['stdout'], before['stdout'])
                    self.assertEqual(after['stdin_file_offset'], before['stdin_file_offset'])
                    samples.append({'input_bytes': len(data), 'output_bytes': len(after['stdout']),
                                    'original_process_seconds': before['wall_seconds'], 'protected_process_seconds': after['wall_seconds']})
                records.append({'selector': seed, 'source_bytes': len(original.read_bytes()), 'protected_source_bytes': Path(spec['destination']).stat().st_size,
                                'artifact_bytes': artifact.stat().st_size, 'baseline_artifact_bytes': baseline.stat().st_size,
                                'compile_wall_seconds': compiled['wall_seconds'], 'transformation': transformed,
                                'samples': samples, 'status': 'PASS'})
        if os.environ.get('CUM_SHARE_EVIDENCE'):
            atomic_json(os.environ['CUM_SHARE_EVIDENCE'], {'format': 'SHARED-STATE-NATIVE-CHECK', 'records': records,
                        'scope': 'Three selectors; all 255 nonzero byte values in a stream plus EOF/NUL/early-stop cases. Process times include launch overhead, not application-only overhead.'})

    @unittest.skipUnless(os.environ.get('BYTEHOST_CRYPTO_TESTS') == '1', 'Real-tool authenticated recovery opt-in required')
    def test_full_optional_flow_and_encrypted_exact_snapshot_recovery(self):
        from host.bytehost import archive, crypto
        from tests.test_crypto import CryptoTests
        fixture = CryptoTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        root = fixture.root
        original = root / 'original'; original.mkdir()
        source_bytes = b'# Sample rule > < + [ ]\r\n,[.,]\r\n'
        (original / 'main.bf').write_bytes(source_bytes)
        (original / 'LICENSE').write_bytes(b'Disposable fixture permission\r\n')
        snapshot = root / 'snapshot'
        archive.copy_tree({'source': str(original), 'destination': str(snapshot)})
        atomic_json(root / 'scope.json', inventory(snapshot))
        archive.pack({'root': str(snapshot), 'manifest': str(root / 'scope.json'), 'destination': str(root / 'snapshot.tar'), 'max_archive_bytes': 1048576})
        crypto.envelope(dict(fixture.common, source=str(root / 'snapshot.tar'), destination=str(root / 'capsule.cms'), recipients=[str(root / 'recipient.crt')]))
        candidate = root / 'candidate'
        archive.copy_tree({'source': str(snapshot), 'destination': str(candidate)})
        (original / 'main.bf').write_bytes(b'changed live source')
        (root / 'state.key').write_bytes(bytes(range(32)))
        native = Path(os.environ['CUM_SHARE_NATIVE'])
        spec = load(ROOT / 'config/share-flow.example.json')
        def bind(value):
            if isinstance(value, dict):
                result = {k: bind(v) for k, v in value.items()}
                if 'executable' in result:
                    result['sha256'] = digest(result['executable'])
                return result
            if isinstance(value, list): return [bind(v) for v in value]
            if isinstance(value, str):
                value = value.replace('D:/GitHub/CUM/private/jobs/REPLACE_OPERATION', root.as_posix())
                value = value.replace('D:/GitHub/CUM/build', native.as_posix())
                if value.endswith('/continuation.hmac') or value.endswith('/checkpoint.key'): value = (root / 'state.key').as_posix()
                return value
            return value
        spec = bind(spec)
        spec['bindings']['5']['paths'] = ['main.bf']; spec['bindings']['1']['paths'] = ['main.bf']; spec['bindings']['2']['paths'] = ['main.bf']
        journal = flow(spec, 1, 2)
        self.assertEqual(journal['status'], 'PASS')
        protected = (candidate / 'main.bf').read_bytes()
        for data in (b'', b'\x00', b'\xff\x01\x00'):
            self.assertEqual(execute(protected, data, steps=100000000).output, execute(b',[.,]', data).output)
        self.assertEqual((candidate / 'LICENSE').read_bytes(), (snapshot / 'LICENSE').read_bytes())
        crypto.envelope(dict(fixture.common, source=str(root / 'capsule.cms'), destination=str(root / 'restored.tar'), identity=str(root / 'recipient.key'), certificate=str(root / 'recipient.crt')), decrypt=True)
        archive.extract({'source': str(root / 'restored.tar'), 'destination': str(root / 'restored'), 'limits': {'bytes': 1048576, 'entries': 100, 'metadata_bytes': 65536}})
        self.assertEqual(inventory(root / 'restored'), inventory(snapshot))
        self.assertEqual((root / 'restored/main.bf').read_bytes(), source_bytes)
        self.assertNotEqual((original / 'main.bf').read_bytes(), source_bytes)


if __name__ == '__main__':
    unittest.main()
