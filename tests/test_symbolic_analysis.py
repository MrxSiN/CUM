"""Independent reconstruction and fail-closed admission regression checks."""
import json
from pathlib import Path
import tempfile
import unittest

from host.bytehost.errors import HostError
from tests.native_checks import projection_check, verify
from tests.reference import execute
from tests.test_shared_state import transduce
from tests.tools.symbolic import AnalysisUnavailable, Projection, observable_projection

OPTIONS = dict(verified_workspace_cells=6, max_terms=1024, max_degree=64, max_operations=1000000)


def evaluate(terms, data):
    result = 0
    for variables, coefficient in terms:
        value = coefficient
        for variable in variables:
            index = int(variable.removeprefix('input_'))
            value *= data[index] if index < len(data) else 0
        result += value
    return result % 256


class SymbolicAnalysisTests(unittest.TestCase):
    def project(self, source, **changes):
        return observable_projection(source, **dict(OPTIONS, **changes))

    def test_transfer_and_shared_state_recover_original_formulas(self):
        original = b'+.,-.,+.'
        expected = self.project(original)
        self.assertEqual(expected['reads'], 2)
        for seed in (0, 17, 255):
            protected, _ = transduce('bf_share', original, 2, seed)
            actual = self.project(protected)
            self.assertEqual(actual['events'], expected['events'])
            self.assertEqual(actual['final_cells'], expected['final_cells'])
            for data in (b'', b'\x00', b'\xff', b'\x00\xff', b'\xff\x00', b'AB', b'ABC'):
                predicted = bytes(evaluate(event[1], data) for event in actual['events'] if event[0] == 'write')
                self.assertEqual(predicted, execute(protected, data, steps=100000000).output)
        transfer = b'+[->+<]>[-<+>]<.,>-[ -<+>]<.,>+[-<+>]<.'
        self.assertEqual(self.project(transfer)['events'], expected['events'])

    def test_polynomial_loop_matches_every_byte_and_retains_read_order(self):
        source = b',>+<[->+<]>.'
        record = self.project(source)
        for value in range(256):
            predicted = bytes(evaluate(event[1], bytes([value])) for event in record['events'] if event[0] == 'write')
            self.assertEqual(predicted, execute(source, bytes([value])).output)
        self.assertNotEqual(self.project(b',.')['events'], self.project(b',.,')['events'])
        self.assertNotEqual(self.project(b'.')['events'], self.project(b'+.')['events'])

    def test_known_loops_and_conditional_bounds(self):
        self.assertEqual(len(self.project(b'+++[.-]')['events']), 3)
        for source in (b'[<].', b'[-<+>].'):
            self.assertEqual(self.project(source, verified_workspace_cells=1)['events'], [['write', []]])
        for source in (b'<', b'>', b'+[-<+>]', b'+[>]'):
            with self.subTest(source=source), self.assertRaises(AnalysisUnavailable):
                self.project(source, verified_workspace_cells=1)

    def test_nested_product_uses_invariant_factor(self):
        source = b',>,<[>[->+>+<<]>>[-<<+>>]<<<-]>>.'
        record = self.project(source)
        self.assertEqual(record['events'][-1], ['write', [[['input_0', 'input_1'], 1]]])
        for first in (0, 1, 2, 17, 255):
            for second in (0, 1, 2, 17, 255):
                data = bytes([first, second])
                self.assertEqual(evaluate(record['events'][-1][1], data),
                                 execute(source, data, steps=10000000).output[0])

    def test_unknown_unsafe_and_invalid_programs_block(self):
        for source in (b',[.]', b',[]', b',[--]', b',[>+<]', b'++[>[.]+<-]', b'[', b']'):
            with self.subTest(source=source), self.assertRaises(AnalysisUnavailable):
                self.project(source)

    def test_analysis_operands_and_budgets_fail_closed(self):
        for changes in ({'max_operations': 1}, {'max_terms': False}, {'max_degree': 0},
                        {'verified_workspace_cells': '6'}):
            with self.subTest(changes=changes), self.assertRaises(AnalysisUnavailable):
                self.project(b'+.', **changes)
        projection = Projection(**dict(OPTIONS, max_terms=1))
        with self.assertRaises(AnalysisUnavailable):
            projection.add(((('input_0',), 1),), ((('input_1',), 1),))
        projection = Projection(**dict(OPTIONS, max_degree=1))
        with self.assertRaises(AnalysisUnavailable):
            projection.mul(((('input_0',), 1),), ((('input_1',), 1),))

    def test_recovered_formulas_fail_and_missing_analysis_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original, protected, report = (root / name for name in ('before.bf', 'after.bf', 'report.json'))
            original.write_bytes(b',.')
            protected.write_bytes(b',>[-]<[->+<]>[-<+>]<.')
            spec = {'symbolic_analysis': OPTIONS, 'report': str(report)}
            with self.assertRaises(HostError) as failed:
                projection_check(spec, original, protected)
            self.assertEqual(failed.exception.code, 'NORMALIZATION')
            self.assertEqual(json.loads(report.read_text())['status'], 'FAIL')
            for options in (None, {}, dict(OPTIONS, max_operations=1)):
                spec['symbolic_analysis'] = options
                with self.assertRaises(HostError):
                    projection_check(spec, original, protected)
                self.assertEqual(json.loads(report.read_text())['status'], 'BLOCKED')
            protected.write_bytes(b',[.]')
            spec['symbolic_analysis'] = OPTIONS
            with self.assertRaises(HostError):
                projection_check(spec, original, protected)
            self.assertEqual(json.loads(report.read_text())['status'], 'BLOCKED')

    def test_unequal_formulas_cannot_be_promoted_to_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original, protected, report = (root / name for name in ('before.bf', 'after.bf', 'report.json'))
            original.write_bytes(b',.')
            protected.write_bytes(b',+.')
            with self.assertRaises(HostError) as blocked:
                projection_check({'report': str(report), 'symbolic_analysis': OPTIONS}, original, protected)
            self.assertEqual(blocked.exception.code, 'ANALYSIS_INCONCLUSIVE')
            self.assertEqual(json.loads(report.read_text())['status'], 'BLOCKED')

    def test_early_failure_invalidates_stale_success_record(self):
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / 'report.json'
            report.write_text('{"status":"PASS"}')
            with self.assertRaises(HostError):
                verify({'report': str(report), 'fixtures': []}, 'normalization')
            self.assertEqual(json.loads(report.read_text())['status'], 'BLOCKED')


if __name__ == '__main__':
    unittest.main()
