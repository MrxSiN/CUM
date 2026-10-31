# Current validation status

**PARTIAL — one complete synthetic BF release passed the actual prepare workflow.
CUM is not complete or production accepted.**

| Evidence | Observed result |
|---|---|
| Source coverage | PARTIAL — whole workflow drafted; restricted adapters |
| Current regression | PASS within executed scope — 77 discovered, 75 passed, two VM opt-in tests not rerun; native/crypto/graph enabled |
| Prior all-enabled checkpoint | PASS — 74 tests with zero skips before the generic CLI repair; historical evidence retained |
| Current Windows BF compilation | PASS — 42/42 at O1, including two test workers |
| Native human command parser | PASS — all eight commands, rejection cases and host-to-BF planner bridge |
| Native XAX edit | PASS — four single-mutation edit/verify stages, native resolve/build, changed code, four behavior inputs, stale replay rejection |
| VM isolation boundary | PASS — 256 KiB binary roundtrip, readonly inputs, UID 1000, no NIC/host shares, unsafe output rejection |
| Isolated BF fixtures | PASS — eight Windows builds under Wine, 32 behavior runs, two normalization comparisons, eleven worker-boundary cases |
| Synthetic signed clone recovery | PASS — direct Windows and isolated VM; exact captured scope restored after original trees were removed; signature/capsule/extra-file mutations rejected |
| Earlier native BF/JVM fixtures | PASS within recorded scope — unchanged native artifacts retain their prior evidence |
| Complete prepare workflow | PASS for one corrected synthetic BF fixture — 71 native instructions, 55 service receipts, sixteen evidence selections, native acceptance and atomic finalization |
| Retained offline runtime and relocated cold restore | PASS within same-host scope — synthetic release and 91-file real-project source snapshot; exact BF recovery and restored native XAX verification |
| Independent-media backup and different-host cold restore | NOT ESTABLISHED |
| Repeated measurements and scale | Scoped PASS — 15 paired samples per O0/O1 arm, 15 BF transformations, binary-text mapping through 1,049,600 bytes, exact 1,024-file archive roundtrip |
| Android protection and advanced resistance | UNSUPPORTED / UNACCEPTED — annotated target semantics fail current standard-BF admission probe |
| Production release acceptance | NOT ACCEPTED |

The parser still declines at O0; O1 is the explicit verified build configuration.
This observation is not a permanent CUM capacity limit. Neither BBC nor XAX was
edited to hide an unavailable compiler ability. Thirty-seven rebuilt artifacts
were byte-identical at the earlier blocker checkpoint. The current build adds
presentation kernels and extends the BF prepare plan with late review hooks.

See [production readiness](PRODUCTION_READINESS.md), [synthetic release](SYNTHETIC_RELEASE.md), [blocker follow-up](BLOCKER_FIXES.md), [VM operations](BYTEVM.md), and the
[current evidence](../evidence/synthetic-prepare-2026-10-31.json). The original
[validation checkpoint](VERIFICATION.md) and its dated failure records remain
historical and unchanged.

BBC checkout: `53783953fd87cbc9308b108d187b7f3fcfedc06d`.
XAX checkout: `f5d07d77614a9ffec17b2271a25447757cbcfd55`.
Actual executable identities are recorded separately. The installed binaries
were not rebuilt from these checkouts during this work. SDK queries remain an
explicit Python dependency; native executables supply edit/build authority.

General Java/Kotlin, arbitrary BF pointer/loop behavior, universal XAX workspaces,
development-ready XAX workspace recovery, COCK and advanced analysis resistance
remain unsupported or unaccepted. Synthetic fixture success does not establish
real-project licensing, owner approval, full offline recovery or release acceptance.
