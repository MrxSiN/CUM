"""Independent wrapping-byte data-flow attack; never emits protected source.

Summarizes pure triangular loops and unrolls known finite loops. Analysis budgets
and a verified safe tape window are explicit operands; unknowns fail closed.
"""
import argparse
import json
from pathlib import Path

from tests.tools.normalize import normalize


class AnalysisUnavailable(ValueError):
    pass


ZERO = ()
ONE = (((), 1),)


class Projection:
    def __init__(self, *, verified_workspace_cells, max_terms, max_degree, max_operations):
        values = (verified_workspace_cells, max_terms, max_degree, max_operations)
        if any(type(value) is not int or value <= 0 for value in values):
            raise AnalysisUnavailable('positive_integer_analysis_operands_required')
        self.cells, self.max_terms, self.max_degree, self.left = values
        self.initial_operations = max_operations
        self.nonce = 0
        self.events = []
        self.inputs = 0

    def charge(self, count=1):
        self.left -= count
        if self.left < 0:
            raise AnalysisUnavailable('operation_budget')

    def poly(self, terms):
        result = tuple(sorted((key, value % 256) for key, value in terms.items() if value % 256))
        if len(result) > self.max_terms:
            raise AnalysisUnavailable('term_budget')
        if any(len(key) > self.max_degree for key, _ in result):
            raise AnalysisUnavailable('degree_budget')
        return result

    def const(self, value):
        return (((), value % 256),) if value % 256 else ZERO

    def add(self, left, right, scale=1):
        self.charge(len(left) + len(right))
        terms = dict(left)
        for key, value in right:
            terms[key] = terms.get(key, 0) + value * scale
        return self.poly(terms)

    def mul(self, left, right):
        self.charge(len(left) * len(right))
        terms = {}
        for a, av in left:
            for b, bv in right:
                if len(a) + len(b) > self.max_degree:
                    raise AnalysisUnavailable('degree_budget')
                key = tuple(sorted(a + b))
                terms[key] = terms.get(key, 0) + av * bv
                if len(terms) > self.max_terms:
                    raise AnalysisUnavailable('term_budget')
        return self.poly(terms)

    def substitute(self, expression, values):
        result = ZERO
        for monomial, coefficient in expression:
            term = self.const(coefficient)
            for variable in monomial:
                term = self.mul(term, values[variable])
            result = self.add(result, term)
        return result

    def inside(self, pointer):
        if not 0 <= pointer < self.cells:
            raise AnalysisUnavailable('outside_verified_workspace')
        return pointer

    def addresses(self, body, pointer):
        found = {pointer}
        for node in body:
            self.charge()
            op = node[0]
            if op in ('right', 'left'):
                pointer = self.inside(pointer + (1 if op == 'right' else -1))
                found.add(pointer)
            elif op == 'affine':
                self.inside(pointer + node[2][0]); self.inside(pointer + node[2][1])
                found.update(pointer + offset for offset, _ in node[1])
            elif op == 'loop':
                nested, end = self.addresses(node[1], pointer)
                if end != pointer:
                    raise AnalysisUnavailable('drifting_loop')
                found.update(nested)
        return found, pointer

    def summarize(self, body, state, pointer):
        touched, end = self.addresses(body, pointer)
        if end != pointer:
            raise AnalysisUnavailable('drifting_loop')
        self.nonce += 1
        names = {cell: 'proof_%d_%d' % (self.nonce, cell) for cell in touched}
        assumptions = {cell for cell in touched if state.get(cell, ZERO) == ZERO}
        # A zero precondition may be used only if one body iteration preserves it.
        while True:
            before = {cell: ZERO if cell in assumptions else (((names[cell],), 1),) for cell in touched}
            after = dict(before)
            self.walk(body, after, pointer, proof=True)
            broken = {cell for cell in assumptions if after.get(cell, ZERO) != ZERO}
            if not broken:
                break
            assumptions -= broken
        deltas = {cell: self.add(after.get(cell, ZERO), before[cell], -1) for cell in touched}
        counter = deltas[pointer]
        if len(counter) != 1 or counter[0][0] or counter[0][1] % 2 == 0:
            raise AnalysisUnavailable('non_triangular_loop')
        invariant_names = {names[cell] for cell in touched if not deltas[cell]}
        for cell, delta in deltas.items():
            if cell != pointer and any(variable not in invariant_names for monomial, _ in delta for variable in monomial):
                raise AnalysisUnavailable('non_triangular_loop')
        substitutions = {names[cell]: state.get(cell, ZERO) for cell in touched}
        iterations = self.mul(state.get(pointer, ZERO), self.const(-pow(counter[0][1], -1, 256)))
        updated = {}
        for cell, delta in deltas.items():
            if cell != pointer:
                updated[cell] = self.add(state.get(cell, ZERO), self.mul(iterations, self.substitute(delta, substitutions)))
        state.update(updated)
        state[pointer] = ZERO

    def walk(self, nodes, state, pointer=0, proof=False):
        for node in nodes:
            self.charge()
            op = node[0]
            value = state.get(pointer, ZERO)
            if op == 'add':
                state[pointer] = self.add(value, self.const(node[1]))
            elif op in ('right', 'left'):
                pointer = self.inside(pointer + (1 if op == 'right' else -1))
            elif op == 'clear':
                state[pointer] = ZERO
            elif op == 'affine':
                if value:
                    self.inside(pointer + node[2][0]); self.inside(pointer + node[2][1])
                    for offset, coefficient in node[1]:
                        dest = pointer + offset
                        state[dest] = self.add(state.get(dest, ZERO), self.mul(value, self.const(coefficient)))
                    state[pointer] = ZERO
            elif op in ('input', 'output'):
                if proof:
                    raise AnalysisUnavailable('loop_io')
                if op == 'input':
                    variable = 'input_%d' % self.inputs
                    state[pointer] = (((variable,), 1),)
                    self.events.append(['read', self.inputs]); self.inputs += 1
                else:
                    self.events.append(['write', [[list(term), coefficient] for term, coefficient in value]])
            elif op == 'loop':
                if not value:
                    continue
                constant = len(value) == 1 and not value[0][0]
                if constant and not proof:
                    seen = set()
                    while state.get(pointer, ZERO):
                        current = state[pointer]
                        if len(current) != 1 or current[0][0]:
                            raise AnalysisUnavailable('input_dependent_io_loop')
                        signature = (pointer, tuple(sorted(state.items())), self.inputs)
                        if signature in seen:
                            raise AnalysisUnavailable('nonterminating_loop')
                        seen.add(signature)
                        position = self.walk(node[1], state, pointer)
                        if position != pointer:
                            raise AnalysisUnavailable('drifting_loop')
                else:
                    self.summarize(node[1], state, pointer)
        return pointer


