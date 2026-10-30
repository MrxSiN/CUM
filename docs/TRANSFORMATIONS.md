# Transformation contracts — source draft

Scoped Windows native BF/JVM fixtures now pass as recorded in `VERIFICATION.md`.
The four-transaction graph regression now passes native edit/verify and finite
behavior checks. The semantic arguments below describe intended
domains; they are not universal proofs or production release acceptance.

## Single-cell worker

`transform.bf` accepts arithmetic, I/O and balanced loops at cell zero. It filters
ignored bytes and rejects pointer commands, including in skipped loops. BBC
independently validates brackets. Zero-initialized wrapping bytes, EOF zero and
sufficient scratch cells are required target semantics.

| Profile | Representative increment | Scratch |
|---|---|---|
| FAST | `[->+<]>+[-<+>]<` | cell 1 |
| CAMOUFLAGE, selector zero | `>+<[->+<]>[-<+>]<` | cell 1 |
| CAMOUFLAGE, selector nonzero | `[->-<]>-[-<->]<` | cell 1 |
| MAXIMUM | `>>+<<[->>+<<]>>[-<<+>>]<<` | cell 2 |
| PERFORMANCE | `+` | none |

Decrement uses the opposite adjustment. Positive transfer maps `(x,0)` to `(0,x)`,
adjusts and transfers back. Negative transfer uses `-x` and the opposite adjustment.
Each transfer terminates in the byte domain and restores zero scratch. Original
I/O ordering and loop tests remain. Profile names imply no measured resistance.

## Multi-cell layout

`machines/bf_layout.bf` uses the event-machine protocol. BF chooses every emitted
instruction, register update and stack operation. Data cells are spaced by two,
or three for MAXIMUM, with zero scratch between them. PERFORMANCE relocates data
with direct arithmetic. Static pointer tracking requires every loop to return
to its entry position, including nested loops. Negative movement, drifting loops
and mismatched brackets reject; some valid BF programs are deliberately unsupported.

No historic BBC tape constant is embedded in example jobs. A nonnegative
`integer_limit` is an explicit operation bound derived from a verified target or
owner policy; null removes that integer bound. Null does not certify an unbounded
target or bypass physical resource exhaustion and compiler failure. Target tape,
scratch extent, pointer errors and finite supported domain need actual evidence.

## Virtualization and JVM modules

`bf_virtualize.bf` accepts linear single-cell arithmetic and I/O and emits a public
BF dispatcher and instruction representation. Pointer/loop inputs reject. This
optional MAXIMUM technique needs independent structural and overhead measurements.

Java/Kotlin BF match kernels recognize only the `tests/projects/` module forms.
BF emission replaces integer addition with carry decomposition or an iterative
carry state machine under JVM wrapping-integer semantics. Public class/object
and method interfaces remain. Arbitrary language/framework behavior is unsupported.
Boundary/random arithmetic, compiler, bytecode, behavior and recovery evidence
are required separately.

## Graph recipe

BF proposes `a + b = a - (0 - b)` in the same wrapping type through a real
`XAXEDIT1` carrier. Queried identities, operation/type/arity preconditions,
expected root, native edit/verify, dependency resolve, rebuild and development-ready
restoration are mandatory. Unsupported nodes/types/backends reject. This is
separate from BF compiled through XAX and not universal graph protection.

The recipe request is four bytes: profile, observed operation, graph kind, stage.
Stages 0/1 insert zero and negation separately; stage 2 changes ADD_WRAP to SUB_WRAP;
stage 3 replaces its RHS. Each carrier contains exactly one mutation, binds the
current root, and must pass native verification before another query/edit. Queries
refresh the changed function by a unique matching interface and fail on ambiguity.
Opaque node indices for inserted values come from earlier query buffers. A ledger
binds all four queries/carriers before expected-digest replacement of the original.
Input must already be an editable canonical build request, not a resolved snapshot.
Exporting the existing request closure is a test-fixture operation, not an adapter
that silently converts unsupported production inputs. Workspace/dependency recovery
still requires its separate development-ready check.

## Structural acceptance

`tests/tools/normalize.py` is an independent analysis tool, never a production
transformer. Checks compare filtered instructions, folded arithmetic/clear-loop
representations and real BBC O1 BFX. JVM/graph checks inspect their appropriate
bytecode/canonical/native structures. Identical representations fail applicable
structural gates. A changed representation alone does not establish practical
reconstruction difficulty. Transfer/carry/dispatcher patterns are recognizable.

Each pass needs independent behavior, input consumption, termination and relevant
error equivalence within its domain, and exact recovery from the same immutable
capture. Finite tests do not prove universal equivalence. General dynamically
moving BF, deeper graph rewrites and advanced AI evaluation are NOT STARTED.
