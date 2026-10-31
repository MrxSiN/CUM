# Production readiness checkpoint — 2026-10-31

The later [prepare/PQ checkpoint](PREPARE_INTEGRATION.md) records scoped prepare
integration, experimental PQ recovery and 196 joint JNI comparisons using all
nine retained protected libraries on the connected device. Full APK source-build,
AI resistance and production acceptance remain unestablished. The rest of this
page preserves the earlier checkpoint.

The subsequent [independent PQ foundation](PQ_INTEROPERABILITY.md) passed
bidirectional CMS interoperability and exact same-host recovery of the retained
97-file snapshot with a separate ML-KEM project identity. Independent key backup,
PQ offline-kit deployment and overall release acceptance remain unestablished.

The [amended resistance/readiness follow-up](READINESS_AUDIT.md) tracks the newer
candidate and check-kit changes. Historical recovery below is not resistance
acceptance and does not admit an integrated protected APK.

This earlier checkpoint precedes [annotation-aware BF and Android follow-up](ANDROID_READINESS.md).
Its failed raw-dialect probe remains historical; the explicit annotation flow now
handles the declared grammar. Android shared-library and release gates remain closed.

**PARTIAL. Production acceptance remains false.** A relocated offline recovery
kit and a real project's declared source snapshot now have executed recovery
evidence. This does not admit an unsupported protection adapter or approve a
public application release.

## Operational work completed

The retained kit contains a CPython executable, DLLs and standard library without
site-packages or bytecode caches; the complete inventoried QEMU distribution;
a standalone QCOW2 guest with Python/OpenSSL/Wine; generic host modules; native
BF recovery components; and the public compiler distribution. Its payload is
4,551,328,284 bytes before the small CLI repair. Credentials and independent
trust pins are retained separately in owner/System-only directories. No private
identity, actual job binding, original source or image is committed to CUM.

The corrected kit ran from a directory outside the development checkout, with
isolated Python, no installed tools on PATH and no original/reference guest
mount. Signed policy validation, native BF signature/inventory/decrypt/extract/
pack/receipt operations and exact archive comparison passed. Both the synthetic
release and the selected real-project snapshot recovered successfully. The latter
contains 91 files and 119 entries, totaling 2,534,412 file bytes. Its recovered
canonical XAX store passed native verification. APK builds and device behavior
were unverified at this checkpoint. Later existing-JNI, standalone and baseline
startup checks are in [Android readiness](ANDROID_READINESS.md); isolated unsigned
APK lowering still produced no artifact, and protected integration remains closed.

These were **same-physical-host relocation drills**, using a fresh disposable VM
without guest networking or filesystem shares. They do not establish a backup on
independent media or a different-machine cold restore. The real-project capture
excluded Git, build outputs, generated files and historical evidence. Required
external Android build inputs and signing capabilities remain outside that scope.

## Defect fixed and bootstrap verification

The generic `service` CLI previously failed JSON serialization after a successful
isolation operation because stdout/stderr were bytes. It now emits `stdout_hex`
and `stderr_hex`, preserving every byte and rejecting conflicting fields. A
regression reproduced the failure before the fix; the corrected retained runtime
then completed both actual VM calls through that CLI.

`host/verify_bundle.ps1` verifies an exact inventory using Windows PowerShell
before bundled Python or other tools execute. Supply the inventory SHA-256 from
independent retained trust, and retain/pin this verifier separately too. A public
key supplied inside an untrusted kit is not its own trust anchor. The verifier
checks every declared file's bytes/size, directory types, missing/extra entries,
duplicate paths and reparse points. It does not claim POSIX mode enforcement on
Windows; exact archive recovery checks the supported mode scope separately.

```text
powershell.exe -NoProfile -NonInteractive -File INDEPENDENT/verify_bundle.ps1 -TreeRoot KIT/payload -InventoryPath KIT/payload-inventory.json -InventorySha256 INDEPENDENT_PIN
KIT/payload/python/python.exe -I -B KIT/payload/bytehost/runtime_entry.py service 44 APPROVED/recovery-job.json
```

