# CUM engineering documentation

CUM is a Brainfuck-authored source-camouflage and authenticated exact-recovery
project. All application decisions and transformations belong in genuine BF under
`src/`; Python under `host/` provides separately identifiable generic services.
The dependency pipeline includes Python, BBC/XAX, OpenSSL and isolation tooling.

**Partial implementation with scoped evidence; production is not accepted.** One
synthetic BF project completed the actual prepare workflow. Current annotations,
Android observations and outstanding gates are recorded separately. A passing
fixture never promotes a broader language, platform or release claim.

## Start here

- [Current status](STATUS.md): latest evidence, exclusions and dependency identities.
- [Operations](OPERATIONS.md): tool binding, capture, prepare, verification and recovery.
- [Requirements](REQUIREMENTS.md): requirement coverage and remaining acceptance work.
- [Test matrix](TEST_MATRIX.md): authored checks, executed scopes and missing coverage.

## Implementation contracts

| Document | Scope |
|---|---|
| [Authority](AUTHORITY.md) | Direct instructions, attachment scope and publication boundary |
| [Ownership](BOUNDARIES.md) | BF application logic versus generic host services |
| [Adapters](ADAPTERS.md) | Restricted language domains and explicit admission |
| [Transformations](TRANSFORMATIONS.md) | Pass semantics, profiles and structural acceptance |
| [Annotated BF](ANNOTATED_BF.md) | Whole-line comment grammar and explicit flow |
| [Presentation](PRESENTATION.md) | BF comments and restricted document encoding |
| [Binary protocol](PROTOCOL.md) | Framing, worker state and authenticated continuation |
| [Workflow VM](VM.md) | BF plans, opcodes, operands and fail-stop execution |
| [QEMU isolation](BYTEVM.md) | Image provisioning, declared capabilities and trust |
| [Measurements](METRICS.md) | Counter scopes, repeated samples and interpretation |
| [Diagnostics](ERRORS.md) | Process, transport, evidence and integrity failures |

## Checkpoints and evidence

| Checkpoint | Interpretation |
|---|---|
| [Original Windows validation](VERIFICATION.md) | Historical 52-test checkpoint, including failures |
| [Blocker follow-up](BLOCKER_FIXES.md) | Historical 67-test checkpoint and restricted fixes |
| [Synthetic release](SYNTHETIC_RELEASE.md) | One full prepare transaction; 74-test all-enabled checkpoint |
| [Recovery and measurement checkpoint](PRODUCTION_READINESS.md) | Historical 77-test run, same-host restores and finite scale probes |
| [Annotated BF and Android](ANDROID_READINESS.md) | 81-test broad checkpoint, separate five-test run, actual device checks and failed APK builds |
| [Audit remediation](AUDIT_FIXES.md) | Seven host fixes, Windows regression, native build smoke and separate 25-test Linux VM run |
| [Fresh ADB verification](ADB_VERIFICATION.md) | Current-tool Android builds, 196 JNI comparisons, 394 standalone cases, eleven startup checks and rejected shared bind |

Read [status](STATUS.md) for current conclusions. Dated checkpoint results keep
their original source/tool scope; later fixes do not rewrite failed evidence.
Source written, compiled, executed, tested, recovered, signed, measured and release
accepted are separate states. Skips, unknowns and budget expirations are not passes.

The root README is a neutral entry point. These engineering documents remain
explicit and readable. README wording does not hide source, documentation, dated
evidence or repository history. Licenses, notices and source-delivery obligations
remain applicable; no protected application publication is authorized by a fixture.
