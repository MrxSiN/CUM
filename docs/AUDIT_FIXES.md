# Audit remediation checkpoint — 2026-10-31

The seven audit findings were repaired sequentially, with a regression reproducer
before each implementation fix and a separate commit per finding. All changes
are generic host infrastructure, tests, example operands or documentation. BF
application sources and both compiler repositories were not edited by this work.

| Finding | Change | Commit |
|---|---|---|
| 1. Unapproved Docker recovery engine | Independent policy must include the exact engine executable/hash; missing or changed pins reject before isolation | `37ffa95` |
| 2. Plaintext left after failed restoration | Owned stages remove read-only files and restrictive directories; cleanup failures retain the original rejection and identify remaining material | `a192452` |
| 3. Incorrect build source identity | Hash the exact compiler-input bytes and reject a source edit before issuing the build report | `87e908e` |
| 4. Descendants survive process completion | Windows uses a Job Object established before the child resumes; POSIX uses a new session/process group; both generic process wrappers stop their descendants | `9dc02ea` |
| 5. Late byte-machine publication | Bound every native call/handoff by remaining operation time and check the deadline before publication | `4e94dbc` |
| 6. Lost directory modes | Apply recorded directory modes after copying children, before exact-tree verification | `ef92e4b` |
| 7. Failed cache entries block retries | Validate input, stage payload/authentication record privately and publish the complete directory atomically | `d591bb8` |

## Executed verification

Focused Windows checks passed for each fix, including actual descendant processes,
real OpenSSL and native BF command checks. A separate native smoke check freshly
compiled two Windows executables through the real BBC driver, echoed all 256 byte
values, ran a five-event BF layout transformation within its deadline, and passed
four protected-native behavior cases. Mocked fault tests establish host failure
handling; they do not establish compiler or language semantics.

The final broad Windows regression ran 93 tests: 91 passed, zero failed/errored,
and two VM opt-ins were not rerun. Native Windows, crypto and native graph checks
were enabled. The confirmation run used the readiness-triggered descendant test.

The separate credential-free Linux VM passed 25 tests, zero failures/errors/skips,
as UID 1000 with only loopback networking. Its first attempt had four subtest
failures because the one-second test startup budget expired before descendants
started under TCG. The test now signals timeout through a controlled clock only
after actual child readiness, with a separate startup guard. Product time limits
were not relaxed. The final Windows suite and raw test counts are linked in the
[dated evidence](../evidence/audit-fixes-2026-10-31.json).

The VM used the existing pinned standalone image and disposable overlay without
host shares or credentials. This was a same-host Linux check, not the deferred
different-host recovery drill. It does not relabel the two VM opt-ins skipped in
the broad Windows regression as passes.

## Compatibility and remaining limits

Existing Docker recovery/runtime policies without `engine` now fail closed.
Update the explicit example operands and independently review/authenticate the
new policy before use. QEMU keeps its separate complete `vm` identity check.

Retained runtime bundles and their independent inventories contain their frozen
host source. They were not silently rewritten or re-signed by this repair pass.
Rebuild, review and pin a new bundle to deploy these fixes; old recovery evidence
does not certify an updated bundle. The root README remains neutral and unchanged.

BBC changed externally to executable SHA-256
`de9a2c5f65312a493f615f5c06f90761a5d3bf1971f460fe37113c8a6a71e405`.
That binary supplied this pass's fresh native builds. The 44 retained BF component
artifacts have their earlier compiler identities; they were not all recompiled.
Source checkout observations do not establish how installed binaries were built.

Actual Docker-container launch was not exercised. Existing Android shared-library,
APK, preferred-source/notice delivery, independent-media and production acceptance
gates remain open. Historical Android probes were not rerun against the externally
updated BBC. See [current status](STATUS.md) and [Android readiness](ANDROID_READINESS.md).
