# Native byte-host migration slice

PARTIAL — both canonical XAX sources are verified, compiled, executed and scoped
tested. This slice replaces physical-EOF-sensitive packet construction, not the entire
process runner or Python host. The whole migration remains in LANGUAGE_MIGRATION.md.

The Windows platform component is a canonical XAX program. Its official
`xax-construct-v1` construction record is non-authoritative tooling data under
host/native/construction; the resulting `.xax` store is authoritative and later
changes require verified native workspace transactions. Initial graph creation
uses the existing external XAX SDK as compiler tooling, without adding a CUM
Python implementation, bootstrap script or runtime helper. Native verification
and compilation use the separately pinned XAX Windows compiler. SDK reference
verification alone is not recorded as native proof.

BF cannot distinguish a physical EOF read from a zero-valued data read through
its comma command. The XAX component calls the platform binary I/O APIs and uses
the actual return count. It never inspects a source language, chooses a CUM
transformation or interprets the supplied prefix/suffix.

## Binary contract

Input is two unsigned bytes (prefix length, suffix length), a little-endian u64
payload-byte budget, the exact prefix, the exact suffix, then raw payload through
physical EOF. Output is `prefix | (01 byte)* | suffix`. Prefix/suffix lengths are
format bounds, not compiler/tape limits. The byte budget is explicit; zero permits
only empty payload. The static 4 KiB allocation is control-plane scratch, with
constant memory use independent of the payload stream length.

No suffix is emitted on truncated metadata, input/output error or budget failure.
The parent must discard the entire response on nonzero process exit, including
any prefix already written. Exit 0 means completed transport, 3 input/truncation,
4 payload budget, 5 output failure, 6 allocation/binary-mode/cleanup failure.
Cancellation, wall/CPU/output budgets and process-tree cleanup belong to the
replacement native process runner and are not supplied by this stream component.

Existing worker records use a two-byte opaque prefix and zero suffix. The BF hex
codec uses prefix `b8 mode` and suffix `02 fe`. These operands remain data, supplied
by the BF workflow or trusted caller. Tests cover physical zero bytes, all 256
values, prefix/suffix boundaries, 64-bit budgets and every truncated header length.
The composed native test uses XAX transport and BF codec executables without any
owned foreign-language helper. Legacy Python integration and its retirement are
separate, still-unaccepted work.

The implementation uses standard `kernel32.dll` allocation/cleanup/exit and
`msvcrt.dll` binary I/O. Pointer-address exposure is used solely for an allocation
null check; no arbitrary address is dereferenced. The canonical verifier must
prove heap/view/effect lifetimes. This does not establish a sandbox or grant
authority to run untrusted project code.

## Response acceptance

A second canonical XAX component accepts `trailer_count:u8 | limit:u32le | raw
response through physical EOF`. A response must contain at least trailer_count
bytes and end with zero status. Only after the complete response is validated
does stdout receive the opaque trailer bytes (excluding status), followed by the
payload. With trailer_count 1 this returns just the payload; with 3 it returns
the existing worker's two opaque state bytes first. Unknown nonzero worker status
is preserved as Windows process exit `256 + status`, with no accepted output.

The admitted limit is 1..1,048,576 response bytes, an explicit bounded transport
capability matching the retained worker use case, not a permanent compiler or
application ceiling. Larger requested limits reject. The bound, opaque trailer
count and process budgets must be independently approved operands in the future
native host. Exit 3 means input error, 4 invalid/exceeded bound, 8 incomplete
response/trailer, 5 output error and 6 allocation/mode/cleanup failure. Cancellation
and tree termination are still outside this component.

The first component supplies EOF-correct input records; the second withholds all
response output until the worker's final status is known. Neither invokes Python
or Java. Native composition with a BF worker is the acceptance condition for
this slice. Full workflow, signatures, inventories, archives and process isolation
are still outstanding conversions. No foreign file is retired by a partial port.

## Executed checkpoint

The framer passed 22 direct vectors and response acceptance passed 21. Twenty
XAX-framer → BF-hex-codec → XAX-response compositions passed, including rejected
worker statuses with zero accepted output. A separate historical BF transform
composition produced source that compiled and emitted byte 1. That exposed
single-cell transformation gains no resistance claim from this result.

Both native XAX components rebuilt byte-identically from their canonical sources.
The Windows XAX seed is pinned in [evidence](../evidence/native-byte-host-2026-11-01.json).
The initial framer verified but failed native ABI compilation because its helper
returned two non-borrowed scalar values. The fix returns the read count and loads
the byte through the borrowed view. A native exact-root edit changed two functions
and their module/package entry references while preserving the write helper.
The first module-only edit retained the old package entry and still failed build;
the completed transaction passed verify, edit, verify, resolve and build.

The [replay manifest](../host/native/transactions/byte-framer-replay.json) pins the
base, native edit record and final authoritative store. The original framer
construction record describes the initial rejected build, not the corrected
source. Do not reconstruct it and silently replace the final graph. Native
verification alone is insufficient to infer ABI build success.

The multi-cell BF controller separately compiled at O1 and passed 24 protocol
vectors. These establish its response/state contract, not helper-chain semantics
or transformed application acceptance. The 88 scoped checks in this checkpoint
are not 88 full workflow tests. No CUM-owned foreign runtime/test helper was used;
the external SDK's initial graph-authoring dependency is disclosed above.

The [native trusted runner](NATIVE_PROCESS_RUNNER.md) now supplies a scoped
no-argument process service. General process lifecycle, workflow VM, storage, signatures, crypto invocation,
complete prepare and the remaining 94 tracked foreign sources remain outstanding.
No new recovery, signing, application measurement or release acceptance occurred.
