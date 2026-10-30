# Diagnostic contract draft

The generic CLI writes canonical JSON. A successful primitive is PASS only for
that primitive, not a product/release claim. Rejection exits 1 with a HostError
record; malformed operand, OS/resource or unexpected service failure exits 2.
Compiler and worker exit codes are retained in structured error details.

| Error | Meaning |
|---|---|
| PHYSICAL_EOF | No physical record was supplied |
| TRUNCATED | Physical EOF before declared record completion |
| FORMAT / CMS_FORMAT / SIGNER_FORMAT | Unknown, incompatible or malformed artifact |
| HEADER_BUDGET / PAYLOAD_BUDGET | Outer record exceeds negotiated policy |
| INPUT_CAPACITY / OUTPUT_BUDGET | Selected native transport/output does not fit |
| WORKER_REJECT | BF rejected eligibility/profile; discard all emitted prefix bytes |
| WORKER_RESPONSE | Missing or malformed native response trailer |
| RECORD_LENGTH | Physical request does not match the byte-program ABI |
| PROCESS_START / PROCESS_EXIT / TIMEOUT | Launch, process-status or execution-time failure |
| TOOL_IDENTITY / TOOLCHAIN_COMMIT | Pinned native executable or repository changed |
| INTEGRITY / CHANGED | Bytes/tree differ or input changed during work |
| REQUEST_BINDING / STATE_BINDING | Wrong operation, sequence, source, worker or configuration |
| STATE_AUTH / STATE_OUTPUT / STATE_KEY | Invalid checkpoint authentication/output/key |
| REPLAY / ORPHAN | Completed/reused operation or unjournaled partial output |
| PATH / REPARSE / TYPE / COLLISION | Unsafe or unsupported path/entry |
| EXISTS / DESTINATION | Refuse unexpected overwrite or in-place processing |
| TRUST_ANCHOR | Signer does not match independently trusted SPKI |
| REVIEW / REVIEW_BINDING | Missing review or review for different captured inputs |
| SEMANTICS / NORMALIZATION / STRUCTURAL | Independent correctness/protection gate failed |
| EVIDENCE / BYTE_ASSERTION | BF decision component refused request/evidence |
| BUDGET / RESOURCE_BUDGET | Explicit owner budget exceeded |
| RECOVERY_MISMATCH | Restored captured scope differs |
| SERVICE_FAILURE | Unexpected service exception; never a success |

Diagnostic logs, absolute paths, request states and review records are private by
default. They are not public release inputs. OS disk/allocation/address-space
failures must remain failures; no truncation/fallback may produce a ready marker.
