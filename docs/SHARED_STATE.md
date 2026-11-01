# Experimental live shared-state BF pass

The [resistance audit](READINESS_AUDIT.md) recovered the public arithmetic
fixture for selectors 17 and 255 with an independent polynomial attack. Both
reconstructions matched 65,809 reference cases. This is a confirmed scoped
resistance failure; the earlier behavior/recovery results below remain valid.

PARTIAL — the BF implementation, optional workflow and scoped tests are executed.
Ten native components compiled, generated applications ran, and encrypted exact
snapshot recovery passed. This pass has no accepted AI-resistance result.

The owner excluded AI-cost accounting on 2026-10-31. Reconstruction acceptance
now uses predeclared algorithm-extraction and independent functional-reimplementation
outcomes under matched opportunity limits. Monetary/token/latency/compute cost
comparisons are not required. Transformation/build/runtime/memory budgets remain.
Historical pilot evidence retains the criteria used when it was collected.

## Purpose and scope

The scratch-transfer pilot exposed a pass that returned to a plain accumulator
after each operation. `src/machines/bf_share.bf` instead emits a program whose
logical byte remains represented by two live modular shares across operations.
At input/output boundaries its mask changes through a nonlinear recurrence that
depends on the old mask and current logical value. These are executable state
and dependency changes, not dead padding or opcode renaming.

The explicit candidate accepts only CAMOUFLAGE profile 2 and a recorded 8-bit
selector. It supports single-cell arithmetic, input/output and balanced loops.
Both pointer instructions reject, even inside skipped loops. Generic opaque
integer depth tracks nesting without an 8-bit depth ceiling; configured depth,
output, storage and time budgets remain explicit. Ordinary ignored bytes are
filtered as in classic BF. Whole-line annotated inputs first pass through the
existing annotation-aware BF filter.

This is a separate experimental option. Existing production/default layout and
virtualization routes are unchanged; their prior evidence is not transferred to
this pass. Native Android/JNI/ABI, multi-cell projects, arbitrary pointer motion,
full prepared release, different-host recovery and AI resistance are unaccepted
for this candidate.

## Runtime invariants

The target must have verified zero-initialized wrapping 8-bit cells, EOF-zero
input and at least six accessible cells. A smaller target is outside the admitted
domain, not a promise of identical tape-boundary errors. The runtime pointer is
at cell zero between source operations. The physical representation is:

| Cells | Meaning at source-operation boundaries |
|---|---|
| 0, 1 | shares A and K; logical value x = (A + K) mod 256 |
| 2–5 | zero temporary workspace |

With recorded selector s, initialization sets K=s and A=-s mod 256, representing
logical zero. Source `+`/`-` adjusts A. Input reads raw x into workspace with EOF
zero and discards the previous logical value. Output reconstructs x in workspace
and emits exactly one byte. After each input/output, the runtime sets:

`K_new = (K_old * K_old + x + 1) mod 256`

`A_new = (x - K_new) mod 256`

Temporary values are cleared and K remains live. Every helper loop terminates
in the wrapping-byte domain. Runtime work can be substantial: the multiplication
uses bounded repeated additions. It must meet an actual application's budgets
before use; no zero-overhead or resistance benefit is presumed.

Loop tests reconstruct x without changing A or K. The opening condition clears
its temporary only when entering; the closing condition reconstructs the next
logical test. Nested loops preserve the same invariant. Finalization materializes
logical x in cell zero, clears K/workspace and returns the pointer to zero.
Therefore output ordering, consumed-input count, EOF behavior, loop termination
and the original single-cell final tape are preserved within the admitted domain.
Compiler failures and configured resource exhaustion remain separate rejection
conditions. Finite differential checks supplement these invariants.

## Transformer and workflow boundary

The generic host supplies the existing fixed 26-byte event record, integer facts,
opaque state storage and effect execution. BF recognizes source commands, chooses
all emitted bytes and depth operations, validates profile/lifecycle, and emits the
178-tagged response. Opaque byte zero records not-started/active/finished as 0/1/2.
Opaque byte one selects a pending emitter only during a handoff and is zero at
committed event boundaries; the other fourteen bytes are reserved zero.
The controller uses existing generic handoffs 201–206 to pinned BF start, input,
output, loop-open, loop-close and finish emitters. Invalid lifecycle or metadata
reject. HMAC checkpoints and atomic publication are existing generic services.

`config/share-flow.example.json` reuses native `annotated_flow.bf` with request
(1,2): annotation filtering, new machine, BF comment presentation, mapping record.
After independently binding compiler/worker identities, capacities, captured
source and controlled destinations, run:

```powershell
python -m host.bytehost flow REVIEWED_SHARE_BINDING.json --command 1 --mode 2
```

