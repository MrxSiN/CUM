# Private operating procedure draft

This procedure has not been executed. Example JSON files contain deliberately
invalid tool digests, image identities and review values. They must fail until
bound to real independently verified materials. Do not replace missing evidence
with a successful exit code or an edited PASS string.

## Workspace and identities

Use an owner-controlled workspace with restrictive Windows ACLs. The Python host
does not provision Windows ACLs, wipe SSD sectors or protect against a local
administrator. Keep keys, plaintext captures and opaque checkpoints outside
public staging and all untrusted mounts. Retain encryption and signing identities
separately; a checkpoint HMAC key is a third, unrelated secret.

Supply existing, established OpenSSL-compatible recipient certificates/identities
and Ed25519 signing identities. Provision keys outside untrusted build containers.
The examples contain paths only and do not generate or transmit credentials.
Encrypted identities may require a separately provisioned noninteractive key
provider; unattended encrypted-key prompting is not implemented in this draft.

Retain independently: recovery identities, signer SPKI trust fingerprint, recovery
certificate, compiled BF planner, generic recovery host, Python/OpenSSL, required
public compilers, tool digests, job operands, formats and instructions. A signer
key copied from an untrusted release is never its own trust anchor.

## Explicit immutable capture

The implemented capture domain is a full immutable Git commit plus an explicit
list of relative source/resource paths. Mutable/untracked worktree data, Git
history, submodules, symlinks, junctions, ACLs and alternate data streams are not
captured. Git export attributes apply. Review the materialized scope manifest;
it defines exactly what can be restored, including regular bytes and directories.

Commit IDs must be full immutable identities. The host checks commit resolution,
rejects selected gitlinks/symlinks, exports from Git objects, validates paths and
then inventories the captured tree. Transformation and reference compilation read
this captured tree, never the live developer worktree.

This is narrower than the master's eventual general development-workspace scope.
If development depends on omitted metadata, generated files or submodules, reject
the operation or use a future explicitly supported capture provider. Never call
the current exporter a complete Git repository backup.

## Job operands

Copy example operands into ignored `private/`. All paths are explicit. Hash and
pin native tools before use. The selected compiler's documented capacities are
not verified just because the example repeats them. Supply actual native transport
and semantics evidence in the authenticated owner review.

Map every source file that is meant to be protected. Unmapped resources/build
inputs are copied byte-for-byte. A signed confidentiality/scope review must reject
unintended plaintext implementation files. No host extension classifier silently
decides whether a file is a source file.

Create report directories and an independently provisioned container image/tool
directory. The image must contain pinned BBC, Wine if used, Python, host and
independent checker dependencies. No image pull/network is allowed by the runner.
The example mounts are illustrations of the declared test scopes, not proof that
the machine has an operational container service. Supply exact check bindings
for each case, correct tool hashes, report paths and held-out binary inputs.

## Prepare order owned by BF

`cum.bf` emits the following service order for command 3:

1. Inspect pinned tools and required isolation infrastructure.
   BF first checks language admission; authenticate and check the pre-capture
   owner scope/license/secret review before exporting any selected source.
2. Export the declared immutable committed scope and verify its inventory.
3. Archive the exact scope, encrypt, decrypt internally, safely restore and compare.
4. Copy captured public/build inputs to an isolated candidate and map explicit
   source paths through the native BF transformer.
5. Execute independent build, behavior, normalization, boundary and budget checks.
6. Authenticate the owner review and bind it to the actual captured scope and
   transformation report. Licensing, secrets, host review and memory evidence
   cannot be invented by the host.
7. In public mode, copy the authenticated encrypted capsule into the candidate.
8. Freeze the protected inventory, compose a bound manifest and sign it.
9. Independently verify signature, inventory and capsule digests.
10. Make a public-style clean artifact checkout, verify again using independent
    trust, decrypt/restore using retained identity and compare the captured scope.
11. Run a restored-development build check without mounting the capture or keys.
12. Supply 16 actual receipts to the BF evidence predicate. Only acceptance permits
    atomic local finalization. Flow journal/readiness information stays private.

No publication step exists. Failed preparations leave a non-ready private
candidate/journal for diagnosis; failed temporary extraction stages are removed.
The live developer tree is not changed. Interrupted workflow transactions must
use a fresh operation; byte mapping alone supports authenticated restart.

## Public capsule and private vault

For public mode (1), the candidate includes `capsule.cms`. It is excluded from
the protected-file inventory and separately bound by its digest in `release.json`.

For private-vault mode (2), BF omits the capsule copy instruction. Before running,
change binding 27 recovery_mode to `private-vault`, point its recovery capsule
digest operand to the independent vault file, remove `capsule.cms` from binding
26 exclusions, change the expected recovery_mode in bindings 30/33, and adjust
bindings 30/33/34 to the retained vault capsule. The
public-style checkout must contain no plaintext originals or private vault file.
A public clone alone cannot recover this mode. Back up the vault independently.

## Inventory and signature trust

Paths are NFC POSIX relative strings, sorted by UTF-8 bytes. Records contain entry
type, mode, file size and SHA-256. JSON is sorted-key, ASCII-escaped, compact, with
one LF. Unknown/colliding/unsafe paths and unsupported types reject.

The protected inventory excludes exactly the configured manifest, detached
signature, inventory record itself and, in public mode, capsule. The inventory
record is separately hashed in the signed manifest, as is the capsule. The
manifest/signature are never included in their own digest. No readiness marker
is written into the public tree. All remaining files, including extras, must match.

OpenSSL signs exact manifest bytes. Verification checks the external signer SPKI
fingerprint, signature, inventory digest and all bound artifact digests. Keys
bundled with downloaded artifacts are not automatically accepted.

## Recovery-only operation

Use command 5 with a fresh private binding/journal and an existing public release
or independently retained vault capsule. Bind 32/33 to those public files and
independent trust; bind 34 to the retained recovery identity and certificate;
bind 35 to a **new** destination. This path does not call capture, transformation,
compiler, source comparison or a mutable developer directory.

Command 6 additionally uses a separately retained expected captured scope for
byte/metadata comparison and performs the development fixture check. Distinguish
this recovery drill from merely decrypting an unsigned archive. The internal
pre-signing round trip and final trusted signed checkout drill are separate.

An independently retained tool package is required for disaster recovery. Capsule
exposure is permanent once public; later key compromise may disclose old source.
No key compromise recovery or secure-erasure guarantee is implemented.

## Licensing and public independence

The owner review must identify actual first-/third-party obligations and preferred
editable source requirements, plus distribution classification. The host only
authenticates that review; it does not fabricate a legal determination. Preserve
all required notices and independently buildable source inputs. Omitted or
incompatible obligations prevent signing/finalization. Publication requires a
separate explicit owner instruction, including review of existing public history.
