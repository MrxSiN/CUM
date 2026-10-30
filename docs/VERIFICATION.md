# Windows validation — 2026-10-30

The whole-workflow source draft was followed by actual unit, compiler, native
fixture, public compiler, crypto and synthetic signed-recovery runs. Overall
status is PARTIAL. The native XAX adapter fails; the human CLI and isolated final
release workflow are blocked. A passing unit suite is not whole-product acceptance.

## Executed checks

- Full suite: **52 PASS**, no skips, 156.948 seconds. This includes exhaustive
  reference-interpreter arithmetic over 256 cell values, both signs and declared
  profiles/selectors; frame truncation/binary checks; restart faults; real Git;
  real OpenSSL encryption/signatures; and the new native signed-recovery test.
- Compiler probes: 40 components at O0 and O1. **17/40 O0**, **39/40 O1** built.
  All declines were BBC exit 5. `command.bf` also declined at O1; its source check
  and 11,587-byte O1 BFX emission succeeded. No interpreter build fallback ran.
- Native Windows host checks: echo/fixed/transform workers with empty, zero and
  binary payloads; cross-process opaque state; fixed/real machine processing.
- BF source protection: counter, input, wrap, single-cell-loop, multi-cell, nested
  and linear-VM fixtures. Native BF emitted the protected sources. Original and
  protected source compiled at both levels (28 builds), then 112 native runs
  matched independent interpretation for empty/00/01/ff00 inputs. Seven source,
  independent normalization and real BBC O1 BFX comparisons retained differences.
- Java/Kotlin: native BF CAMOUFLAGE emission of the restricted Arithmetic module,
  real JDK/Kotlin builds, five integer boundary pairs plus 16 seeded random pairs
  per language, and different public compiler bytecode. General-language support
  and all-profile native behavior are not established by this fixture.
- Signed recovery: Windows locked capture, internal CMS authenticated roundtrip,
  native BF transformation, portable inventory/signature, exact Git staging/audit,
  commit and real clone. After removing original/snapshot/internal fixture trees,
  a separate Python process using copied host modules and a native BF recovery
  planner restored the exact scope. Signature/capsule mutation and extra files
  failed before restoration. Keys and fixtures were disposable and not published.
- Native XAX seed verify/inspect of an existing canonical fixture succeeded.
  The actual BF recipe on a selected wrapping-add node **failed native edit** with
  `XAX.WORKSPACE.DUPLICATE_MUTATION`. The output was a diagnostic, not a candidate.

## Reproduce

Use a fresh ignored build/output directory and independently hash the chosen
compiler. `config/build.example.json` lists every source. Bind real tool pins and
compile each source at O0/O1; unsupported native cases must remain declined.
Native check modules consume explicit private bindings with fresh report paths.
The executed bindings and full raw compiler observations remain under the ignored
`private/validation-2026-10-30/` folder on the development machine.

The full suite command, after building available O1 workers, was:

```powershell
$env:PATH = 'C:\Program Files\Git\ucrt64\bin;' + $env:PATH
$env:BYTEHOST_CRYPTO_TESTS = '1'
$env:BYTEHOST_NATIVE_INTEGRATION = '1'
$env:BYTEHOST_NATIVE_DIRECTORY = 'D:\GitHub\CUM\build\validation-2026-10-30\O1'
$env:XAX_REQUIRE_NATIVE = '1'
python -u -m unittest discover -s tests -t . -v
```

Individual executed native check entries are `tests.native_checks` (boundary,
behavior, normalization), `tests.machine_checks`, `tests.language_checks`
(behavior/normalization for each JVM language), and `tests.test_signed_recovery`.
The signed recovery test generates its synthetic data, independently retained
signer trust and disposable identities itself, using established OpenSSL tools.
It is not a project-provided build script or a real release approval.

The installed Kotlin batch launcher failed to load its preloader. The test driver
now accepts explicit tool argument prefixes and pinned compiler inputs. The
working binding invokes installed Java with `-cp <kotlin-compiler.jar>` and
`org.jetbrains.kotlin.cli.jvm.K2JVMCompiler`; `inputs_sha256` pins that JAR.
No Kotlin source transformation was added to the host or test driver.

## Evidence and limits

The dated `evidence/*-2026-10-30.json` records retain component/fixture scope,
source/tool/artifact identities, native outcomes and actual failures. The full
suite log is `evidence/unit-suite-native-2026-10-30.txt`. The earlier 22-check
record is historical, not relabeled as this run.

Native processes ran directly on Windows x86-64. The installed BBC executable
contains its own XAX backend; the XAX Windows seed is an older pinned executable.
The XAX checkout update does not establish that these binaries were rebuilt from
that commit. SDK graph queries remain an explicit Python dependency and supply
no native authority; acceptance/rejection above comes from the native seed.

No Docker/Podman command or installed WSL was available and no reviewed container
image was provisioned. Thus the final isolated build/recovery, full offline tool
backup, real-project release/licensing gates and publication were not exercised.
No large scalability stress, Android execution, repeated performance benchmarks,
accepted runtime budgets or advanced resistance experiments ran. Diagnostic
single-process counters are not a performance comparison or protection guarantee.
