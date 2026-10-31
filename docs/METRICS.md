# Measurements and interpretation

The latest measurement checkpoint includes finite correctness-first O0/O1 process
samples, repeated BF transformations and transport/archive scale probes. See
[production-readiness measurements](PRODUCTION_READINESS.md) and
[their dated record](../evidence/production-readiness-2026-10-31.json). Earlier
single-process observations in `VERIFICATION.md` remain historical. No general
performance win or production budget acceptance follows from either checkpoint.

The fixture passed 258 behavior vectors per arm/optimization before fifteen
randomized paired process samples per optimization, after an untimed warmup.
Approximately 23 ms medians include process startup and the host's 10 ms polling;
they cannot establish zero overhead. Fifteen actual BF transforms had identical
output identities and a median operation time of 1.823 seconds. Mapping through
1,049,600 bytes tested binary ignored text with three commands, not a million
instructions. Exact 1,024-file archive recovery was a storage probe, not a full
release at that scale. The interfaces below retain their explicit counter scopes.

`ResourceSample` records Windows selected-process peak working set, peak pagefile
use, page faults and user/kernel CPU using the documented native process APIs.
It excludes descendants and explicitly reports BLOCKED when counters cannot be
queried. `process.run` returns these alongside wall time and process status.
`machine.transduce` records host-visible elapsed time, native process wall-time
sum, native CPU sum and maximum native-process working set for the current
invocation. Resumed invocations are separately scoped; do not present one attempt
as the total operation's cost.

The API contracts were checked against Microsoft's documentation:
[GetProcessMemoryInfo](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo),
[GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes).
Reading an API reference is not executing or verifying this implementation.

Inside a fresh Linux cgroup-v2 container, `host.providers.cgroup_run` collects real
CPU delta and `memory.peak`. That peak includes the entire container since its
creation, including the measurement/check harness; it is not a subtraction or
estimate of application-only memory. The generic isolation service can persist
this observation outside the container with `measurement_report`. Use one fresh
container per sample, a pinned image and reviewed measurement/check harnesses.
Container counters are not native Windows process measurements.

`metrics.paired` randomizes two or more explicit isolated arms and preserves raw
samples, execution order, median, range and population standard deviation. It
requires prior actual correctness evidence. Cold/warm policy and startup behavior
must be identified in context; the harness does not invent a cache flush.

`metrics.collect` binds each required numeric value to its source-record digest.
Missing values fail. `guards.measured_predicate` asks the BF budget program for
apply/skip/reject decisions. Skip is a separate outcome and never satisfies a
required apply result or structural release gate. Owner-selected limits are
transparent job budgets, not global source/graph capacity constants.

Required records cover transformation, archive/encryption, compilation,
behavior/audit, signing/provenance, clean recovery and end-to-end release time.
The workflow receipts record each primitive's elapsed cost. Application startup,
runtime, CPU, memory and binary/source sizes require their own explicitly scoped
samples. A cheap verification result cannot stand in for any of these metrics.

Further resource-exhaustion, counter-integrity and representative repeated
compilation/full-release checks remain open. The Android compiler budget failures
are failed build attempts, not successful build-time samples or comparative
performance results. Production budgets and advanced resistance remain unaccepted.
