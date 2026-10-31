"""Test-only generic protocol executor for actual BF kernel sources.

This supplies opaque storage effects, never a source rewrite. It cannot establish
native compilation/execution evidence.
"""
import io
from pathlib import Path

from host.bytehost.machine import _effects, _request
from tests.reference import execute

ROOT = Path(__file__).resolve().parents[1]


def transduce(name, data, profile=2, selector=0, limit=1000000, kernels=None):
    spec = {"profile": profile, "selector": selector, "integer_limit": limit,
            "max_output_bytes": 1048576, "max_storage_bytes": 1048576,
            "max_stack_entries": 1000000}
    state = {"opaque": "00" * 16, "integers": ["0"] * 4,
             "stacks": [[] for _ in range(4)], "buffers": [""] * 8}
    output = io.BytesIO()
    languages = {"java_int_module": "java", "kotlin_int_module": "kotlin"}
    for event, byte in [(0, 0), *[(1, value) for value in data], (2, 0)]:
        active = name
        for _ in range(8):
            source = (ROOT / "src/machines" / (active + ".bf")).read_bytes()
            response = execute(source, _request(event, byte, spec, state), steps=100000000).output
            if len(response) < 18 or response[0] != 178:
                raise ValueError("malformed BF kernel result")
            if response[-1]:
                raise ValueError(("BF kernel rejected", response[-1]))
            state["opaque"] = response[-17:-1].hex()
            handoff = _effects(response[1:-17], state, output, spec)
            if handoff is None:
                break
            if kernels is not None:
                active = kernels[handoff]
                continue
            language = languages[name]
            active = language + ("_emit" if handoff == 100 else "_match_" + str(handoff - 1))
        else:
            raise ValueError("kernel handoff budget exceeded")
    return output.getvalue(), state
