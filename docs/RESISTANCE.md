# Amended reconstruction-resistance contract

PARTIAL — the new profile release gate is implemented. Actual AI reconstruction
resistance remains BLOCKED until measured, repeatable evidence exists. Complexity,
comments, a working APK, different BFX and exact recovery do not establish it.

The amendment supplied on 2026-10-31 has SHA-256
`ec59cf0024c168f47eb4ef9dbd415c573f64b152be2c1472f8573628dfdd1ded`.
Section 28 directs the next verifiable correction rather than a replacement of
working foundations. This increment closes the missing profile-specific release
gate. It does not declare Stage 6, every adapter or production complete.

## Release decisions

`src/resistance_policy.bf` contains the executable policy in genuine eight-command
BF. The generic host reads explicitly selected integer fields and transports
exactly twelve bytes. It knows no profile names or transformation rules.

| Byte | Meaning |
|---|---|
| 0 | profile: FAST 1, CAMOUFLAGE 2, MAXIMUM 3, PERFORMANCE 4 |
| 1 | explicit AI-resistance claim: 0 or 1 |
| 2 | baseline normalization evidence |
| 3 | criteria/scope predeclared before evaluation |
| 4 | review binds the actual immutable input, job, passes/seeds and protected inventory |
| 5 | matched protected/unprotected attack arms and budgets |
| 6 | isolated evaluators; protected arm never sees originals or heldout grader |
| 7 | verified evaluator/model/tool identities and repeatable runs |
| 8 | private heldout grading performed locally |
| 9 | complete reconstruction outcomes, rubrics, failures and repetitions retained |
| 10 | predeclared extraction/reimplementation success criteria met |
| 11 | all disclosures within explicit authorization; no unauthorized private upload |

Evidence bytes use 0 unknown, 1 PASS, 2 FAIL, 3 BLOCKED, 4 PARTIAL and
5 NOT STARTED. All other bytes are invalid. Output is 1 PASS, 2 FAIL or 3 BLOCKED;
only exactly byte 1 allows a release. Required FAIL takes precedence over incomplete
evidence. Invalid metadata always fails, including invalid unused evidence.

Bytes 2–4 are mandatory for every profile. Bytes 5–11 are mandatory for profiles
2/3 and for any profile with an AI-resistance claim. FAST/PERFORMANCE without that
claim can omit advanced evidence; their other release gates remain mandatory.
The claim flag cannot disable CAMOUFLAGE/MAXIMUM's evaluation gate.

This policy admits authenticated evidence; it does not turn assertions into
measurements. A reviewer must inspect the actual evaluation outputs. Signing an
invented PASS or a tool returning exit zero is not evidence. The signer and pinned
reviewer remain explicit trust assumptions, as with the existing legal review.

## Prepare and publication

The five prepare job examples now authenticate a preregistered plan before
capture, check its exact job and criteria digests, and atomically record those
three input digests. The plan must also match the running journal's actual
bindings digest, planner identity and request, so an edited job file cannot
silently stand in for the in-memory workflow. Once candidate metadata and inventory exist, a pinned
independent local reviewer supplies a signed review bound to that inventory,
private snapshot manifest, normalization report, frozen job, plan and criteria.
The review must match the frozen digests and the plan's profile/claim. BF selects
signature verification, exact assertions and its native policy before composing
or signing the release. Any refusal aborts signing/finalization.

The signed public manifest carries only the twelve reviewed numeric facts and
`protection_contract: CUM-RESISTANCE-GATE`; no private scope hashes, criteria,
logs, originals, seeds/mappings or identities are exported by these additions.
The inventory still binds the actual protected source. Publication re-runs the
BF policy on the signed manifest after existing provenance/history checks and
before push. Legacy manifests missing the new contract cannot be newly published
through this path. Legacy exact recovery remains available and unchanged.

Existing private job files must be deliberately re-bound to the new native planner
and operands 75–81. Examples contain replacement pins and cannot pass unchanged.
An old runtime bundle retains its old behavior; a bundle used for prepare or
publication must be rebuilt/reviewed and independently pinned before relying on
this enforcement. A recovery-only bundle does not need the new release policy.
Direct arbitrary Git
commands cannot be prevented by a release tool; review the selected publication
path and trust the pinned BF programs and generic host.

## Evaluation contract

Use `config/resistance-criteria.example.json`, `resistance-plan.example.json` and
`resistance-review.example.json`. They are deliberately incomplete, not runnable
approval fixtures. No model backend or numerical security threshold is invented
by CUM. Select suitable budgets and acceptance criteria before collecting data.
Authenticate the plan before capture/attack execution and retain the frozen input
record outside untrusted evaluator mounts. Independent reviewers sign only real
observations; the examples do not implement a model or reviewer.

Measure four separate outcomes: exact bytes, structural reconstruction, algorithm
and design extraction, and independent functional reimplementation. The last two
are the objective. Public code can always be copied. Both arms get the same task,
models/tools, context and opportunity limits; the protected evaluator receives only
approved public materials, public history and approved oracle access. Use fresh
isolated sessions, not two prompts in one conversation. Preserve all attempts,
multiple seeds/projects/repetitions where feasible, failures, exclusions, rubric
scores and uncertainty. Grade private heldout behavior locally and independently
review maintainability and buildability. A failed baseline or censored attack is
inconclusive unless the predeclared analysis justifies a conclusion.

