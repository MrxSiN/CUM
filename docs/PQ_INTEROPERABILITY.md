# Independent PQ CMS interoperability increment

PARTIAL — independent full CMS exchange and the explicit project-scoped PQ
foundation passed their scoped checks. Production release acceptance remains
false. The source, bindings, tests and contract were drafted before execution.

The next unmet recovery gate is a bidirectional full CMS exchange between
Bouncy Castle Java and independently implemented OpenSSL CMS, using
ML-KEM-1024 / HKDF-SHA256 / AES-256-Wrap / AES-256-GCM. OpenSSL 3.6 documents
the KEM recipient options unavailable in the previously tested 3.5.9 tools.
See [OpenSSL CMS](https://docs.openssl.org/3.6/man1/openssl-cms/) and
[MSYS2 package provenance](https://packages.msys2.org/packages/mingw-w64-ucrt-x86_64-openssl).

The draft adds no production encryption route or CUM policy to the host.
`tests/test_pq_interop.py` invokes standard libraries against disposable synthetic
inputs. It covers both directions, empty/binary/1 MiB data, fresh ciphertext,
wrong identities, corrupt/truncated capsules, existing-output preservation,
multiple recipients and rejection of weaker suites. OpenSSL output uses the
existing temporary-output publication guard; failed authentication cannot
publish a plaintext destination. Java CMS invocation is shared with its existing
test without changing that test's cryptographic operations.

Use a separately downloaded, authenticated tool bundle in ignored private
storage. Verify its package SHA-256 from the official package page and detached
signature against the preinstalled MSYS2 public keyring before extraction or
execution. Pin its executable and DLLs and clear provider/config injection
variables, as in `config/pq-interop.example.json`. No global install, user keyring
change or replacement of existing tools is needed. The dependency license and
notices remain with the retained package.

After completing the draft, bind the independent tool and run with
`BYTEHOST_CRYPTO_TESTS=1`, `CUM_PQ_JAVA`, `CUM_PQ_CLASSPATH` and
`CUM_PQ_INTEROP_BINDING` set explicitly:

```powershell
python -m unittest tests.test_pq_cms tests.test_pq_interop -v
```

Record failed attempts separately. A successful synthetic exchange will establish
interoperability for the tested suite and identities only. Operational project
identity generation, signed context/prepare adoption, independent offline backup,
full release recovery, size/performance budgets, AI resistance and protected APK
acceptance remain separate gates. Ed25519 provenance remains classical.

## Project-scoped PQ foundation

`src/pq_identity_flow.bf` is a separate genuine BF planner. It verifies signed
interoperability evidence and binds it to the selected executable/DLL identities
before creating the owner/System-only pending vault. It requests standard
ML-KEM-1024 key generation, public-key extraction and certificate issuance using
the existing independently trusted Ed25519 signer, then signs the strict public
identity record and atomically publishes the new vault. It never replaces an
existing classical identity or shares a universal decryption key.

`config/pq-identity-flow.example.json` and
`config/pq-project-recovery.example.json` keep this explicit foundation separate
from ordinary prepare. The existing project-recovery BF planner supplies capture,
authenticated seal/internal restore, signed context checks and exact recovery.
The generic CMS transport now forwards optional standard KDF/wrap operands and
the existing trusted-tool runtime pins/environment controls; it makes no project
or transformation decision. Existing classical operands remain valid.

The certificate is a pinned recipient public-key container, not a trusted-CA
chain claim. Identity metadata has the same strict public schema as the classical
identity. Its `post_quantum` value describes recipient encryption only; the
manifest explicitly retains `ED25519-RAW` provenance. Neither the certificate nor
the release signature becomes quantum-safe.

Executed checks cover pure BF plans/rejections, compatibility mismatch rejection
before private storage/key creation, runtime-DLL pin rejection before execution,
native project initialization/seal/recovery, independent BC archive decryption,
local ciphertext-clone restore after plaintext removal, and wrong-project/security
scope rejection before decryption. The identity/recovery planners compiled at
O0 and O1; 80 native plan/rejection vectors passed. Fifteen foundation/classical
crypto/trusted-input methods passed, four of them also passed with the O0 builds,
and sixteen affected prepare/recovery/isolation/runtime methods passed. Along
with the four interoperability methods, that is 35 distinct methods with no
unittest skips. No new guest VM execution is included in those method counts.

The new project identity then sealed the retained immutable 97-file, 125-entry
project snapshot (2,682,880 archive bytes). Its internal recovery, independent
Bouncy Castle decryption and native recovery from a ciphertext-only local Git
clone matched exactly. This was not a fresh live-source capture: it used the
preserved 2026-10-31 snapshot. The new vault is separate from the classical vault.
Neither the working target nor Original was written. Original plaintext still
existed elsewhere on the trusted host; this was not an isolated or different-host
recovery drill. No capsule was published or production release signed.

Initial project runs rejected unresolved DLL-path keys in a test binder and a
wrong retained native-fixture path. The generic CMS refactor also passed the
executable twice into the trusted-tool API, which the regression caught before
successful encryption. The redundant executable was removed, the original
classical recipient argument form retained, and the fixture binding corrected.
The two failing 15-method runs remain private; the final 15-method rerun passed.

This explicit foundation does not enable PQ in ordinary full prepare/release.
An authenticated compatible backend and new signed bindings must be retained in
a rebuilt, independently pinned offline kit. The old OpenSSL 3.0 recovery guest
is not a PQ backend. Independent key backup is NOT STARTED, and different-host
recovery is owner-deferred. No fallback to a classical recipient occurs. The
new identity and capsule are not a production-approved replacement for the
existing verified recovery route. AI/APK, preferred-source licensing and real
application performance gates remain unaccepted.

See [interoperability evidence](../evidence/pq-interoperability-2026-11-01.json),
[foundation evidence](../evidence/pq-project-foundation-2026-11-01.json),
[project regression](../evidence/pq-project-tests-2026-11-01.txt) and
[affected regression](../evidence/pq-affected-tests-2026-11-01.txt).
