# Project-scoped recovery increment

The later [PQ interoperability/project foundation](PQ_INTEROPERABILITY.md) adds
a separate ML-KEM identity and executed same-host recovery. It supersedes the
earlier installed-tool PQ blocker below for the tested suite. This page retains
the classical checkpoint; its passing identity and recovery route are preserved.

PARTIAL — the whole increment was drafted before tests; the scoped classical
identity, native workflow and real-project signed recovery checks now pass.
This increment follows the updated master and handoff's earliest missing Stage 1
gate. It is a recovery foundation, not a protected release or an AI-resistance
claim. Earlier shared-state reconstruction failures and release blocks remain.

## Ownership and operation

`src/identity_flow.bf` accepts command 1, mode 1. The BF planner requires disjoint
storage, creates an owner/System-only pending vault, invokes pinned OpenSSL to
generate a project RSA-3072 recovery key/certificate, exports its public SPKI,
binds those public identities to an opaque project ID, signs and verifies that
record with an independently supplied Ed25519 signer, checks its bindings and
atomically publishes the private vault. Other commands/modes reject, including
the unavailable PQ mode. Partial initialization stays private and unaccepted;
existing destinations and operation journals are never overwritten or resumed
implicitly. Use a fresh reviewed operation after an interruption.

`src/project_recovery.bf` accepts command 1 to seal and internally verify an
immutable archive; command 2 verifies and restores the signed recovery package.
Mode 1 is the explicit classical CMS baseline. Independent signer trust, expected
project/release IDs, exact recipient certificate and signed identity record are
checked before decrypting. Recovery validates the archive's encrypted scope
manifest and safely restores into a new directory. The older clean-recovery
planner/format remains unchanged; no historical capsule is silently migrated.

The generic host gains only a disjoint-tree assertion. Existing services supply
ACLs, external key generation, storage, CMS, signing and archive verification.
It neither chooses a protection pass nor parses or transforms project source.
Bindings are explicit reviewed operands, not a second decision program. Example
limits are operation budgets, not compiler/application capacity claims.

Use the existing host command surface with concrete, pinned private jobs:

```text
python -m host.bytehost flow PRIVATE/identity.json --command 1 --mode 1
python -m host.bytehost flow PRIVATE/recovery.json --command 1 --mode 1
python -m host.bytehost flow PRIVATE/clean-recovery.json --command 2 --mode 1
```

The examples deliberately contain unresolved paths, signer pins and owner SIDs.
They are not runnable defaults. No proposed `cum identity init` stub is added.

## Cryptographic contract

The ciphertext is the existing CMS authEnvelopedData/AES-256-GCM BYTE-TAR format.
OpenSSL generates the CEK and IV on each encryption call; the host supplies no
key or nonce override. A test-only decoder inspects disposable RSA envelopes and
unwraps their CEKs with OpenSSL solely to confirm 32-byte distinct sample keys
and distinct 12-byte sample nonces. It is never used on real project identities,
never implements a cipher and never records CEK values or their digests.
Finite samples alone do not prove universal nonce uniqueness or RNG security.

The canonical `SIGNED-PROJECT-CMS-RECOVERY` manifest binds the opaque project ID,
release ID, capsule ciphertext digest, recipient-certificate digest, signed
project-identity digest, format and classical-security scope. It contains no
plaintext source names, hashes or mapping. Its detached Ed25519 signature and
independently retained expectations provide context authentication before
decryption. These are signed-context bindings, not new GCM AAD attributes or a
novel encryption construction. All recovery entry goes through the BF workflow;
calling raw generic decryption alone does not enforce this application contract.

Multiple recipient certificates use OpenSSL's existing CMS recipient mechanism.
A collaborator has an independent key, not the owner's key. Add/remove recipients
only in a newly reviewed release binding and sign its declared certificate set.
Removal cannot revoke already accessible capsules or plaintext. A stolen project
identity exposes every retained capsule addressed to it; backup/rotation and
historical exposure review remain operational requirements. The current private
key file is protected by OS ACLs, not a passphrase or offline-media encryption.
Signing and recovery keys are distinct, separately supplied capabilities.

The independent `tests/tools/crypto_probe.py` tests ML-KEM-1024 key generation,
certificate construction and actual CMS encrypt/decrypt. Primitive support alone
does not admit PQ mode. A same-backend roundtrip remains PARTIAL until algorithms,
RFC 9629/9936 and independent interoperability are verified. Unsupported CMS
recipients are BLOCKED. No custom KEM, hybrid combiner or PQ-signature claim is
introduced, and the working classical decoder remains available.

