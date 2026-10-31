# Deferred test matrix

The matrix lists acceptance areas, not blanket passing coverage. Current outcomes
and exclusions are in `STATUS.md` and dated evidence. The original 52-test checkpoint
and its XAX/isolation failures remain in `VERIFICATION.md`; later restricted
native edits and VM checks passed. Test source existence is never a passing result.

| Area | Authored checks / required runs |
|---|---|
| BF source | Eight-command-only bytes, exact bracket acceptance, native O0/O1 builds |
| BF arithmetic | All 256 cell values, both signs, profiles/selectors, scratch-zero invariant |
| BF behavior | Nested single-cell loops, zero-skipped loops, wrap, EOF, binary I/O, termination |
| BF eligibility | Both pointer moves, including skipped loops, unknown profiles/adapters |
| Structural | Filtered instruction difference, actual BBC O1 BFX difference, later independent simplifiers |
| Frames | Empty/binary/all byte values, every truncation, physical EOF, wrong lengths/digests, trailing data |
| Continuation | Width-one and varied chunks, constructs crossing frames, restart, altered key/state/output/input |
| Host boundary | Fixed BF versus real BF through identical map/exchange services, host source inspection |
| Snapshot | Exact Git commit/path scope, export exclusions, changed live worktree, submodule/symlink rejection |
| Archive | Exact bytes/line endings/binary zeros/empty dirs, duplicate paths, truncation, malicious types |
| Windows paths | Traversal, drive/UNC/ADS, reserved names, reparse points, Unicode/case collisions |
| Crypto | Correct recipient, wrong key/cert, corrupted CMS, unauthenticated format rejection |
| Signatures | Wrong key/trust fingerprint, changed manifest/capsule/inventory/files, missing/extra entries |
| Recovery | Internal round trip separate from signed public-style clean recovery; new destination only |
| Failures | Process exit, capacity, integer conversion, disk full, OOM, interruption, final rename failure |
| Isolation | No network, only approved mounts, no keys/archive mounts, process/time/memory/output limits |
| Profiles | Source/native expansion, transform/build/runtime/RAM budgets, normalization failure blocks |
| Release | Each failed/unknown gate blocks readiness, no circular hashes, no private material, no publication |
| Provenance | Exact tool/artifact/commit identities, raw observed outputs and commands in private evidence |

Reference interpreter and host-only runs are separate from native Windows runs.
Wine/container runs are emulation/isolation evidence, not real Windows device
evidence. Actual Android execution is recorded separately in
`ANDROID_READINESS.md`; its standalone and existing-JNI checks do not accept an
integrated protected APK.

The authored unit suites cover a subset of this matrix. Crypto, native pipeline,
restart/failure injection, isolation and actual release exercises need provisioned
tools and further executable cases. Never claim complete test coverage from this
table or silently treat skipped tests as passing.


Additional deferred sources: `test_workflow_draft.py`, `test_git_transport.py`,
`test_isolated_recovery.py`, `test_runtime_bundle.py`, and expanded native/runtime
checks. Required cases include complete operands/order, failed/unknown evidence
before finalization, public/vault modes, exact binary staging and real clone,
removed private blobs in history, pinned-policy mutation/missing/duplicate mounts,
forbidden-original overlap, complete runtime distributions and cold tools, and
restricted JVM/graph behavior. The four new unit modules ran as recorded; native
runtime/JVM/graph acceptance did not. Further allocation/disk exhaustion,
Windows metadata, clean signed recovery and native target cases remain necessary.


`test_signed_recovery.py` is an opt-in native Windows integration test using
synthetic fixtures/disposable keys, real capture/crypto/Git, copied host modules
and a BF recovery planner in a separate process. It removes original fixture trees
and rejects signature/capsule mutation and extra release files. With the explicit
VM opt-in it also checks recovery under the independently pinned QEMU policy.
`test_qemu_isolation.py` checks transport faults and real VM boundaries;
`test_qemu_native.py` checks isolated builds/behavior without identities. None
established a complete offline runtime package at that checkpoint. A retained
runtime now passed separate same-host relocation drills; see
`PRODUCTION_READINESS.md` for its scope and remaining different-host requirement.
The earlier statement
about four new unit modules describes the draft checkpoint, not the current run.

The previous regression discovered 77 tests, passed 75 and skipped two VM opt-ins.
`test_service_output.py` reproduces and guards binary JSON service output and
ambiguous-field rejection. `test_offline_bootstrap.py` uses Windows PowerShell to
verify a complete tree and reject wrong pins, changed, extra and missing files.
Two actual retained-runtime VM calls independently recovered the synthetic release
and a real-project declared snapshot after the CLI fix. These executed drills do
not relabel the two skipped regression tests as passes.

The annotation/Android follow-up ran 81 tests: 79 passed and two VM opt-ins were
not rerun. A separate five-test annotation run includes the subsequently added
native record-boundary and rejected-output test. `test_annotations.py` covers
whole-line precedence at every split, binary comment bytes, unsupported code and
state rejection, explicit planner ordering, native continuation and atomic failure.
See `ANDROID_READINESS.md` for device counts and dependency build declines.
