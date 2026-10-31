# Prepare integration and remaining acceptance — 2026-11-01

This earlier checkpoint precedes the later
[independent PQ exchange and project foundation](PQ_INTEROPERABILITY.md), which
passed the tested full CMS interoperability gate. Its earlier BLOCKED findings
below describe the installed 3.5.9 tools and preceding evidence. Ordinary prepare
and overall production acceptance remain unaccepted.

PARTIAL — source integration and scoped checks executed. A complete amended
prepare/release transaction, resistant candidate and protected APK remain
unaccepted. The initial implementation and checks were drafted before testing.

## Full prepare adoption

The two ordinary prepare modes now verify a signed project-prepare context and
signed project identity before capture. The context binds actual runtime planner,
request and operand identities to the reviewed job; encryption recipients and
internal/clean recovery key paths are also bound. All five adapter examples use a
project-specific vault. Disjoint-root checks precede capture.

Before protected-tree inventory, the BF planner exports only public identity
metadata, its signature, recipient certificate and public SPKI. No private key
is copied. The signed release binds the project ID, classical-security scope,
`PROJECT-SCOPED-CMS-RECOVERY` contract and public identity/certificate digests.
Candidate and clone checks include these same public files. Public builds still
need no private CUM or recovery identity.

The separate `scoped_clean_recovery.bf` verifies release provenance/inventory,
identity provenance and expected project/release/recipient bindings before
decryption. Default clean-recovery bindings now use this decoder. Historical
`clean_recovery.bf` and legacy recovery tests remain available for old capsules.
Publication requires the scoped contract; recovery of historical data does not
silently reinterpret its security properties. Existing isolation approval must
be repinned for the new runtime and bindings.

Preflight tests may stub unrelated services to isolate the real native planner
and OpenSSL context checks. Those tests are not a full signed prepare transaction.
The resistance gate remains mandatory and unchanged. The tested weak transforms
still reject; no fake positive normalization or review record is supplied.

## PQ CMS candidate

Both installed OpenSSL CMS paths are blocked for KEM recipients. A separately
identifiable, generic Java adapter invokes actual Bouncy Castle CMS APIs for
ML-KEM-1024 / HKDF-SHA256 / AES-256-Wrap / AES-256-GCM. It implements no cipher,
KEM, wrapping construction or source transformation itself. See
[backend boundary](../host/tools/README.md).

