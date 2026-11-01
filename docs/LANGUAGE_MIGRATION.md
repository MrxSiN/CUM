# BF/XAX-only implementation migration

PARTIAL source drafting; language compliance is NOT ACCEPTED. The owner's latest
instruction replaces the Python-host exception. All CUM-owned executable code,
providers, tests and development scripts use genuine Brainfuck, with canonical
XAX where BF cannot supply a required capability. This also reaches the owned
Java helper and foreign executable fixtures. Full prepare, AI resistance, APK,
licensing and performance remain the active objective under this stronger rule.

The [tracked inventory](migration/foreign-source-inventory.json) records 94
outstanding files: 89 Python, three Java, one Kotlin and one PowerShell. These are
not completed ports. Ignored historical captures, keys, jobs and external compiler
dependencies are not relabeled as source. Moving, renaming, packing or deleting
old code merely to make an extension count look compliant is not conversion.
This is a tracked-source inventory, not a full filesystem count. Ignored owned
operational/authoring helpers also need conversion or retirement; archived
external dependencies and captured original projects must not be mistaken for
owned implementation or destructively swept up with it.

## Whole migration draft

1. Port byte/record primitives to BF with binary contracts and native hostile
   input fixtures: hex, length coding, canonical records, framing, collections
   and path policy. Preserve the old definitions as parity references.
2. Supply canonical XAX platform services for complete I/O, explicit argv,
   subprocess handles, environment isolation, budgets/counters, confinement,
   reparse rejection, ACLs and atomic publication. Eight BF commands alone do
   not expose OS calls. Native XAX-MCP demonstrates Windows APIs and isolation;
   its bounded sandbox is not CUM's full host contract. Use existing verified
   graph interfaces; do not invent textual XAX or edit a compiler to fill a gap.
3. Replace the Python CLI, transport/providers and generic workflow VM. Keep CUM
   decisions/transformations BF first and generic platform capabilities separate.
   Invoke standard cryptographic tools through XAX; retire the owned Java helper
   after equivalent native integration checks. Do not introduce another runtime
   language behind a BF/XAX entry point.
4. Port independent checks/attacks, tests, recovery guests, build and performance
   orchestration. Preserve independence, exact provenance and hostile-data
   handling. Remove Python from new recovery kits only after actual cold recovery;
   old kits retain historical evidence, not language acceptance.
5. Replace or retire foreign executable fixtures and scripts with BF/XAX cases.
   Do not hide Java/Kotlin/Python in JSON/byte arrays or claim an unsupported
   adapter is accepted. Configuration, protocol records and fixture bytes are data.
6. Rebuild/repin the complete host, check kit and offline kit. Then rerun full
   prepare, authenticated recovery, matched reconstruction, integrated protected
   APK, preferred-source/licensing and real application budgets. New publication
   still requires fresh approval; different-host recovery remains owner-deferred.

## First BF primitive

`src/hex_codec.bf` is genuine eight-command BF. It encodes binary bytes as lowercase
hex and decodes both ASCII hex cases, allowing ASCII whitespace between complete
byte pairs. Its wrapping-byte workspace is independent of stream length; no
whole-file byte counter or inherited compiler ceiling is introduced.

Request: `b8 | mode | (01 | byte)* | 02 | fe`. Mode 1 encodes and 2 decodes.
Response: transformed bytes followed by status: 0 accepted, 1 invalid data/framing,
2 unsupported mode. Discard all output on nonzero status. The native caller must
provide exactly one complete bounded request and enforce output/time/memory
limits. BF checks the final sentinel; it does not claim to distinguish suffix
bytes after it or raw physical EOF from a zero data byte. This is a new native
contract, not an already integrated Python-function replacement.

`tests/fixtures/hex-codec.json` drafts 24 native vectors: every byte, a 4 KiB stream,
both letter cases, whitespace, odd/invalid digits, binary NUL and truncated
transport. Standard operator commands may compile/run binaries and compare data;
no new foreign-language implementation or test script is stored in CUM. Existing
compiler and system utilities are explicit external dependencies.

The codec and multi-cell share controller were fully drafted before their native
checks. Their executed scopes are recorded below; neither supplies positive
resistance, APK or production acceptance.

## Executed codec checkpoint

After the source, fixtures and migration draft were written, native BBC O1
compilation succeeded and all 24 vectors passed. O0 declined with exit 5 and
`the native XAX backend does not support this program on the selected target`.
No dependency compiler was changed. Native output bytes and final statuses were
checked through standard operator commands; no legacy CUM Python/Java helper or
foreign test script was executed for this checkpoint.

The codec is written, compiled, executed and scoped-tested. It is not integrated
into a complete replacement native host, and no tracked Python file is retired. All 94
tracked foreign files remain outstanding, in addition to ignored owned helpers.
Application performance, full prepare, AI resistance, APK, licensing and offline
recovery are not accepted by this codec result. See
[execution evidence](../evidence/language-migration-2026-11-01.json).

## Native transport and ignored-helper checkpoint

Two canonical XAX platform components now provide physical-EOF framing and
complete worker-response/status acceptance. They passed 43 direct vectors, 20
compositions with the native BF hex codec and one historical transform composition.
Both rebuilt byte-identically. A native workspace transaction repaired the
framer's ABI after its initial build rejection; no compiler was edited. The
multi-cell controller compiled and passed 24 protocol vectors, without claiming
complete transformation semantics. See [native contracts](NATIVE_BYTE_HOST.md)
and [scoped evidence](../evidence/native-byte-host-2026-11-01.json).

An ignored-file audit found 980 foreign-extension files: 265 exact tracked-CUM
legacy copies, 260 exact external-checkout matches and 455 requiring provenance
review. These are identity categories, not a claim that every unknown file is
owned. One ignored one-time controller authoring generator was retired after its
authoritative BF output compiled and passed protocol checks; 454 unknown files
remain unretired. Detailed paths/hashes are private. Keys, captured originals and
historical recovery/compiler material were not swept up or deleted.

The 94 tracked files remain intact until whole-file parity. Transport components
are partial replacements, not a complete native CLI, runner, VM or crypto host.
Initial canonical graph creation used the external XAX SDK's official API as
development tooling; the native validation/build/composed runtimes used BF/XAX
executables and standard operator commands. No new owned foreign source file was
added. This distinction does not claim that all compiler development dependencies
have themselves been converted to BF/XAX.

## Native trusted process increment

`host/native/trusted_byte_runner.xax` now supplies a bounded no-argument worker
service with opaque binary input/output, explicit handle inheritance, empty
environment, job cleanup and measured wall/CPU/memory/input offset. Ninety-three
scoped cases and a separate supervisor-cancellation drill passed. The native CPU
correction preserved four helper identities and the executable rebuilt
byte-identically. The initial OS CPU enforcement failure and memory-probe trap
remain explicit observations. See [contract](NATIVE_PROCESS_RUNNER.md) and
[evidence](../evidence/native-process-runner-2026-11-01.json).

This is partial process.py coverage. Argument vectors, tool identity, caller
environments, large file streaming, reparse-safe storage and isolation adapters
are not ported. No untrusted build or production job uses the new runner. All 94
tracked foreign sources remain pending whole-file parity; native VM, providers,
complete CLI/test drivers and acceptance integrations remain outstanding.
