# Test coverage and outstanding matrix

This matrix lists acceptance areas, not blanket passing coverage. Test source
existence is not execution. [Status](STATUS.md) and dated evidence distinguish
reference, native, isolated, recovered, signed, measured and accepted states.

| Area | Authored checks / required runs |
|---|---|
| BF source | Eight-command-only bytes, exact bracket acceptance, native O0/O1 builds |
| BF arithmetic | All 256 cell values, both signs, profiles/selectors, scratch-zero invariant |
| BF behavior | Nested single-cell loops, zero-skipped loops, wrap, EOF, binary I/O, termination |
| Annotated BF | Whole-line precedence, binary comment bytes, every split, explicit flow, unsupported state/code and rejected-output atomicity |
| Android | Shipped JNI ABI, finite-file ARM64 behavior, backend declines and baseline startup; integrated protected APK unaccepted |
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

## Latest executed checkpoints

| Run | Scope and outcome |
|---|---|
| Original Windows checkpoint | 52 passed; later fixes do not rewrite its XAX/CLI/isolation failures |
| Blocker checkpoint | 67 passed with zero skips, including native/crypto/graph/VM scopes |
| Synthetic prepare checkpoint | 74 passed with zero skips; one complete restricted prepare release |
| Recovery/measurement checkpoint | 75/77 passed; two VM opt-ins skipped; actual same-host cold VM calls recorded separately |
| Latest broad annotation run | 79/81 passed, zero failures, two VM opt-ins not rerun; native/crypto/graph enabled |
| Subsequent annotation run | Five passed, including the newly added native boundary/rejected-output case |

The last two runs are separate; no single all-enabled 82-test run is claimed.
Reference-interpreter checks are distinct from native Windows runs. Wine/TCG
results are emulation/isolation evidence. Existing-JNI and standalone ARM64 device
checks do not accept an integrated protected APK.

## Current executable coverage

- `test_annotations.py` covers every comment split, binary comment bytes,
  unsupported code/state, BF planner order, native widths 1/7/31 and no publication
  of rejected mapped output. `test_presentation.py` checks comment headers and
  restricted HTML mapping. The full native fixture flow has 512 comparisons.
- `test_service_output.py` covers lossless binary CLI JSON and ambiguous-field
  rejection. `test_offline_bootstrap.py` checks PowerShell exact-tree validation
  and changed, extra, missing or wrongly pinned material.
- `test_workflow_draft.py`, `test_git_transport.py`, `test_isolated_recovery.py`,
  `test_runtime_bundle.py`, `test_trusted_inputs.py` and the policy/storage/transport
  suites exist and ran within recorded opt-in scopes. Their names are not deferred
  implementation tasks and do not establish every case listed in this matrix.
- `test_native_commands.py` and `test_native_graph.py` cover restricted parser and
  four-transaction graph behavior. Native BF/JVM fixture checks retain their own
  exact compiler/semantic domains; general language support is not inferred.
- `test_signed_recovery.py` uses disposable identities, real capture/crypto/Git and
  native BF recovery in a separate process. With the explicit VM opt-in it also
  tests independently pinned isolation. `test_qemu_isolation.py` checks real VM
  boundaries; `test_qemu_native.py` checks credential-free isolated native fixtures.
  Those last two VM opt-ins were skipped in the latest broad run.
- Separate retained-runtime VM calls restored the synthetic release and a 91-file
  real-project source scope. They do not relabel skipped regression tests as passes
  or cover the later-added readiness and license files.

## Outstanding acceptance

Broader disk/allocation exhaustion, failure injection, Windows metadata scope,
representative program complexity and repeated full-release budgets remain open.
Android shared-library tape/budget compatibility, isolated APK production and
restored development closure remain unaccepted. Controlled unsigned baseline
builds passed source verification but expired in lowering and produced no APK.

The existing library checks passed 196 JNI comparisons; seventeen standalone
programs passed 372 cases, with ten further explicit PERFORMANCE cases and eleven
existing-APK startup check lines. These finite observations and the compile
rejections are detailed in [Android readiness](ANDROID_READINESS.md).

Independent-media backup, different-host recovery (owner-deferred), source/notice
provision and final production approval remain separate gates. Use fresh ignored
bindings and explicit opt-ins described in [operations](OPERATIONS.md) and
[QEMU instructions](BYTEVM.md); never turn skips, missing tools or unknown evidence
into passes. Historical logs and evidence files remain unchanged.
