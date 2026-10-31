# ADB Android verification — 2026-10-31

Fresh verification used `D:/Android/platform-tools/adb.exe` on the connected
Pixel 8 Pro, Android API 37, `arm64-v8a`. The installed module APK exactly matched
the retained baseline. No replacement APK or JNI library was installed.

## Executed results

| Check | Result |
|---|---|
| Current source/candidate binding | All nine original inputs and retained candidates match their previously verified identities |
| Fresh BBC O1 Android builds | 18 successful standalone executables; ELF64/AArch64 headers checked |
| Baseline JNI | 196 independent reference comparisons across nine actual shipped policy libraries passed; unused output tails and Java tape unchanged |
| Standalone behavior | 394 cases passed: 196 original and 198 candidate cases, including two additional signed-long boundaries |
| Structural comparison | All nine candidates differ from their originals under the current BBC O1 BFX |
| Existing application startup | Eleven fresh self-check lines passed, collected through read-only root logs for the current process |
| Additional CAMOUFLAGE time-window probe | Native backend declined with exit 5; separate from the 18 successful selected builds |
| Shared-library bind | BBC emitted a record; the existing XAX adapter rejected it: expected one graph referencing the decision, found zero |

All uploaded executables, libraries, driver and finite binary input files were
checked by SHA-256 on the device. Native programs read regular files through
`adb exec-out` and a bounded device process. This avoids relying on ADB stream EOF.
The JNI driver was freshly compiled to DEX and executed with `app_process`.
Source transformation outputs were reused only after exact identity checks;
this pass did not regenerate those transformations or change product code.

The selected candidate uses eight explicit CAMOUFLAGE profile-2 outputs and one
explicit PERFORMANCE profile-4 output. The extra profile-2 time-window probe did
not trigger an automatic fallback. O0 was not reprobed in this pass.

The installed bridge again returned status 3 for a one-cell tape, -4 for a
65,536-cell tape, and 1 for zero budget. These are baseline observations, not
replacement-ABI approval. The existing YouTube installation was opened once;
it was not already running. No application data was cleared and no settings were
changed by the verification commands. Startup checks do not certify all live features.

## Tool identity and acceptance

The current BBC executable SHA-256 was
`de9a2c5f65312a493f615f5c06f90761a5d3bf1971f460fe37113c8a6a71e405`.
ADB SHA-256 was
`b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f`.
The Android shared adapter was reprobed with that BBC and still rejected the bind.
Neither compiler repository was modified to bypass the rejection.

**Scoped device verification passed. Protected Android release acceptance remains
false.** Standalone candidates and the original shipped JNI libraries are distinct
artifacts. A supported replacement shared-library ABI, integrated protected APK,
restored development build and final source/notice delivery review remain open.
The different-host recovery drill remains owner-deferred.

See [sanitized evidence](../evidence/adb-verification-2026-10-31.json) and
[result summary](../evidence/adb-verification-2026-10-31.txt). Actual source/artifact
identities, device identifiers, operation bindings and raw application logs remain
private. The earlier [Android checkpoint](ANDROID_READINESS.md) retains its own
counts and failed attempts; [status](STATUS.md) links the latest results.
