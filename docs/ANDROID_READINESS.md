# Annotated BF and Android checkpoint — 2026-10-31

**PARTIAL. No protected Android release is accepted.** The annotation issue is
resolved for the declared grammar; shared-library integration and source-provision
approval remain closed. The owner deferred the different-host drill.

## Executed annotation and native checks

The BF filter and explicit flow are documented in [ANNOTATED_BF.md](ANNOTATED_BF.md).
Three current BF components were freshly compiled at O1; 41 previous native
artifacts retain matching source and artifact identities. This is a 44-component
matched inventory, not 44 fresh compilations.

The complete annotated fixture flow passed 512 native Windows behavior checks
across O0/O1. Fixed-worker replacement showed that the generic host does not strip
comments or transform code independently. All nine real-project BF sources matched
the independent annotation reference and passed the current layout preconditions.
The commented test candidates differ from their originals under BBC O1 BFX.

The broad regression checkpoint ran 81 tests: 79 passed, two VM opt-ins were not
rerun, and none failed. A subsequent five-test annotation run includes an additional
native regression for record widths 1/7/31 and rejection without output publication.
It passed separately; this is not a claim of one all-enabled 82-test run.

## Actual Pixel observations

- The actual shipped JNI bridge and nine policy libraries passed 196 independent
  reference comparisons. Unused output tails and the Java tape remained unchanged.
- Boundary observations were status 3 for a one-cell tape, -4 for a 65,536-cell
  tape, and 1 for a zero budget. These are observed existing-ABI results, not a
  promise that a replacement compiler/library has the same contract.
- Seventeen standalone ARM64 executables passed 372 finite-file input cases.
  They cover all nine filtered originals and eight CAMOUFLAGE outputs. An initial
  ADB stream run timed out; regular, digest-checked files established finite stdin.
- The time-window CAMOUFLAGE output declined in the native Android backend with
  exit 5. An explicit PERFORMANCE-profile probe compiled at O1 for Windows and
  Android, retained different optimized BFX, and passed ten further Pixel cases.
  Its O0 builds declined on both targets. No implicit runtime fallback selected it.
- The installed baseline APK matched the retained artifact exactly. Its freshly
  started YouTube process reported eleven passing startup self-checks. Root
  read-only log access was needed; unprivileged log collection did not establish
  those results. No candidate was installed and no application data or settings
  were cleared or changed. Startup checks do not certify every live feature.

The existing BBC Android bind interface emitted a record, but the existing XAX
shared-library adapter rejected it: no graph referenced its expected decision.
The installed bridge's tape/budget results also prohibit treating a different
shared ABI as compatible. Neither compiler was changed. Standalone executable
success is not acceptance of an in-process JNI library or a protected APK.

## Isolated APK build

The unsigned baseline build receives only the canonical source, thirteen exact
declared inputs, public compiler material and an empty result directory. It has
no signing credentials, original working-directory mount or private CUM runtime.
It uses the existing unsigned compiler API; it cannot approve or sign a release.

The controlled run passed source verification and reached unsigned lowering, then
its compiler subprocess exceeded the explicit 900-second budget (exit 124).
Earlier cold attempts ended at the VM response deadline without build evidence.
The retained configuration uses the SDK's existing explicit Python bootstrap
paths; it is not evidence of a native self-hosted APK build. Neither SDK source
nor compiler binaries were modified.

A second controlled run used the SDK's existing initially empty proof cache.
It also passed source verification, reached unsigned lowering and expired at its
600-second compiler budget (exit 124). The cache did not establish a successful
build within this run. Disposable QEMU instances were stopped by their runners.

No unsigned artifact was produced for payload comparison or installation. A
compiler budget expiration does not establish a semantic compiler rejection or
a permanent capacity limit. Isolated baseline APK reproducibility remains open.

## Artifact licensing review

The fetched DexKit AAR exactly matches the retained Java input and packaged ARM64
library. D8 rebuilt the packaged dependency DEX byte-for-byte from that input plus
the declared FlatBuffers Java and Kotlin stdlib artifacts. The Morphe notice also
matches its packaged resource exactly.

The exact DexKit POM lists LGPL-3.0 and Apache-2.0. Its tag README specifies
LGPL-3.0 for `Core/` and Apache-2.0 for everything else; the review preserves both
component terms, not an Apache-only choice. See [the pinned component declaration](https://github.com/LuckyPray/DexKit/blob/2.3.0/README.md#license).
Repository license texts and an artifact-specific review were added locally. The
existing APK's notice packaging was not changed by those source-only additions.
The pinned Core tree also contains vendored code with its own notices, including
Apache attributions and a zlib-style thread-pool notice. The Core label does not
erase those terms; complete the transitive notice/source inventory before release.

The selected project's GPL source-provision decision remains unresolved. A private
recovery capsule does not replace delivery of the preferred editable source and
required build material. Preserve the applicable license, notice and modification
requirements; obtain an explicit source-delivery and release review before public
distribution. See the [GPL source definition](https://www.gnu.org/licenses/gpl-3.0.html#section1).
No protected application, credentials or real job configuration was published.

See [dated implementation evidence](../evidence/annotated-android-2026-10-31.json).
Actual project sources, per-file source digests, raw device logs, dependencies and
operational bindings remain private.
