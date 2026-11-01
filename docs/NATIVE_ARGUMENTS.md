# Native argument integration

PARTIAL. The BF serializer, backward-safe trusted-runner extension and independent
CRT probe are compiled, executed and scoped-tested. Their source and fixture
drafts preceded native checks. This is not complete process.py or prepare parity.
XAX-MCP's checked local executor still lacks stdin/argv; it is not modified here.

## BF ownership and wire contract

`src/windows_args.bf` serializes arguments using ordinary Microsoft wide-CRT
quoting. BF can perform this byte transformation; XAX only transports the result
and invokes Windows process APIs. The quoter never selects an executable or a CUM
transformation. Its request is `b9 | arguments | 02 fe`, where each argument is
`01 | (01 low-byte high-byte)* | 02`. UTF-16LE NUL and unpaired surrogates reject.
The response is UTF-16LE serialized arguments, excluding argv[0], followed by one
status byte. Status 0 accepts, 1 rejects malformed data, 2 rejects a slash run
exceeding the serializer's two-byte counter. Discard every output byte on rejection.
The caller supplies exactly one complete bounded request; BF does not certify
physical EOF or reject arbitrary suffix bytes after its final sentinel.

Every argument is quoted, including empty strings. A backslash run is emitted
unchanged before ordinary characters, doubled before a closing delimiter, and
doubled plus one escaping backslash before a literal quote. Spaces separate
arguments outside quotes. The two-byte run counter must work beyond 255 slashes.
This is an execution ABI serializer, not a shell or general source adapter.

## Runner extension

Keep NRQ1 byte-for-byte compatible. NRQ2 uses the same 64-byte header and five
paths, with a u16 serialized-argument unit count at offset 50; bytes 52..63 remain
reserved zero. The exact UTF-16LE argument segment follows the five path strings.
The segment comes from an independently accepted BF serializer response, without
its status byte. The native service treats it as trusted serialized argument data;
it is not itself an argv parser or proof that BF produced those bytes.

The runner appends that segment to its quoted, independently pinned executable
path. It retains a separate CreateProcessW application name, empty environment,
explicit stdio handles, job cleanup and resource checks. No shell/PATH lookup or
new authority is added. All metadata, segment bounds and physical EOF are checked
before files or child processes are opened. Embedded NUL rejects.

The current command buffer admits at most 4097 UTF-16 units excluding its NUL,
including the quoted executable, separating space and serialized arguments.
This explicit prototype transport bound is smaller than the Windows API maximum;
it is not a compiler/project limit or a claim of general process.py parity.
Future callers must honor this capacity and pin/approve executable and paths.
Untrusted builds still require a separate verified isolation boundary.

The canonical store changes only through an exact-root native transaction,
retaining unchanged helper identities. Construction carriers remain tooling data.
Draft the probe, fixture vectors and complete change before native checks.

## Acceptance scope

Predeclare binary fixtures for empty vectors/arguments, whitespace, quotes,
ordinary/trailing/quote-adjacent backslashes, Unicode/surrogates, malformed input,
truncation and long slash runs. Compare against declared serialized bytes, then
round-trip actual child argv using an independent native wide-CRT probe.

Run NRQ1 regressions, NRQ2 framing/budget rejections, preservation of existing
files, CPU/wall/output handling and cancellation. Invoke the pinned native XAX
compiler with real arguments on synthetic CUM-owned input. Record separate
compiled/executed/tested states, failed attempts and source/tool identities.
Do not run legacy Python CUM for this checkpoint or count a compiler verify as a
full prepare/APK/license/recovery/performance acceptance. Publication requires
separate explicit owner approval.

The probe calls the system CRT's `__wgetmainargs` with wildcard expansion off.
It copies only an in-range CRT argv-array entry into owned memory, then uses
standard length/copy APIs for that OS/CRT-owned string. It reports argc and exact
UTF-16 argument bytes; it does not share the BF quoting implementation. See
[Microsoft argument parsing](https://learn.microsoft.com/en-us/cpp/c-language/parsing-c-command-line-arguments)
and [the wide startup API](https://learn.microsoft.com/en-us/cpp/c-runtime-library/getmainargs-wgetmainargs).

## Executed checkpoint

- 32 native BF vectors passed, including rejection of malformed/NUL/unpaired
  surrogate input and 300-byte backslash runs without an eight-bit counter wrap.
- All 19 valid vectors round-tripped through the independent wide CRT, comparing
  argv[0], every argument length and exact UTF-16 bytes.
- All 93 NRQ1 regressions passed with the updated runner. Seven NRQ2 metadata,
  NUL, truncation, trailing-data and capacity rejection cases passed.
- The exact 4097-unit command boundary round-tripped; oversized commands reject.
  Supervisor-only cancellation under NRQ2 terminated the child and removed temps.
- A native exact-root transaction changed only main, retaining four helpers.
  Verify/edit/verify/resolve/build and byte-identical rebuild passed; applying the
  edit again rejected its stale root. Earlier NRQ1 source is retained exactly in
  the arguments transaction base, not silently rewritten as new evidence.

The pinned native XAX compiler verified a CUM-owned synthetic graph at a path
containing spaces, using arguments emitted by the BF serializer. OpenSSL 3.6.5
also accepted its `version` argument through this path. These are actual standard
tool invocations; neither performs protected application acceptance.

The first compiler invocation failed with child 0xC000001D under a 2 GiB memory
limit. A separately declared 4 GiB capacity probe succeeded, with 3,559,272,448
bytes of job-reported peak process memory. The original budget remains failed;
this is not a revised passing compiler/application performance gate. Do not equate
that job counter with resident working set. No compiler was edited or unconfined
fallback substituted for the bounded invocation.

Initial operator checks were corrected for early broken-pipe rejection, absent
measurement headers and drive-prefix path normalization. Actual failing child
and resource observations remain in [evidence](../evidence/native-arguments-2026-11-01.json).
The [replay manifest](../host/native/transactions/trusted-byte-runner-arguments-replay.json)
pins the exact base, edit record and resulting store.

The slash-counter overflow branch beyond 65,535 consecutive slashes was not
executed; the native command contract admits far less. A full native test driver,
workflow VM, executable/path pinning service, custom environments, safe large-file
publication and untrusted isolation adapters remain outstanding. All 94 tracked
foreign files remain until whole-file parity. No new AI, APK, licensing/relinking,
recovery, signing, application-performance or production acceptance is claimed.
