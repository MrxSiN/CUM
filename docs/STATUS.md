# Current validation status

**PARTIAL — one complete synthetic BF release passed the actual prepare workflow.
CUM is not complete or production accepted.**

Use the [engineering index](INDEX.md) to navigate contracts and dated checkpoints.
The root README is intentionally neutral. Engineering details, limitations and
evidence remain explicit here; README wording grants no additional acceptance.

| Evidence | Observed result |
|---|---|
| Source coverage | PARTIAL — whole workflow drafted; restricted adapters |
| Latest broad regression | PASS within executed scope — 93 tests, 91 passed, two VM opt-ins not rerun; native/crypto/graph enabled |
| Audit remediation | Seven host findings fixed sequentially with regression checks; separate Linux VM run passed 25 tests with zero skips |
| Final annotation regression | PASS — five tests including the added native record-boundary and rejected-output case |
| Prior all-enabled checkpoint | PASS — 74 tests with zero skips before the generic CLI repair; historical evidence retained |
| Retained native inventory | 44 matched components at O1 from the annotation checkpoint — three fresh then, 41 matching prior identities; audit fixes changed no BF sources |
| Audit native smoke | Two fresh Windows builds, all 256 echo bytes, five native BF layout events and four protected-native behavior cases passed |
| Annotated BF | Scoped PASS — full-line precedence, split records, binary comment bytes, explicit BF workflow and nine real sources |
| Native human command parser | PASS — all eight commands, rejection cases and host-to-BF planner bridge |
| Native XAX edit | PASS — four single-mutation edit/verify stages, native resolve/build, changed code, four behavior inputs, stale replay rejection |
| VM isolation boundary | PASS — 256 KiB binary roundtrip, readonly inputs, UID 1000, no NIC/host shares, unsafe output rejection |
| Isolated BF fixtures | PASS — eight Windows builds under Wine, 32 behavior runs, two normalization comparisons, eleven worker-boundary cases |
| Synthetic signed clone recovery | PASS — direct Windows and isolated VM; exact captured scope restored after original trees were removed; signature/capsule/extra-file mutations rejected |
| Earlier native BF/JVM fixtures | PASS within recorded scope — unchanged native artifacts retain their prior evidence |
| Complete prepare workflow | PASS for one corrected synthetic BF fixture — 71 native instructions, 55 service receipts, sixteen evidence selections, native acceptance and atomic finalization |
| Retained offline runtime and relocated cold restore | PASS within same-host scope — synthetic release and 91-file real-project source snapshot; exact BF recovery and restored native XAX verification |
| Independent-media backup and different-host cold restore | NOT ESTABLISHED — owner deferred the different-host drill |
| Repeated measurements and scale | Scoped PASS — 15 paired samples per O0/O1 arm, 15 BF transformations, binary-text mapping through 1,049,600 bytes, exact 1,024-file archive roundtrip |
| Android execution | Scoped PASS — 196 existing-JNI comparisons, 372 standalone cases, ten explicit PERFORMANCE cases and eleven existing-APK startup checks |
| Isolated unsigned baseline APK | NOT ESTABLISHED — source verification passed; unsigned lowering exceeded controlled 900/600-second budgets |
| Protected Android shared libraries / APK | UNACCEPTED — tested adapter rejected the recorded bind; tape/budget compatibility and integrated protected APK remain closed |
| Advanced resistance | UNACCEPTED |
| Production release acceptance | NOT ACCEPTED |

The prior parser probe declined at O0; O1 remains the verified component configuration.
This observation is not a permanent CUM capacity limit. Neither BBC nor XAX was
edited to hide an unavailable compiler ability. Thirty-seven rebuilt artifacts
were byte-identical at the earlier blocker checkpoint. Later checkpoints added
presentation/review hooks and the explicit annotated filter/flow. The complete
synthetic prepare result belongs to its recorded source snapshot, not an implicit
rerun of every subsequent source change.

See [audit remediation](AUDIT_FIXES.md), [annotated BF and Android](ANDROID_READINESS.md), [production readiness](PRODUCTION_READINESS.md), [synthetic release](SYNTHETIC_RELEASE.md), [blocker follow-up](BLOCKER_FIXES.md), [VM operations](BYTEVM.md), and the
[current evidence](../evidence/audit-fixes-2026-10-31.json). The original
[validation checkpoint](VERIFICATION.md) and its dated failure records remain
historical and unchanged.

Initial BBC checkout: `53783953fd87cbc9308b108d187b7f3fcfedc06d`.
Initial XAX checkout: `f5d07d77614a9ffec17b2271a25447757cbcfd55`.
During the follow-up they advanced externally to BBC
`520db418b73fe751d002790323b20643f28a1538` and XAX
`40db64ca742eaf462b894bd3077243f45f4a3087`. The tested executable hashes
remained unchanged. Isolated SDK jobs use their retained, checked input inventories.
Actual executable identities are recorded separately. The installed binaries
were not rebuilt from these checkouts during this work. SDK queries remain an
explicit Python dependency; native executables supply edit/build authority.

At the audit-fix checkpoint the externally advanced source heads were observed as
BBC `cd67df41fd7647de2f2232602b796d5009dd3bfe` and XAX
`b3e22b008bb1ff9fb773dcafe05d6d6b3f92b1de`. The installed BBC binary had also
changed to SHA-256 `de9a2c5f65312a493f615f5c06f90761a5d3bf1971f460fe37113c8a6a71e405`;
the tested XAX executable remained `110a76a2578f5f55777e6b0438b05642013e9587cae902ef3729229af8e5420e`.
These are observations, not a claim that the binaries were rebuilt from those
heads. Retained bundle inventories were not rewritten; deploying the host fixes
requires a newly reviewed and pinned runtime bundle.

General Java/Kotlin, arbitrary BF pointer/loop behavior, universal XAX workspaces,
development-ready XAX workspace recovery, COCK and advanced analysis resistance
remain unsupported or unaccepted. Synthetic fixture success does not establish
real-project licensing, owner approval, full offline recovery or release acceptance.