def observable_projection(source, *, verified_workspace_cells, max_terms, max_degree, max_operations):
    analysis = Projection(verified_workspace_cells=verified_workspace_cells, max_terms=max_terms,
                          max_degree=max_degree, max_operations=max_operations)
    state = {}
    analysis.charge(len(source))
    try:
        nodes = normalize(source)
    except ValueError as exc:
        raise AnalysisUnavailable('invalid_brackets') from exc
    try:
        pointer = analysis.walk(nodes, state)
    except RecursionError as exc:
        raise AnalysisUnavailable('analysis_recursion_resource') from exc
    return {'format': 'WRAPPING-BYTE-OBSERVABLE-PROJECTION', 'status': 'PASS',
            'events': analysis.events, 'reads': analysis.inputs,
            'final_pointer': pointer,
            'final_cells': {str(cell): [[list(term), coefficient] for term, coefficient in value]
                            for cell, value in sorted(state.items()) if value},
            'operations': analysis.initial_operations - analysis.left,
            'scope': 'Zero-initialized wrapping 8-bit cells, EOF-zero reads, declared verified workspace; only fully summarized finite operations.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Independent polynomial BF data-flow reconstruction')
    parser.add_argument('source'); parser.add_argument('binding')
    args = parser.parse_args()
    try:
        options = json.loads(Path(args.binding).read_text(encoding='utf-8'))
        print(json.dumps(observable_projection(Path(args.source).read_bytes(), **options)))
    except AnalysisUnavailable as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)}))
        raise SystemExit(2)
