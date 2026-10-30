# Generic workflow instruction contract

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
| 10 | Execute a bounded, network-disabled container process |
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
