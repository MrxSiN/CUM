# Transformation contracts — source draft

Scoped Windows native BF/JVM fixtures now pass as recorded in `VERIFICATION.md`.
The four-transaction graph regression now passes native edit/verify and finite
behavior checks. The semantic arguments below describe intended
domains; they are not universal proofs or production release acceptance.

## Annotated input and emitted comments

Whole-line `#` comments require `annotated_filter.bf` before layout; ordinary BF
ignored-byte filtering has different semantics when comments contain commands.
The explicit annotated flow filters, lays out, adds command-free headers and
binds the reports. It does not select a language from a filename. See
[ANNOTATED_BF.md](ANNOTATED_BF.md) for grammar, state and rejection rules.

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

The Android follow-up passed finite cases for nine filtered originals and eight
CAMOUFLAGE outputs. One protected time-window CAMOUFLAGE build declined. Explicit
PERFORMANCE at O1 compiled on Windows/Android, retained a different optimized BFX
and passed ten more device cases; its O0 builds declined. This is a recorded
profile choice for that candidate, not an automatic fallback or an ABI guarantee.

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

The restricted presentation pass adds non-executable BF annotations and encodes
static document text while preserving its rendered meaning. See `PRESENTATION.md`.
Comment changes and document encodings cannot substitute for an executable
structural change, independent behavior checks or exact recovery.

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
Current executed scopes and remaining build/release gates are in
[status](STATUS.md) and [Android readiness](ANDROID_READINESS.md).
# Amended acceptance boundary

The [resistance contract](RESISTANCE.md) supersedes any interpretation that visual
complexity or unequal compiler output establishes AI resistance. CAMOUFLAGE and
MAXIMUM now require measured matched reconstruction evaluation before release;
FAST/PERFORMANCE do too whenever that resistance is claimed. Current passes are
not accepted against this requirement. Do not infer protection of the full XAX
host from transformed embedded BF components.

The [owner-collected source-only pilot](RECONSTRUCTION_PILOT.md) exposes the
small `transform.bf` scratch-transfer pass: both supplied protected answers
recover its algorithm despite different optimized BFX. This observation covers
that fixture and pass, not full layout/virtualization or the Android/XAX project.

The optional [live shared-state candidate](SHARED_STATE.md) keeps a modular mask
live across operations and changes it at I/O through an input-dependent nonlinear
transition. It supports restricted single-cell loops and restores physical state
at the end. This is an experimental BF pass, not accepted AI resistance. The
owner waived AI-cost comparisons; reconstruction outcomes and application budgets
remain separate requirements.

The [independent polynomial audit](READINESS_AUDIT.md) subsequently reconstructed
the tested shared-state arithmetic variants. Distinct executable state and
nonlinear mask updates did not prevent recovery in that scope. A multi-cell
candidate and independently reviewed analysis/admission contract remain required
before considering the real Android project.