Standards and backend references: [NIST FIPS 203](https://csrc.nist.gov/pubs/fips/203/final),
[RFC 9629](https://www.rfc-editor.org/rfc/rfc9629.html),
[RFC 9936](https://www.rfc-editor.org/rfc/rfc9936.html),
[OpenSSL CMS](https://docs.openssl.org/3.5/man1/openssl-cms/) and
[OpenSSL CMS key/IV generation](https://github.com/openssl/openssl/blob/openssl-3.5.4/crypto/cms/cms_enc.c).
The installed binary version/pin must be observed independently; a source tag
is not proof of how a particular installed executable was built.

## Experiment workspace

The owner moved the working target to
`D:/Android/AndroidStudioProjects/Experiment/Encrypted` and designated
`D:/Android/AndroidStudioProjects/Experiment/Original` as the read-only reference.
Current private bindings must use those roots; historical Dummy evidence stays
unchanged. Capture the reviewed source/development scope from Encrypted, compare
its source/development inputs to Original, and use only the immutable capture
for archive creation. Record existing documentation/license differences separately
and preserve them; source equality does not certify a licensing decision. Exclude
Git, caches, build outputs, generated binaries and credentials explicitly.

Private jobs, original inventories/archives, restored checks, signing credentials
and the project identity stay outside both roots. Only the signed encrypted
recovery-check package may be copied under Encrypted's build area. Its manifest
explicitly says `protected_release_accepted: false`. No original source edits,
APK replacement, publication or repository visibility change is performed by
this increment.

## Drafted verification and remaining gates

Drafted checks cover BF plan bytes/rejections, disjoint storage, scoped identity
creation/replay, fresh sample CEKs/nonces, multiple independent recipients, exact
restoration after removing captured originals, wrong project/release/recipient,
wrong keys, corruption and truncation. Existing legacy crypto/signed recovery
checks must still pass. The real-project run must compare aggregate inventory
identities without publishing original paths/digests or credentials.

## Executed checkpoint — 2026-10-31

PASS within scope: both BF planners compiled at O0 and O1; all 80 native
plan/rejection vectors passed. Four new test methods and 19 affected legacy
methods passed, including the previous signed clone recovery path. Disposable
envelope inspection confirmed two distinct 256-bit CEKs and two distinct
96-bit nonces; both authorized independent recipients recovered the same archive.
Wrong keys, changed project/release/recipient expectations, corruption and
truncation rejected without accepted plaintext output.

The working Experiment source matched Original. Seven existing documentation/
license differences were preserved; whole-tree equality is PARTIAL, not a source
or licensing approval. The exact captured working scope is 125 entries, including
97 files and 2,572,619 file bytes. A real local Git clone contained only ciphertext,
the signed context manifest and detached signature. The trusted pinned VM restored
that scope exactly with UID 1000, loopback only, no Git metadata, no original or
reference mounts and no signing private key. Three context substitutions rejected
before decryption. The recovered canonical XAX store passed native verification.
Both declared live source scopes remained unchanged afterward. The only new
working-target output is `build/cum/project-recovery-2026-10-31/`, containing the
three-file signed encrypted foundation package, never a production-ready APK.

Both installed OpenSSL 3.5.9 builds passed ML-KEM-1024 key generation and recipient
certificate construction, but CMS AES-256-GCM encryption rejected with exit 3,
`03000096 evp_pkey_asym_cipher_init: operation not supported for this keytype`.
Their shared backend family is not independent implementation interoperability.
PQ mode remains BLOCKED; the installed classical path interoperated with OpenSSL
3.0.13 inside the pinned guest. That classical same-family cross-version check
is not PQ interoperability or quantum-resistant authenticity.

The initial full-tree equality guard stopped safely before identity creation.
After classifying and preserving the seven non-code differences, the first VM
attempt failed with PROCESS_EXIT; its configuration mapped the signer's public
key to the results directory. Detailed first-attempt guest stderr was not retained.
The corrected trust mapping, fresh ciphertext-only clone and repinned capability
policy passed. Original jobs and failure records remain private; they are not
silently counted as successful attempts.

See [sanitized evidence](../evidence/project-recovery-2026-10-31.json),
[new checks](../evidence/project-recovery-native-2026-10-31.txt) and
[legacy regression](../evidence/project-recovery-regression-2026-10-31.txt).

Remaining: independent/offline key backup and different-host recovery (owner
deferred), a positively admitted resistance candidate, full native graph/ABI/
Android protected integration, licensing/preferred-source approval and measured
production budgets. Nothing in this recovery increment removes those gates.
The [next integration increment](PREPARE_INTEGRATION.md) now wires the contract
into ordinary prepare jobs and scoped recovery. Its scoped tests pass, while
a complete accepted prepare transaction and protection acceptance remain blocked. Private-key and trust-anchor backup
on independent media is NOT STARTED; the private vault alone is not that backup.
