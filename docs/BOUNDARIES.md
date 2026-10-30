# BF and generic host ownership

| Decision/service | Owner |
|---|---|
| Command plan and release ordering | `src/cum.bf` |
| Profile selection and pass order | BF planners, routes, policies and machine kernels |
| Source-byte recognition and eligibility | BF workers, machine kernels and graph recipe |
| All protected instruction/source emission | BF workers, machine kernels and graph recipe |
| Meaning of the two worker-state bytes | BF worker |
| Every mandatory-evidence acceptance decision | `src/gates.bf` |
| Supported language admission | `src/adapters.bf` |
| Path validation, bytes, trees, atomic storage | Generic host |
| Physical record completeness and process transport | Generic host |
| Opaque checkpoint authentication and storage offsets | Generic host |
| Generic VM instruction execution | Generic host |
| Numeric measurement/threshold comparisons | Generic host, thresholds are explicit operands |
| BF compiler optimization/native emission | Existing BBC/XAX |
| Authenticated encryption/decryption, signing | Existing pinned OpenSSL |
| Isolation | Existing pinned container engine/image |
| Licensing/confidentiality judgments | Independent owner review, authenticated and scope-bound |

`host/bytehost` contains no BF token filter, source-language parser, pass selector,
camouflage emitter, XAX mutation generator, or extension-based adapter selector.
It can map any pure native byte worker over explicit owner-supplied file operands.
The owner declares project paths and required tools; these are not secretly
discovered by a non-BF language adapter. All source analysis remains in BF.

The workflow VM's instructions come only from a pinned native BF planner. A job
binding supplies paths, budgets, compiler argument vectors and independent trust
anchors; it cannot supply a replacement action list. The trusted operator still
has power to choose a dishonest verifier. Code cannot establish trust in an
arbitrary owner-configured executable merely because that executable exits zero.
Pin and inspect verifiers, and retain their actual reports independently.

## Compliance experiment to execute after drafting

1. Build `echo.bf`, `transform.bf` and `tests/workers/fixed.bf` natively.
2. Run the exact same generic exchange/map host with each pinned component.
3. With fixed BF, every request returns only `FIXED`, plus the declared trailer.
   No source-dependent camouflage may appear in the host output.
4. With real BF, run eligible arithmetic/I/O/loop fixtures, verify emitted source
   against independent BF interpretation and compile both through BBC O0/O1.
5. Exercise complete binary frames, zeros, every truncation, error propagation,
   and authenticated multi-process continuation. Repeat across chunk boundaries.
6. Inspect the host implementation for source-sensitive branches. Retain source
   identities, command vectors and observed results; do not record a plan as PASS.

The initial fixed-worker experiment alone does not prove a functioning source
transformation or analysis resistance. Status here is NOT STARTED.

## Application source audit notes

The `.bf` files contain only executable BF characters and whitespace. Human
annotations are separate documents so punctuation cannot accidentally execute.
There is no committed foreign-language generator for the BF implementation.
Source files were placed by editing tools, like other source files; those tools
are not runtime dependencies. The generic reference interpreter lives in tests.

The host is Python and uses platform services. Calling CUM or its dependency
pipeline entirely foreign-language-free would be false.


The XAX query provider invokes the existing pinned SDK for explicit observations.
Its legacy Python inspection dependency is declared; it does not author CUM
mutations or compile protected graphs. Exact Git bytes/modes/object enumeration
are generic host services; private selection/rejection remain BF. Clean recovery
ordering is `clean_recovery.bf`; backup/distribution/publication are
`maintenance.bf`. No BBC/XAX implementation was edited for this draft.