This is a functioning optional transformation flow, not a release-acceptance
shortcut. Derive its staged candidate from the immutable snapshot and retain that
same snapshot for authenticated exact recovery. The example has deliberately
invalid pins. The build example includes the controller and its six BF emitters. Main prepare and
publication still require the existing semantic, normalization, legal, signing,
recovery, performance and applicable reconstruction gates. No host source-language
parser or CUM transformation was added.

## Independent checks and limits

`tests/test_shared_state.py` drafts semantic/final-state checks, input-dependent
live-mask observations, malformed transport/lifecycle rejection, unsupported
profiles/pointers/brackets/depth budgets, native/reference kernel parity,
interrupted checkpoint resumption, native builds across three selectors, all
nonzero byte values in a stream plus NUL/EOF/early-stop cases, and a complete
optional filter/share/comment flow with authenticated encrypted exact-snapshot
recovery after live source changes. Native and real-crypto checks require explicit
opt-ins, and cannot be counted as executed until their results exist.

## Executed checkpoint — 2026-10-31

All eight new shared-state test methods passed (five reference checks and three
native integrations), plus the pure-eight-command source check. Six emitters and
their controller compiled at O1, along with three fresh supporting workers.
The resulting program bytes match the unsplit BF implementation in nine source/
selector comparisons. Interruption/resume and completed-checkpoint replay rejection
passed with native kernels. The explicit four-operation BF flow ran filtering,
shared-state emission, comments and mapping. Its CMS-authenticated snapshot
restored original comments/CRLF/license exactly after the live tree was changed.
This is an encrypted snapshot test, not a signed production release.

Generated stream programs for selectors 0,17,255 compiled and passed twelve paired
native comparisons, including all 255 nonzero byte values in a stream, NUL/EOF and
early-stop suffixes. Native input file offsets agreed. Three follow-up programs
(the public arithmetic baseline and two shared-state selectors) also compiled,
passed 27 direct reference comparisons and emitted actual BBC O1 BFX for analysis.
The affected regression passed 19 of 21 tests; two unchanged native-policy opt-ins
were skipped. Application-only performance and AI resistance are not inferred.

The initial monolithic BF emitter hit the compiler's source resource check.
Compacting it preserved all 36 tested event responses but its native backend still
declined. Splitting through existing generic BF handoffs resolved compilation.
Both rejection records remain; neither compiler was edited.

Measured costs are substantial on the five-byte stream fixture: source grew to
978–1488 bytes and native artifacts to 20,480–20,992 bytes versus 8,192. Reported
process times include launch overhead. No application budget acceptance or
resistance benefit is claimed from those measurements. AI-cost comparisons are
excluded as instructed by the owner.

See [evidence](../evidence/shared-state-2026-10-31.json),
[native checks](../evidence/shared-state-native-2026-10-31.txt),
[reference checks](../evidence/shared-state-reference-2026-10-31.txt) and
[affected regression](../evidence/shared-state-regression-2026-10-31.txt).
Paired follow-up prompts and predeclared outcome criteria are retained privately
under `private/live-share-2026-10-31/followup/`. No online trials of this candidate
or new public push occurred in this increment.

The public mask, recurrence and BF helpers are available to an analyst. A
symbolic normalizer now tracks the dependencies and erases the representation
on the tested arithmetic fixture. This is executed evidence, not a pending risk.
The simple pilot remains a negative baseline, not an obstacle made impossible by
this pass. Required follow-up compares representative programs, selectors and
repeated fresh model sessions, grades extraction and functional reconstruction,
and includes compiler normalization and trace/devirtualization attacks. Complete
all application budgets and exact recovery before any promotion. No universal
AI failure, secrecy or copy-prevention claim is made.

## Multi-cell controller checkpoint — 2026-11-01

`src/machines/bf_share_tape.bf` extends the drafted controller domain to a
nonnegative logical pointer with six physical cells per logical cell. Integer
register zero tracks the logical pointer; stack zero records loop-entry pointers.
Loop bodies must return statically to their entry pointer. Pointer-underflow,
capacity, unbalanced loops, drift and malformed lifecycle reject. It reuses BF
helpers 201–206; each cell's live value is represented by its two shares modulo
256. Finishing materializes the current cell only; interpreting other final tape
cells requires the share relation. This is an explicit semantics limitation.

The controller compiled natively at O1 and passed 24 protocol fixtures. No complete
helper-chain, representative policy, transformed final-state or new AI comparison
has executed for this controller. `config/tape-share-flow.example.json` remains
an unbound example; the old Python flow runner is migration debt. Native transport
components do not themselves provide that VM. The retired ignored one-time
authoring generator is not needed to execute or modify the authoritative BF.
See [migration](LANGUAGE_MIGRATION.md) and
[scoped evidence](../evidence/native-byte-host-2026-11-01.json).