No private originals, maps, recovery capsules/identities or hidden tests may be
uploaded to an external AI without explicit owner authorization. An existing
public repository is already disclosed; changing visibility cannot undo history.
No new publication or visibility change is authorized by this amendment.

The independent normalizer now folds odd-counter affine transfer loops modulo
256, including positive-counter variants, retaining conditional pointer excursions
so bounds failures are not erased. Even-counter/nonterminating, nested or I/O
loops stay explicit. Pointer cancellation without bounds proof is deliberately
not applied. This tool analyzes; it never emits protected project source.
Actual BBC BFX/native inspection and trace/devirtualization analysis remain
required where relevant. Unequal normal forms alone prove no AI resistance.

Tiny Boolean policies such as those in Dummy can be inferred by enumerating their
inputs. More comments, opcode renaming or layout changes do not remove that oracle.
The current Android work protects nine BF components, not the full XAX host.
Do not call the whole APK resistant on that basis.

## Evidence and next acceptance

Source, configuration, fixtures, tests and this contract were drafted before
executing amended checks. Executed results belong in the dated amendment evidence;
reference interpretation, mocks, native execution and adversarial measurements
must be reported separately. Historical release/recovery evidence is retained
with its original scope, not promoted to acceptance under this contract.

Next acceptance requires an approved isolated evaluator and populated predeclared
criteria, normalization/trace attacks on representative protected programs,
matched reconstruction experiments and independent local heldout grading. Only
then should stronger transformations be chosen from measured failures. No AI
resistance, different-host recovery or new protected APK is accepted here.

## Executed checkpoint — 2026-10-31

PASS within scope: all three changed BF components compiled at O1; 423 native
policy inputs and three native prepare/publication routes matched expectations.
Eight new test methods passed across the focused runs. Real OpenSSL signatures
and the native policy admitted a disposable FAST/nonclaim record, rejected
CAMOUFLAGE with missing evaluation and rejected a modified signature. These are
test facts, not a signed production resistance result.

The broader regression ran 93 tests: 91 passed, two independent-VM opt-ins skipped.
Native annotations/commands, real crypto/signed recovery and native XAX edit/build
checks were enabled. The affine model also matched actual BF execution over all
256 byte values for three counter variants, retaining conditional negative-pointer
failures. Nine existing protected/original pairs still differed under the new
normalizer. An exploratory eight-query oracle table reproduced the complete
Boolean-triple behavior of one small policy; this was not an AI benchmark.

See [machine-readable evidence](../evidence/amendment-2026-10-31.json),
[native focused log](../evidence/amendment-focused-native-2026-10-31.txt),
[signed-admission log](../evidence/amendment-signed-admission-2026-10-31.txt) and
[regression log](../evidence/amendment-regression-2026-10-31.txt).
Private input inventories and oracle observations remain private. No affected
prepare was run to a new signed release, no new release recovery was accepted,
and no publication or visibility change was performed. No local Ollama, LM Studio
or llama-cli executable was found on PATH; an approved isolated evaluator/model
and populated criteria are needed for the next reconstruction experiment.

## Owner-collected online pilot

The owner subsequently selected online ChatGPT in Chrome Temporary Chat and
supplied four answers, reporting **Sol 6 High**. See the
[pilot report](RECONSTRUCTION_PILOT.md) for local grading and its limitations.
Both protected explanations expose the exact arithmetic algorithm. The pasted
Python arrived as one physical line and is graded separately after documented
formatting restoration. Fresh-session isolation, run order, immutable backend
identity remain unverified. AI costs were not measured in the historical pilot
and are excluded from current acceptance by direct owner instruction. This is a source-only
pilot of one arithmetic worker; it does not satisfy the full reconstruction gate.

## Current owner override and implementation increment

The owner waived AI-cost accounting on 2026-10-31. Monetary, token, latency and
compute-cost comparisons are not mandatory. Predeclare extraction and independent
functional-reconstruction outcomes with matched attempts, prompt/context and
oracle opportunities instead. Byte 9 (`metrics_complete`) now covers outcome
reports and grading, not AI fees or compute accounting; the wire schema is
unchanged. Application/transformation/build/runtime/memory budgets still apply.
The new [shared-state candidate](SHARED_STATE.md) addresses the exposed primitive
as an explicit experimental BF workflow. It does not bypass any release gate.

The subsequent [readiness audit](READINESS_AUDIT.md) recovered both tested
shared-state arithmetic variants without an outside AI. Each independent
reimplementation matched 65,809 reference cases. The mandatory BF normalization
checker now rejects equal observable projections and blocks incomplete or
inconclusive analysis. No BF release is admitted by this conservative checker;
its supported attack domain and unavailable admission path are explicit. This
negative result does not count as a matched online AI experiment or establish
the resistance of any other pass. The drafted online follow-up is deferred for
these exposed variants.
