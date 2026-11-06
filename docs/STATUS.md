# Current validation status

**PARTIAL. CUM is not complete or production accepted.** Release acceptance
remains false. Dated results, including failures, are in [history](HISTORY.md).

| Area | State | Details |
|---|---|---|
| Production release | NOT ACCEPTED | No complete amended prepare/release transaction has passed |
| Reconstruction resistance | UNACCEPTED | CAMOUFLAGE/MAXIMUM BLOCKED; an independent attack recovered the tested shared-state variants ([follow-up](READINESS_AUDIT.md), [pilot](RECONSTRUCTION_PILOT.md)) |
| Profile resistance gate | PARTIAL | Implemented across BF, transport and prepare bindings; full amended transaction outstanding ([resistance](RESISTANCE.md)) |
| BF/XAX-only migration | PARTIAL | 94 tracked foreign-language files remain; none retired; language compliance closed ([migration](LANGUAGE_MIGRATION.md)) |
| Native byte host | Scoped PASS | Two XAX transport components pass 43 direct cases and rebuild byte-identically ([native host](NATIVE_BYTE_HOST.md)) |
| Native worker runner | Scoped PASS | 93 cases and cancellation drill; memory-denial probe traps, so graceful failure is unaccepted; not a sandbox ([runner](NATIVE_PROCESS_RUNNER.md)) |
| Native arguments | Scoped PASS | 32 BF vectors and 19 CRT roundtrips; XAX verifier failed the 2 GiB budget ([arguments](NATIVE_ARGUMENTS.md)) |
| Native workflow VM | INCOMPLETE | Native host/VM/CLI migration not finished |
| Project-scoped recovery | Scoped PASS | Real 97-file scope restored exactly from a ciphertext-only clone ([recovery](PROJECT_RECOVERY.md)) |
| PQ interoperability | Scoped PASS | OpenSSL 3.6.5 / Bouncy Castle 1.86 full CMS exchange; ordinary prepare still admits only the classical scheme ([PQ](PQ_INTEROPERABILITY.md), [prepare](PREPARE_INTEGRATION.md)) |
| Offline kit and independent key backup | NOT ESTABLISHED | Different-host cold restore deferred by the owner |
| Android | Scoped PASS / UNACCEPTED | 196 joint JNI comparisons on Pixel 8 Pro passed; protected APK and isolated baseline APK not established |
| Private source delivery | DRAFT | Assembled and checked; rebuild, notices, relinking, licensing and publication unaccepted ([delivery](SOURCE_DELIVERY.md)) |
| Live shared-state pass | EXPERIMENTAL | Not a production/default-route replacement ([shared state](SHARED_STATE.md)) |

General Java/Kotlin, arbitrary BF pointer/loop behavior, universal XAX workspaces,
development-ready XAX workspace recovery, COCK and advanced analysis resistance
remain unsupported or unaccepted. Synthetic fixture success does not establish
real-project licensing, owner approval, full offline recovery or release acceptance.

Source written, compiled, executed, tested, recovered, signed, measured and release
accepted are separate states. Compiler identities and older checkpoint results are
in [history](HISTORY.md). Use the [engineering index](INDEX.md) for contracts.
