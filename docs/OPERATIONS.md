# Operating procedure and acceptance limits

One restricted synthetic BF project completed the actual prepare workflow;
see [the release checkpoint](SYNTHETIC_RELEASE.md). Current annotation/native/device
results and remaining gates are in [status](STATUS.md). The procedure below is
not production accepted for arbitrary projects or an integrated protected APK.
The human `app` command parser and numeric BF workflow planner now build at O1.
Example bindings contain
invalid executable hashes, image identities, trust anchors and capacities. They
must fail until bound to independently reviewed real materials. Never manufacture
PASS records to advance a workflow.

## Prepare tools and private storage

1. Use a new owner-controlled private directory. The separate generic directory
   service can create owner/System Windows ACLs or POSIX 0700; it does not protect
   against administrators, repair existing permissions, or guarantee secure erasure.
   `config/private-storage.example.json` supplies operands. Keep originals, keys,
   journals, job bindings and reports outside public staging.
2. Retain separate CMS recovery, Ed25519 signing and checkpoint-HMAC identities.
   Provision keys outside build containers. Back up identities and signer SPKI
   fingerprints independently. No key generation or external upload is automatic.
3. Review BBC/XAX source and installed executable identities. The compiler build
   interface is `bbc.exe compile windows-x86_64 -O1 <output>` with source on binary
   stdin. The host invokes argument vectors directly; no PowerShell text pipeline
   handles application input. XAX uses its existing inspect/edit/verify/resolve/build
   file interface. No compiler fallback or invented XAX syntax is supplied.
4. Bind an ignored copy of `config/build.example.json`, then later invoke
   `python -m host.bytehost.build private/build.json`. It lists all BF sources and
   fixed-response workers. The current inventory has 44 matched O1 components:
   three fresh builds and 41 retained matching source/artifact identities at the
   latest checkpoint. This is not a claim that all 44 were rebuilt in that run.
   Probe other required configurations into different new output directories;
   O0 still declines the command parser. Record failures without changing BBC/XAX.
5. Provision reviewed, digest-pinned container images and public compiler tools.
   Images are never pulled by the runner. The normal build image has no identities
   or plaintext archive. The distinct trusted recovery image has only the public
   clone, independently retained runtime, recovery identity/certificate, signer trust,
   exact recovery binding and empty output mount. Neither image is available merely
   because a JSON example describes it.

   On this Windows host the alternative generic QEMU backend supplies a disposable
   VM without a guest NIC or host shares. See `BYTEVM.md` for provisioning, pins,
   output capabilities and the independent recovery policy. A provisioned and
   tested VM does not itself approve the whole release procedure.

`config/capabilities.example.json` separates requirements from observations. Fill
observations only after actual native probes. Sign the independent
`toolchain-review.json`; the BF plan verifies this review before capture. Runtime
input/output capacities are required verified per-process byte budgets, not
permanent BBC constants. Null `integer_limit` requests no host integer ceiling;
it does not certify the target tape or permit accepting unsupported programs.

## Bind a release operation

Copy `public-job.example.json`, `private-vault-job.example.json`, or the restricted
language job into ignored private storage. Every path, disposition, source mapping,
tool pin, independent verifier, resource budget and review must be explicit.
CLI profiles/project paths are supplied through these operands; the proposed
master-prompt positional/flag interface is not implemented.

The current command surface is:

```text
python -m host.bytehost app private/job.json doctor
python -m host.bytehost app private/job.json toolchain inspect
python -m host.bytehost app private/job.json prepare --mode 1
python -m host.bytehost app private/job.json verify
python -m host.bytehost app private/recovery.json recover
python -m host.bytehost app private/drill.json test-recovery
python -m host.bytehost app private/job.json benchmark
python -m host.bytehost app private/job.json audit
```

`command.bf` parses those exact command strings. `cum.bf` chooses instructions;
JSON supplies operands, not an alternate workflow. Use a new journal per command.
Mode 1 prepares a public capsule; mode 2 uses private vault operands. An interrupted
whole flow needs a new operation; only byte-worker mapping has authenticated restart.

## Capture and transform one authoritative scope