Dependency pins/sidecars and the installed JDK are explicit. Executed checks cover
OpenSSL-generated key/certificate interchange, authenticated roundtrip, empty and
binary data, wrong identities, corrupt/truncated capsules and output refusal.
Publisher signatures for the dependencies passed. One-family roundtrip and key
interchange are PARTIAL; independent full CMS interoperability remains required
before PQ mode can enter prepare. Classical recovery stays available, without downgrade or
quantum-safe signature claims. Standards: [RFC 9629](https://www.rfc-editor.org/rfc/rfc9629.html),
[RFC 9936](https://www.rfc-editor.org/rfc/rfc9936.html) and
[Bouncy Castle CMS API](https://downloads.bouncycastle.org/java/docs/bcpkix-jdk18on-javadoc/org/bouncycastle/cms/jcajce/JceKEMRecipientInfoGenerator.html).

## AI resistance and APK acceptance

The last independent attack reconstructed the shared-state arithmetic variants;
the new key-management work cannot repair that failure. All nine project BF
components use pointer movement, outside that pass's domain. Do not generate
another online trial for an already exposed candidate or pretend source masking
protects the unchanged XAX host. A representative, semantics-proven candidate
must survive deterministic attacks before matched external AI exercises help.

The current APK inventory and ADB ABI/device visibility were observed
without installing, uninstalling or changing application data. A baseline APK or
separate protected shared libraries cannot be accepted as an integrated protected
APK. The prior unsigned source-build runs expired at 900/600 seconds on the
unchanged pinned compiler path; do not rerun them with a larger budget and call
that a capability fix. Independent source build, integrated JNI/ABI behavior,
device checks, signing, licensing/preferred-source approval, resistance and
performance all remain separate requirements. No blocker grants a release PASS.


## Executed checkpoint

The current planner and scoped decoder compiled at O1. The decoder also compiled
and ran at O0. Whole CUM O0 rejected with backend exit 5; the exact pre-change CUM
source rejected identically. No compiler source was edited. Seventy-six native
planning/rejection vectors matched independent interpretation.

Twenty-three final focused checks passed: real-signature native prepare preflight,
runtime recipient-substitution rejection, exact scoped fixture recovery, strict
public-identity schemas/types and legacy signed clone recovery. The preflight test
stubs unrelated services and stops before capture; it is not a full prepare run.
The earlier broad regression passed 17 checks with one native signed-recovery
opt-in skipped; that check passed in the final enabled run.

The PQ test passed with freshly compiled/packaged code: empty/binary data,
OpenSSL-generated key interchange, wrong keys, corrupt/truncated messages and
existing-output refusal. An intermediate duplicate-local compile error left an
older class available; that stale-artifact run is excluded. After correction,
compilation and JAR packaging each succeeded separately before retesting.
The backend then recovered the retained 97-file immutable project archive exactly
and matched its captured scope. This same-backend experiment stays private; its
identity is disposable, not an admitted operational project identity.

Publisher signatures for all three Java JARs passed against the key linked on
the official publisher's HTTPS page, using an isolated public-key GPG home. The
first import attempt used unsupported Git/MSYS Windows paths; correcting those
to /d/ paths resolved it. The user's trust database was not modified. Each
classpath JAR is pinned before tool invocation and JVM injection variables are
cleared. The decoder checks KEM/KDF/wrap and GCM nonce/tag parameters. The
experimental binding is config/pq-cms-tool.example.json; production prepare
still admits only the verified classical scheme.

C# 2.7 source inspection found ASN.1 KEMRecipientInfo but no KEM handler in its
CMS recipient dispatcher. No C# program was executed. Together with installed
OpenSSL CMS rejection, this leaves independently implemented full CMS
interoperability BLOCKED. Successful key interchange is a narrower result.

The read-only inventory observed 89 APKs and nine retained protected libraries;
none of those APKs contained a matching retained protected library. This does
not classify unrelated/rebuilt payloads as unprotected; no accepted candidate
with the expected retained payload and source-build proof was identified.
After initial checks found no device, the owner enabled the connection. The
advertised paired wireless service connected successfully: Pixel 8 Pro, SDK 37,
arm64-v8a. Read-only inspection of the installed module found 11 native libraries,
none matching the nine retained protected libraries. No APK was installed or
removed, and no app data changed.

All nine retained protected libraries then passed 196 joint JNI comparisons in
a fresh shell-owned directory with the existing bridge. Original and protected
expected outputs were independently interpreted again, and every transferred
file hash was checked on-device. Three tape/budget cases remain observations
(statuses 3, -4 and 1), not successful application cases. The first local
provenance attempt selected an earlier intermediate source; its hash mismatch
stopped before any device operation. Selecting the exact retained compilation
inputs corrected the verification runner. This is joint library evidence, not
an installed or accepted integrated APK.

A paused, diskless, networkless QEMU WHPX probe failed accelerator initialization.
No host feature was enabled or changed. Thus the earlier isolated source-build
timeout is still unresolved; no new full APK build or larger-budget retry is
claimed. Licensing/preferred-source and production performance approval remain
separate unaccepted gates.
Known resistance failures remain valid for the unchanged attacked fixture bytes.

See [dated evidence](../evidence/prepare-integration-2026-11-01.json),
[focused regression](../evidence/prepare-focused-2026-11-01.txt) and
[PQ test](../evidence/pq-cms-2026-11-01.txt). The
[joint JNI record](../evidence/joint-protected-jni-2026-11-01.json) contains only
sanitized observations; device addresses and original-source hashes stay private.