Use `-B` explicitly: `-I` ignores `PYTHONDONTWRITEBYTECODE`. Python cache creation
changed the initially frozen kit and was correctly rejected before execution.
Additional backup metadata also invalidated an initially overbroad credential
mount. The corrected layout mounts only the exact credential subdirectory and
keeps mutable instructions outside it. A minimal Windows environment must retain
`SYSTEMROOT`; dropping it prevented Winsock initialization. Those attempts remain
failed records, not recovery passes. The old runtime also reproduced the binary
serialization error after its guest recovery passed; its outer CLI result failed.

## Measured evidence and its limits

- O0/O1 native builds of the original/protected BF fixture passed 258 behavior
  vectors per arm, including every single-byte input, empty input and trailing
  input. Physical stdin cursor observations matched. This is finite evidence.
- Fifteen randomized paired process samples per optimization level were recorded
  after correctness checks and an untimed warmup. Median process wall time was
  about 23 ms for both arms. Startup and the host's 10 ms polling dominate this
  tiny fixture; these samples do not establish zero runtime overhead.
- Fifteen actual BF machine transformations produced identical source digests;
  median operation time was 1.823 seconds. Native process CPU and peak working-set
  counters are retained separately from host wall time.
- Native framed mapping accepted 1,024, 65,536 and 1,049,600 input bytes. The
  largest input took 7.232 seconds across 257 records. These inputs contain binary
  ignored text and three executable commands. They prove that scoped transport
  case, not million-instruction or deeply nested program scalability.
- Exact archive roundtrips passed for 16, 256 and 1,024 files plus an empty
  directory. These are storage probes, not complete release transactions.

QEMU process counters include the guest OS and software emulation. They are not
protected-application memory measurements. Compilation and whole-release repeated
budgets still need representative projects and raw repeated samples.

## Historical dialect rejection and current gates

The selected project's BF dialect ignores whole lines starting with `#`, including
BF punctuation inside those annotations. The standard-BF adapter treats
that punctuation as commands. An independent native probe passed syntax handling
but failed all eight expected AND3 behavior vectors. Its protection request is
therefore **rejected**, despite native XAX verification and matching recorded SDK
file identities. Reference-only annotation stripping in this test is not an
implemented production adapter at this checkpoint. The later BF-owned explicit
annotation flow resolves the declared grammar; it does not change the semantics
of the raw standard-BF route or admit an enclosing Android application.

Before this target can be accepted, verify the Android shared-library tape/budget
ABI and full dependency closure, independently build and test the protected APK,
and demonstrate usable restored development. Retain the external dependencies
needed for that build, complete a different-host recovery drill when the owner
resumes it, and obtain project-specific source-provision, license/attribution and
final owner reviews. Existing fixture signers explicitly do not grant production
approval. No protected application was published.

See the [dated evidence](../evidence/production-readiness-2026-10-31.json). Original
source, per-file original digests, real operation bindings and identities remain
private. Earlier dated checkpoints are unchanged.

This checkpoint's regression discovered 77 tests: 75 passed, zero failed, and two VM
opt-in tests were not rerun. Native, crypto and graph checks were enabled. The two
fresh cold VM drills are separate executed evidence, not replacement labels for
those skipped tests. The prior 74-test all-enabled checkpoint remains historical.
The later broad run passed 79/81 with two VM opt-ins skipped, followed by a separate
five-test annotation pass. Use [status](STATUS.md) for current inventory and gates;
the dated [evidence here](../evidence/production-readiness-2026-10-31.json) remains
the original recovery/measurement record.
# Amended release status

BLOCKED for production AI-resistance claims. The amended design requires
predeclared, matched protected/unprotected reconstruction experiments and private
heldout grading. The BF-owned enforcement and evidence binding are documented in
[RESISTANCE.md](RESISTANCE.md). Historical successful recovery, native tests and
normalization differences below do not satisfy that new gate.
