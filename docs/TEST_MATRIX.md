# Test coverage and outstanding matrix

This matrix lists acceptance areas, not blanket passing coverage. Test source
existence is not execution. [Status](STATUS.md) and dated evidence distinguish
reference, native, isolated, recovered, signed, measured and accepted states.

The [native transport checkpoint](NATIVE_BYTE_HOST.md) executed 22 framer cases,
21 response cases, 20 BF codec compositions, one historical transform composition
and 24 controller protocol cases. Fixtures are JSON data, not foreign test code.
The [source package](SOURCE_DELIVERY.md) separately checks archive/source identity
and privacy; it does not establish full application rebuild or licensing acceptance.

The [native trusted runner](NATIVE_PROCESS_RUNNER.md) separately passed 93 scoped
cases and a supervisor-only cancellation drill. Its CPU-limit correction, initial
probe/build failures and limited-versus-generous memory observations are retained.
No complete host, sandbox or application performance acceptance follows from it.

The [argument increment](NATIVE_ARGUMENTS.md) adds 32 native BF vectors,
19 independent CRT roundtrips, seven new rejection cases, exact command-boundary
and supervisor-cancellation checks, plus all 93 NRQ1 regressions. Real pinned
compiler/OpenSSL invocations executed. The compiler failed at 2 GiB and passed a
separate 4 GiB capacity probe; neither promotes application performance acceptance.

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
| Audit-fix Windows run | 91/93 passed, zero failures, two VM opt-ins not rerun; native/crypto/graph enabled |
| Audit-fix Linux VM run | 25 passed with zero skips after removing the descendant test's startup-timing assumption |

The annotation runs are separate; no single all-enabled 82-test run is claimed.
The audit's separate Linux VM run does not relabel skipped Windows opt-ins.
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

`test_build.py`, `test_process.py`, `test_machine_host.py`, `test_cache.py` and
the extended storage/recovery tests cover all seven audit fixes. The process
tests use actual descendants with a readiness-triggered timeout clock; compiler
mutation and deadline fault tests use mocked tools/clocks. The separate smoke
check used the real BBC and native BF workers. See [audit remediation](AUDIT_FIXES.md).

Broader disk/allocation exhaustion, failure injection, Windows metadata scope,
representative program complexity and repeated full-release budgets remain open.
Android shared-library tape/budget compatibility, isolated APK production and
restored development closure remain unaccepted. Controlled unsigned baseline
builds passed source verification but expired in lowering and produced no APK.

The latest ADB check passed 196 existing-JNI comparisons and 394 standalone cases
across eighteen freshly compiled O1 programs, including two additional signed-long
boundaries. Eleven baseline startup lines and all nine current O1 BFX differences
passed. One additional CAMOUFLAGE time-window build declined, and the shared
adapter still rejected the current bind. See [fresh ADB verification](ADB_VERIFICATION.md);
the earlier counts remain in [Android readiness](ANDROID_READINESS.md).

Independent-media backup, different-host recovery (owner-deferred), source/notice
provision and final production approval remain separate gates. Use fresh ignored
bindings and explicit opt-ins described in [operations](OPERATIONS.md) and
[QEMU instructions](BYTEVM.md); never turn skips, missing tools or unknown evidence
into passes. Historical logs and evidence files remain unchanged.
# Amended checks

`tests/test_resistance.py` covers all four profile policies, unknown/failing
facts, nonclaim paths, strict observed byte transport, digest/profile binding,
failure before signing/finalization, configuration coverage and affine-loop
normalization attacks. Native checks require `CUM_AMENDMENT_NATIVE` pointing to
fresh policy/planner builds. These tests establish policy enforcement within
their executed scope; none is an AI reconstruction benchmark. See
[RESISTANCE.md](RESISTANCE.md) and dated evidence for actual execution status.

`tests/test_symbolic_analysis.py` verifies independent polynomial recovery,
boundary/termination/budget rejection, read ordering and stale-report checks.
The opt-in QEMU native fixture expects the weak candidate to fail normalization;
its behavior and boundary records remain separate. See
[readiness follow-up](READINESS_AUDIT.md) for executed status. All nine focused
methods passed, including nested multiplication and inconclusive-result blocking.
The affected set completed 20 unique methods across initial and corrected
invocations. The isolated native fixture added one passed method with eight
builds, 32 behavior runs, eleven boundary cases and expected normalization FAIL.
The final unequal-projection branch was locally checked after the VM snapshot;
see the dated evidence for that limitation and the preserved initial errors.

## Project-scoped recovery draft

`tests/test_project_identity.py` covers BF routing, disjoint roots and scoped real-crypto recovery.
`tests/tools/crypto_probe.py` probes the installed ML-KEM/CMS backend without selecting a product mode.
`tests/vm_project_recovery.py` drafts isolated signed-context verification without original mounts.
Executed after drafting: all four new methods and 19 affected legacy methods
passed, along with four fresh builds and 80 native plan/rejection vectors.
The real-project signed clone/VM recovery and three guest context rejections
passed after a corrected driver path mapping. Both ML-KEM/CMS probes are BLOCKED.
See [project recovery evidence](../evidence/project-recovery-2026-10-31.json),
which retains the initial comparison and VM failures separately.

## Prepare/PQ integration — 2026-11-01

Six new prepare-scope methods are included in the 23-method final focused run.
The PQ method adds authenticated same-backend/key-interchange checks. All passed.
Seventy-six native planning vectors passed. Real-archive PQ recovery passed only
within the one-backend scope. Independent full CMS, AI and APK acceptance remain
blocked; see [dated evidence](../evidence/prepare-integration-2026-11-01.json).

The connected Pixel 8 Pro also passed 196 joint JNI comparisons with all nine
retained protected libraries, using the existing bridge and fresh on-device
hash verification. Expected outputs for original and retained candidate sources
were independently rechecked. Three tape/budget cases were observations, not
application successes. No APK was installed and no complete protected APK was
accepted. A no-workload WHPX availability probe failed initialization; it did
not change host configuration or establish an accelerated build path.

## Independent PQ CMS and project foundation — 2026-11-01

The four interoperability methods, fifteen project/classical crypto/trusted-input
methods and sixteen affected prepare/recovery/isolation/runtime methods passed:
35 distinct methods, no unittest skips. Four project methods additionally passed
with O0 artifacts. Four fresh BF builds supplied 80 native plan/rejection vectors.
The existing signed-recovery method ran its native Windows branch; no new VM
execution is implied. Initial project errors and the initial receipt-length typo
are retained separately. Real retained-project recovery passed within the
same-host scope. See [the exact boundaries](PQ_INTEROPERABILITY.md).
