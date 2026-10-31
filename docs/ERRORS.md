# Diagnostic contract draft

The generic CLI writes canonical JSON. A successful primitive is PASS only for
that primitive, not a product/release claim. Rejection exits 1 with a HostError
record; malformed operand, OS/resource or unexpected service failure exits 2.
Compiler and worker exit codes are retained in structured error details.
Binary primitive stdout/stderr are returned as `stdout_hex`/`stderr_hex` in the
success JSON. Conflicting pre-existing hex fields reject as FORMAT; no lossy text
decoding substitutes for the bytes. Diagnostics remain separate from a successful
artifact or release claim.

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
| PROCESS_START / PROCESS_EXIT / PROCESS_TREE / TIMEOUT | Launch, process-status, tree-cleanup or execution-time failure |
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
| VM_BOOT / VM_JOB / VM_TRANSPORT / VM_TRUNCATED | VM readiness, execution, transport or incomplete response failed |

Diagnostic logs, absolute paths, request states and review records are private by
default. They are not public release inputs. OS disk/allocation/address-space
failures must remain failures; no truncation/fallback may produce a ready marker.
If stage cleanup also fails while handling a HostError, its original code remains
and `details.cleanup_failure` identifies the remaining stage and cleanup reason.
This is private diagnostic material, not a successful restoration receipt.

The Android checkpoint distinguishes native-backend exit 5 from VM transport
TIMEOUT and a compiler controller's exit 124. The controlled 900/600-second runs
passed source verification and expired during unsigned lowering. They produced no
APK; neither a semantic rejection nor a permanent compiler capacity follows from
that timeout. See [the executed record](ANDROID_READINESS.md).
