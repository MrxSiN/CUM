# Deferred test matrix

The matrix is not an executed acceptance checklist. After whole-project source
drafting, 22 focused generic host/BF workflow checks passed; their exact scope is
`../evidence/unit-checks-2026-10-30.json`. Native and release checks remain NOT
STARTED. Test source existence is never a passing result.

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
evidence. Android target execution is not implemented by this draft.

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
