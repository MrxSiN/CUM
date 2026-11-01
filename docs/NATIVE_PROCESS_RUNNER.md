# Native trusted byte-worker runner

PARTIAL. The source is natively verified, built and scoped-tested. This is a
generic Windows platform service for an explicitly pinned, trusted no-argument
byte worker. It is not the workflow VM or a sandbox for untrusted project builds.
BF cannot create OS processes or inspect physical file handles; canonical XAX
owns those capabilities. CUM language recognition and policy remain in BF.

## Complete increment scope

Draft the canonical runner, construction transport, BF/probe fixture sources,
data vectors and this contract before native checks. Retain the existing transport
components and all legacy process code until whole-interface parity. The new
runner does not implement arguments, custom environment, shells, untrusted code,
network confinement, snapshot capture, reparse-safe path traversal, executable
digest checking, atomic publication or the full host. Unsupported requests reject.
The caller must independently pin the executable and approve regular non-reparse
paths in a private owner-only workspace. No production job uses this prototype.

Request is a 64-byte little-endian header followed by five UTF-16LE strings,
without terminators, then exact physical EOF. Header fields:

| Offset | Field |
|---:|---|
| 0 | Four bytes `NRQ1` |
| 4 | Reserved u32 zero |
| 8 | Positive wall budget in milliseconds, u32 |
| 12 | Reserved u32 zero |
| 16 | Combined stdout/stderr budget in bytes, u64; zero permits no output |
| 24 | Positive per-process user CPU budget, in 100 ns units, u64 |
| 32 | Process memory budget in bytes, u64, at least 1 MiB |
| 40..49 | Five u16 string lengths: executable, cwd, stdin file, stdout temp, stderr temp |
| 50..63 | Reserved zero |

Each string has 3..4095 UTF-16 units and a drive-absolute prefix. Embedded NUL,
quotes and additional colons reject. The explicit path bound is a prototype
transport capability, not a project/compiler size limit. UNC paths and child
arguments are unsupported. The executable is supplied separately to CreateProcessW;
its only command-line token is the quoted executable path, with no shell lookup.

All metadata is accepted before opening files. Stdin is read-only and denies
writers. Output files use CREATE_NEW, exclusive access and delete-on-close;
existing files must never be overwritten or deleted. The inherited handle list
contains only those three handles. The child receives an empty Unicode environment.
It starts suspended in a new job through the job-list process attribute, with
kill-on-close, one active process, explicit CPU and memory limits; membership is
checked before resuming. Unsupported job/attribute operations fail closed.

The parent samples combined output size and wall time while waiting. Temporary
disk output can overshoot between samples; no hard instantaneous disk quota or
untrusted-code containment is claimed. After termination it rechecks output,
waits for job cleanup and records actual exit, CPU, peak memory and stdin offset.
It never accepts truncated captured output as a successful worker response.

Response is `NRR1`, child exit u32, flags u32, reserved zero u32, then seven u64
values: wall milliseconds, user CPU 100 ns, kernel CPU 100 ns, job peak process
bytes, stdin file offset, stdout length and stderr length. This 72-byte header is
followed by exact stdout and stderr. Flag 1 means wall timeout, 2 output budget
and 4 sampled user CPU exceeded. Flagged runs return no payload. The caller must
reject nonzero flags/child exit
before interpreting any byte-worker status. API/setup/measurement/cleanup failures
exit nonzero and require discarding all stdout. Streaming response-write failure
may leave a prefix and is never success.

Required checks: binary/EOF input, exact/zero output bounds, failed child exit,
empty inherited environment, wall timeout, output flood, file preservation,
malformed/truncated/trailing metadata, missing files, cleanup and composition with
the BF codec. Native verifier/build results, timing samples and application budget
acceptance are separate evidence. No APK, AI, license or release gate is implied.

The process setup follows the standard
[CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw),
[attribute list](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
and [job limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
interfaces. Actual execution must establish which declared capabilities work on
the pinned host; documentation of an API is not execution evidence.

The finite BF output-budget fixture emits 2,048 NUL bytes. Its first infinite BF
form returned BBC child status 2 without output; it cannot establish the runner's
output limit. An infinite-loop XAX probe also verified but its native build
returned 1 without an artifact. Those attempts remain private failure records;
neither is admitted as an executed output-budget check. The finite BF fixture
avoids introducing another platform implementation for this test.

The first CPU-limit exercise exceeded its requested CPU allowance and reached
the wall timeout despite successful job configuration. The corrective draft adds
explicit process-user-time samples and final CPU/wall rechecks; OS job limits
alone are not treated as sufficient bounded-runtime evidence. Native edits must
retain unchanged helper objects and verify/build the updated graph before tests.

## Executed scope and remaining checks

The corrected runner passes 93 scoped cases, including every header truncation,
binary BF input/output, split binary stdout/stderr, exact combined output bounds,
file preservation, empty selected environment variables, wall and sampled CPU
termination. A native exact-root transaction changed only main and preserved all
four helper identities. Native verify/edit/verify/resolve/build passed, followed
by a byte-identical rebuild from the authoritative store. The initial construction
record is historical; the CPU transaction supplies the current graph change.

The memory probe initially expected a graceful denial code, but observed
0xC000001D under 64 MiB. The same executable allocates/frees 128 MiB and returns
its success-control code under 256 MiB. The repeated limited-budget trap is
recorded explicitly; graceful allocation-denial handling remains unaccepted.
CPU and wall limits are sampled and can overshoot. These are process observations,
not accepted application performance budgets or new AI-cost requirements.

The additional cancellation drill passed: killing only the supervisor after its
child started terminated that child and removed both temporary output files.
The test did not use a process-tree kill to establish this result. Cancellation
during CreateProcessW, host crashes, disk exhaustion and every API fault point
remain independent, unexecuted coverage. No production input is admitted.

The final run observed wall termination at 109 ms for a 100 ms request and CPU
termination at 1,093,750 user CPU ticks for a 1,000,000-tick request. These include
sampling/accounting granularity; they are not hard instantaneous limits. Native
measurements distinguish wall, user/kernel CPU, peak process memory and shared
stdin file offset. They do not establish the target application's budgets.

See [scoped evidence](../evidence/native-process-runner-2026-11-01.json) and
[transaction replay](../host/native/transactions/trusted-byte-runner-replay.json).
The external XAX SDK supplied initial construction and changed-function tooling;
native XAX performed verification, editing, resolving and builds. Checks used data
fixtures and transient standard PowerShell/.NET operator commands. No foreign
source file was added, but a complete native test driver remains migration work.
This does not retire process.py: argv, pinning, environments, large file output,
isolation adapters and the complete legacy interface still need parity.
