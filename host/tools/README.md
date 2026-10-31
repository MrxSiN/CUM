# Generic CMS library adapter

`StandardCms.java` invokes Bouncy Castle's standard CMS/KEM/GCM APIs. It knows
nothing about projects, source languages, protection profiles, recovery maps or
release acceptance. CUM application decisions remain in BF. This optional tool
is not part of BBC/XAX and introduces no code into those repositories.

The candidate uses Bouncy Castle Java 1.86 (`bcprov-jdk18on`, `bcpkix-jdk18on`,
`bcutil-jdk18on`) and a separately pinned JVM. The owner-side candidate dependency
manifest records Maven Central URLs, SHA-256 identities and checked published
SHA-512 sidecars. Publisher signatures have passed against the official-site key. Independent full
CMS interoperability subsequently passed with authenticated OpenSSL 3.6.5 in
both directions for the tested suite; see
[executed scope](../../docs/PQ_INTEROPERABILITY.md). This is not full prepare or
production PQ admission. Retain the libraries' supplied licenses/notices.

Operations are `encrypt RECIPIENT_CERT INPUT OUTPUT` and
`decrypt PRIVATE_PKCS8_PEM INPUT OUTPUT`. All arguments are paths, never keys or
passphrases. The caller must provision private, disjoint output storage and pin
the JVM, class and every dependency before using the generic trusted-tool service.
The adapter accepts ML-KEM-1024, HKDF-SHA256, AES-256-Wrap and AES-256-GCM. It
publishes a new output only after library authentication succeeds and refuses
replacement. Its library buffering requires explicit memory/size budgets.

This is an experimental external cryptographic capability. The ordinary prepare
examples continue to admit only the verified classical project identity; they
must not be relabeled PQ merely because this tool compiles or self-interoperates.
Ed25519 provenance also remains classical. No automatic fallback is implemented.

Use a pinned helper JAR, not an open classes directory. Clear JVM-injection
environment variables as in config/pq-cms-tool.example.json. Suite and GCM
nonce/tag parameters are checked before authenticated plaintext publication.
