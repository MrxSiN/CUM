# Generic workflow instruction contract

The implementation of this complete instruction set is still legacy Python.
The new [native trusted runner](NATIVE_PROCESS_RUNNER.md) is a component service;
it does not execute these plans, authorize bindings or replace the VM. BF/XAX-only
full prepare remains blocked on the remaining host/services migration.

The [argument extension](NATIVE_ARGUMENTS.md) permits bounded standard-tool
invocations through BF-serialized arguments. It does not supply these workflow
instructions, authenticated bindings, native storage or complete prepare ordering.

The native BF planner receives exactly two physically supplied request bytes:
command and mode. Output is zero or more `(opcode, operand-id)` byte pairs followed
by one status byte. Nonzero status rejects the entire plan before side effects.
Unknown opcodes or missing operands are preflight errors. No JSON action graph is
accepted from a job binding. The small opcode/operand fields identify services and
bindings; they do not cap files, trees, source sizes or total byte-worker records.

| Opcode | Generic primitive |
|---:|---|
| 1 | Inspect pinned tool and optional repository identity |
| 2 | Capture explicit paths at an immutable Git commit |
| 3 | Verify a regular-file tree against its inventory |
| 4 | Pack an exact inventoried tree |
| 5 / 6 | Authenticated CMS encrypt / decrypt |
| 7 | Validate and safely extract an exact tree archive |
| 8 | Compare exact inventoried trees |
| 9 | Map an opaque native byte worker over explicit files |
| 10 | Execute a bounded process in a network-disabled container or VM |
| 11 | Produce canonical tree inventory |
| 12 | Bind declared record fields to explicit artifact digests |
| 13 / 14 | Sign / independently verify an exact byte record |
| 15 | Verify a tree and all declared record digest bindings |
| 16 | Ask pinned byte predicate to accept selected observed receipts |
| 17 | Atomically rename a new local staged tree |
| 18 | Copy and verify a regular tree |
| 19 | Assert declared fields/digests in an authenticated external record |
| 20 | Collect repeated isolated wall-clock samples |
| 21 | Apply a declared numeric interval to a measured record field |
| 22 | Select an observed service receipt for the later byte predicate |
| 23 | Copy and verify an opaque file |
| 24 | Invoke a pinned byte program and require exact response bytes |

On service failure, no later instruction runs and the private journal records
FAIL. Success receipts contain sequence, primitive, operand and observed wall
time. A receipt means that primitive succeeded; it does not establish unrelated
semantic, security or performance facts. BF selects exactly sixteen relevant
receipts for `gates.bf`, which requires a PASS byte for each. Missing evidence is
encoded as zero and refused. The BF plan places final rename after this predicate.

Bindings 44/45 authenticate and check a pre-capture owner scope/license/secret
review; binding 46 asks the BF language-admission program before capture.
Post-transformation bindings 24/25 independently authenticate the final review
bound to actual private scope and mapping report. These are different reviews.

The whole-flow journal prevents accidental reuse of the same operation file but
does not currently support transaction resumption. Byte-worker mapping has its
own authenticated restart protocol. Signed provenance verifies released content;
private workflow journals are operational diagnostics, not public trust anchors.

## Additional generic primitives

| Opcode | Service |
|---:|---|
| 25 | Invoke an explicitly pinned trusted external tool |
| 26 | Map opaque event-machine workers over declared files |
| 27 | Assemble BF-produced literal/copy recipes with opaque buffers |
| 28 / 29 | Nested BF workflow / BF-selected service dispatch |
| 30 / 31 | Append bound record / expected-digest file replacement |
| 32 | Capture explicit regular Windows paths with deny-write handles |
| 33 / 34 | Content-addressed cache store / retrieve |
| 35 / 36 | Collect measured fields / randomized isolated measurements |
| 37 / 38 | BF metadata predicate / BF measured-interval policy |
| 39 / 40 | BF-classified discovery / checked explicit file replacements |
| 41 / 42 | Owner-only storage / BF-selected public projection |
| 43 | Bundle pinned files and exact inventoried tool distributions |
| 44 | Run an independently pinned isolated capability policy |
| 45 / 46 | Stage exact Git blobs / audit committed tree and reachable blobs |
| 47 / 48 | Apply BF-produced directory metadata / filesystem preconditions |

Every planner binding supplies `planner_input_bytes`; there is no implicit BBC
capacity default. Normal command/mode records have two bytes. The budget flow
uses its separately validated complete request file. Unknown capacity is not
permission to truncate or guess a compiler ability.

Prepare authenticates capability operands 61/62, emits metadata 63 and creates
and checks a fresh Git namespace using 64..69 and clone operand 31. Trusted clean
recovery is 70, its output receipt 72 and safe result extraction 71. The sixteen
selected receipts include the clone history audit and isolated recovery. A service
failure always aborts, whether or not separately selected. Standalone recovery
retains its no-reference signature/decrypt/extract path.

Prepare invokes independent final-review operand 73 before authenticating the
scope-bound review, and recovery-policy operand 74 after clone audit. Their
argument vectors and script/configuration inputs must be independently pinned.
They supply real review artifacts; an exit code cannot replace review signatures
or independently checked content bindings. Dynamic policies use detached
signatures anchored outside the clone, or the existing independent hash method.

The explicit annotation planner emits `9/5, 26/1, 9/2, 12/4`: generic byte mapping,
event-machine mapping, byte mapping and digest-bound reporting. Its route request
emits `28/47`. BF owns the filter/layout/comment choices; the host merely executes
the pinned plan. The nested flow omits prepare's capture/review/sign/recovery
gates and cannot independently finalize a release. See
[annotated BF](ANNOTATED_BF.md) and the [operations guide](OPERATIONS.md).