Git capture uses a full immutable commit plus explicit paths; export attributes
apply. Windows directory capture uses explicit regular paths and deny-write file
handles. Select the provider through the BF snapshot request and bind its matching
owner scope review. Directory capture is not an atomic filesystem-wide snapshot;
all declared files must be locked and scope consistency checked. Relevant empty
directories and supported permission bits belong in the manifest.

Links, junctions, reparse points, devices, submodules, ACLs, ADS and hardlink identity
are unsupported, not silently preserved. Git history is outside the recovered
source scope. XAX graph/workspace/evolution/dependency files needed for development
must be explicitly included and independently reopened after recovery.

The BF prepare plan:

1. Admit the restricted adapter, inspect tools, authenticate capability and
   scope/license/secret reviews, then capture and verify the immutable scope.
2. Pack/encrypt the capture; internally decrypt/extract/compare before any signing.
3. Project approved public build inputs into reference and candidate trees. Read
   transformation inputs from the capture. Recovery-only entries remain excluded.
4. Dispatch real BF transformations; independently build, check behavior, normalize,
   enforce measured budgets, and authenticate the scope-bound final owner review.
   A skip may restore original bytes but never bypass a structural acceptance gate.
5. Copy ciphertext into public mode only. BF emits per-directory Git attributes,
   retaining public empty directories and disabling automatic byte rewriting.
6. Freeze a portable inventory, compose/sign the manifest, then independently
   verify the signature, inventory and capsule digests.
7. Require a fresh Git namespace, stage exact hash-object blobs without filters,
   set declared executable modes, make a local commit, and audit committed bytes
   and all reachable blob history through BF privacy predicates.
8. Perform a real local Git clone with no shared object storage; audit it again.
9. Execute the independently pinned clean recovery policy. The BF recovery plan
   verifies signer/inventory, authenticates/decrypts, restores, and packs an exact
   result archive. It has no original/reference mount. Validate the returned
   receipt's bindings, safely extract the result outside the container, and compare
   the captured scope. Run development checks separately with no key mount.
10. Supply sixteen observed receipts to the BF evidence predicate. Any service
    failure stops the plan. Only acceptance permits local atomic finalization.

A service receipt proves its operation completed, not general semantic/security
truth. Review and pin actual independent checkers, retain their reports, and never
substitute an arbitrary successful executable for a required gate.

For whole-line annotated BF, explicitly bind the nested annotation flow described
in [ANNOTATED_BF.md](ANNOTATED_BF.md). Its input projection comes from the immutable
capture. The BF filter rewrites only that candidate, then layout reads the filtered
candidate through its `input_root`. Preserve the untouched annotated capture for
exact recovery. Directly running the nested flow does not execute prepare or grant
release acceptance. Ordinary BF filtering is not an interchangeable preprocessing
step, and the host never detects the dialect from extensions.

Prepare now invokes independent review operand 73 after measured checks and before
authenticating the final review. Operand 74 provisions the recovery policy after
the signed clone has been audited. Both are pinned external review operations;
they cannot grant approval merely by returning zero. Final review signatures,
scope/mapping bindings and exact recovery capabilities are independently checked.
Script-based tools must pin their input scripts and configuration with
`inputs_sha256`. Existing private bindings missing these operands fail closed.
Synthetic reviewers explicitly identify their fixture subject and set
`production_approval` to false; they are not production owner approval.

## Portable inventory, trust and recovery modes

Public inventory format is `BYTE-TREE-PUBLIC-GIT`: canonical NFC relative paths,
UTF-8-byte ordering, entry type, byte count/SHA-256 and explicit Git executable
policy. Private recovery inventories retain supported POSIX mode bits separately.
Git internals are nonrelease metadata. The public inventory excludes exactly itself,
release manifest/signature and the public capsule when applicable. Inventory and
capsule have separate digests in the signed manifest; no circular self-digests or
public readiness marker is used. Unexpected extra release files reject.

The capsule is OpenSSL CMS authEnvelopedData/AES-256-GCM. The manifest is signed
with Ed25519 and checked against an independently retained signer SPKI fingerprint.
A repository-supplied public key is not its own trust anchor. Public ciphertext
can be retained indefinitely, including after a later key compromise.

