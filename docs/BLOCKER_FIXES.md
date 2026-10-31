# Blocker follow-up — 2026-10-30

This historical checkpoint preserves its executed 67-test scope. This follow-up
changed CUM application BF and generic infrastructure without editing BBC or XAX.
Later synthetic, recovery and annotation/Android results are indexed in
[INDEX.md](INDEX.md); use [STATUS.md](STATUS.md) for current conclusions.

## Command parser

The genuine BF parser now shares command prefixes and rejects missing/changed bytes,
prefixes and suffixes while preserving opaque state. The selected BBC builds it
at O1. All 40 BF components at this checkpoint (including two test workers) built in a fresh
directory. O0 still declines the parser; O1 is the explicit verified build binding.
Native tests exercise all eight command strings, binary suffix rejection and the
real host app-to-BF planner bridge. That bridge test uses a synthetic planner
binding and does not itself execute the full production doctor/prepare workflow.

## Native graph edit

Each XAXEDIT1 carrier now has one mutation. Native BF emits four transactions:
insert zero, insert negation, change ADD to SUB, replace the RHS. The BF flow
queries and verifies each stage before recording the chain and replacing source.
All seven workflow examples supply the corresponding operands. The read-only
SDK query refreshes a unique changed function interface and rejects ambiguity.

The native regression compiles `,+.` through the real BBC frontend, exports its
existing canonical build-request closure, and chooses its wrapping-byte ADD node.
All four edits/verifications, resolve/build, changed native code, four behavior
inputs and stale-root replay rejection pass. No textual XAX was authored. SDK
queries remain Python observations; the native XAX executable supplies edit/build
authority. Its executable pin is separate from the current SDK commit.

An earlier existing XAX regression fixture hung on Windows even before editing,
including when built with the installed native drivers. It is not counted as a
passing behavior fixture. Resolved snapshots are also not editable build requests.
The finite BBC-authored regression establishes neither universal graph support nor
development-ready workspace recovery.

## Isolation

The generic QEMU backend uses a pinned standalone disk, disposable overlay, no NIC,
no host shares, unprivileged execution and explicit returned files. The real
boundary test passed readonly-input, network, binary output and path rejection
checks. A separate credential-free VM passed eight Windows builds, 32 finite
behavior runs, two normalization comparisons and eleven worker-boundary cases.
These Wine/TCG results are emulation evidence. See `BYTEVM.md` for image trust,
provisioning and independently pinned recovery capabilities.

The new image also passes a 256 KiB real-VM roundtrip, exercising complete-write
framing beyond the earlier small responses. A nonce-bound READY handshake precedes
job transfer, and the host enforces a deadline across the entire response.

Signed recovery now passes inside a separate VM after deleting the original,
snapshot and internal-restoration fixture trees. It receives only a fully
inventoried export from the real Git clone (without `.git`), retained runtime,
disposable identity/trust, exact bindings and empty results. Native BF selects
signature/inventory verification, authenticated decryption, extraction and result
packing. The returned archive restores the exact captured bytes and metadata.
Altered signature, altered capsule and extra files all reject before restoration.
OpenSSL 3.0.13 and Wine 9.0 in this image are independently identified in the result.

At this checkpoint, a complete protected-release flow, independent offline runtime
backup drill, real-project review, scalability/performance budgets, Android
execution and production acceptance remained separate requirements. Later scoped
results do not retrospectively expand this run's evidence.

## Final executed gate

The full discovered suite passed **67 tests**, zero failures/errors/skips, in
798.552 seconds. Native graph, crypto, native integration and real VM opt-ins
were all enabled. The checkpoint build record binds all 40 source/artifact identities;
37 artifacts are byte-identical to their prior build. Prior failed attempts remain
private diagnostics and are not promoted into passing results.

- [Consolidated results and source identities](../evidence/blocker-validation-2026-10-30.json)
- [Full suite log](../evidence/blocker-suite-2026-10-30.txt)
- [O1 compilation](../evidence/blocker-native-build-2026-10-30.json)
- [Native graph regression](../evidence/blocker-native-graph-2026-10-30.json)
- [Isolated compiler checks](../evidence/blocker-isolated-build-2026-10-30.json)
- [Isolated signed recovery](../evidence/blocker-isolated-recovery-2026-10-30.json)

Reproduce in fresh ignored output directories with independently verified tools
and a provisioned VM binding:

```powershell
$env:PATH = 'C:\Program Files\Git\ucrt64\bin;' + $env:PATH
$env:BYTEHOST_CRYPTO_TESTS = '1'
$env:BYTEHOST_NATIVE_INTEGRATION = '1'
$env:BYTEHOST_NATIVE_GRAPH = '1'
$env:BYTEHOST_NATIVE_DIRECTORY = '<ABSOLUTE_FRESH_O1_ARTIFACT_DIRECTORY>'
$env:BYTEHOST_XAX_REPOSITORY = 'D:\GitHub\XAX'
$env:BYTEHOST_BBC_EXECUTABLE = 'D:\GitHub\BBC\build\bbc.exe'
$env:BYTEHOST_XAX_EXECUTABLE = 'D:\GitHub\BBC\build\xaxc.exe'
$env:BYTEHOST_VM_TESTS = '1'
$env:BYTEHOST_VM_BINDING = '<ABSOLUTE_INDEPENDENTLY_PINNED_VM_BINDING_JSON>'
python -u -m unittest discover -s tests -t . -v
```

SDK observations do not become native authority by setting an environment flag.
The regression invokes the actual pinned native edit/verify/resolve/build tools;
there is no SDK build fallback. Optional evidence destinations must be new files.