Public mode uses `clean-recovery.example.json` and `recovery-policy.example.json`.
Private vault mode uses `clean-recovery-vault.example.json` and a separately pinned
vault policy containing the explicit readonly `/vault/capsule.cms` mount. A Git
clone alone cannot recover a vault-only archive. Retain that archive independently.

Trusted policies pin the exact mount set, host source paths, readonly flags,
readonly file hashes/directory inventories, image, arguments, workdir and environment.
Docker policies must also pin the exact `engine` executable/hash record. Existing
Docker policies without that independent pin reject and require a reviewed,
reauthenticated policy. QEMU retains its complete `vm` identity check.
Fill directory inventory placeholders with independently reviewed expected records;
do not derive trust automatically from the untrusted clone. Keep the policy outside
all mounts. For each new release its expected clone inventory must be reviewed.

A policy can be authenticated by its independently retained SHA-256 or by a
detached signature checked against an independent signer SPKI pin. Specify exactly
one method. Signed policies allow a reviewed policy to be issued for the actual
new clone without predicting future artifact hashes. The policy itself cannot
supply its trust anchor or change the prebound execution capabilities.

Standalone `recover` authenticates provenance, decrypts and safely restores to a
new destination without original files or a compiler. Bind it to downloaded release
files and independently retained tools/identity/trust. `test-recovery` additionally
requires the independent isolated drill plus a retained reference scope and a
restored-development check. These are distinct from the internal encryption test.

## Retained runtime and explicit publication

`maintenance.bf` command 1 selects encrypted backup and the offline runtime bundle.
The bundle copies all declared host modules, BF recovery executables and complete
independently inventoried Python/OpenSSL/Wine distributions, including libraries.
No installed private CUM module fallback is permitted. Review `runtime-check` and
`runtime-policy` operands and provision empty result storage. The cold check runs
before signing the backup. Windows BF binaries use the explicitly pinned Wine
launcher inside Linux recovery images; that is not native Windows evidence.
Images, distributions and all required offline dependencies must also be backed up.
The retained runtime has now passed same-host relocation drills, including a real
project's declared source scope. See `PRODUCTION_READINESS.md` for the independently
pinned Windows bootstrap, explicit `-I -B` invocation, failed attempts and limits.
A different physical host and independent backup medium remain unverified. The
owner deferred the different-host drill. The 91-file source snapshot predates
later annotation-readiness and license additions; those files are outside that
older recovered scope. A restored APK build and full external-input closure have
not been established.

Maintenance commands 2 and 3 cover approved project-recipient distribution and
signer replacement records. They never give a collaborator the universal owner
identity. Key compromise/rotation cannot erase ciphertext already distributed.

Maintenance command 4 authenticates explicit publication approval bound to the
accepted manifest and target remote, re-verifies the release, then audits its
existing commit/history before pushing `HEAD:refs/heads/main`. It does not add or
commit new bytes after acceptance. Bind private-vault publication operands without
a public capsule sidecar. No force push or automatic upload is performed by prepare.
Source publication of this CUM draft is separately owner-authorized; this does not
accept or publish any protected application release.

Legal classification, preferred-source obligations, attributions, dependency and
reflection/ABI constraints need actual project review. The host authenticates that
review; it does not invent legal conclusions. Missing or incompatible obligations
prevent acceptance. No advanced resistance or zero-overhead claim is established.

Generic trusted-tool wrappers own a process tree for each invocation. Windows
children start suspended, enter a kill-on-close Job Object, then resume; POSIX
children start in a new session/process group. Timeout, output rejection and
normal parent completion stop the owned descendants before returning. These
wrappers are not a sandbox for hostile tools; project code still belongs in the
separate isolation service. The Windows mechanism uses
[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
Existing retained bundles must be rebuilt and independently re-pinned to deploy
host fixes; their frozen inventories are not upgraded automatically. See
[the audit checkpoint](AUDIT_FIXES.md).

The real-project follow-up recorded existing-JNI and standalone ARM64 checks, but
the shared adapter rejected the tested bind record. Isolated unsigned baseline
lowering exceeded controlled 900/600-second budgets and produced no APK. The
source-only BF candidate must not replace shipped JNI libraries. Preferred-source
delivery, transitive notices and next-APK packaging remain open; see
[Android readiness](ANDROID_READINESS.md). A neutral README changes none of these
requirements.
