# Binary records and continuation

## Outer physical record: BFRAME-NUL-01

An exchange accepts exactly one record:

```text
8 bytes magic 42 46 52 41 4d 45 00 01
canonical unsigned base-128 header-byte-length
canonical ASCII JSON header
payload bytes
32-byte SHA-256 of all preceding bytes
physical EOF
```

Header keys are exactly `operation`, `request`, `sequence`, `state` and
`payload_bytes`. The last two integer-valued fields are canonical unsigned decimal
strings; sequence and payload length have no fixed integer-width field.
`state` is the opaque worker state in hex. Unknown keys/formats, noncanonical
lengths, trailing bytes, wrong digests and mismatched expected identity are errors.
Header and payload budgets are explicit per-operation transport policy.

`read_frame` obtains every declared byte and validates the physical end before a
worker starts. An empty stream produces PHYSICAL_EOF. A short header, payload or
checksum produces TRUNCATED. A genuine zero payload byte is normal data.
The checksum detects transport corruption, not malicious provenance; persistent
checkpoints use HMAC and public releases use independent signatures.

## Inner BF worker ABI

```text
Input:  state byte A | state byte B | (01 | data byte)* | 00
Output: emitted payload | new state byte A | new state byte B | status
```

The host constructs the inner stream only after it has physically complete
payload bytes. The marker byte and data byte occupy distinct positions, so any
data byte including zero is representable. BF reads no byte after the terminal
marker. An empty payload still has the two state bytes and one terminal marker.
On a nonzero status the entire response and staged mapped file are unusable.

The output trailer allows BF to discover an ineligible byte late in a record
without buffering the whole record. Prefix output is never accepted as success.
Statuses in the transformation worker are 0 success, 1 unsupported pointer/source
domain, and 2 unknown profile. Native process failures remain separate host errors.

`transform.bf` defines state A as profile 1..4 and state B as diversification
selector. Zero chooses one transfer representation; nonzero chooses the other in
the CAMOUFLAGE profile. State is returned unchanged. There is no claimed PRNG.

The current pass is byte-local and preserves loop punctuation. Therefore it needs
no open-bracket parse stack across records: BBC validates the final concatenated
source. A loop may span any record boundary. This property must not be assumed
for future context-sensitive passes; those require a richer, new worker format.

## Restart checkpoints

`BYTE-MAP-STATE-HMAC-SHA256` stores input/worker/config digests, unbounded decimal
sequence/cursors, committed-output digest, opaque worker state and completion.
HMAC-SHA256 uses a separately retained random key. This is authentication, not
encryption: source-bearing future state must additionally be kept confidential.

Write order is output append → fsync → authenticated checkpoint atomic replace.
On restart, verify bindings/HMAC and the committed prefix, truncate an uncommitted
tail, and continue from the committed input offset. Complete operations reject
replay. Different inputs, workers, profiles, budgets or changed output reject.
This prevents duplicate committed bytes following ordinary interruptions.

Local storage is trusted against rollback of an entire authenticated checkpoint
and its filesystem history. HMAC alone cannot detect wholesale rollback of both
valid state and expected state; a stronger threat model needs an independent
monotonic ledger. No rollback-proof hardware guarantee is claimed.

## Transport versus compiler resources

BBC currently documents 65,536-byte total input/output buffers per native run.
Example record payload 512 is an owner-editable transport budget, not a maximum
file size. Two input bytes per payload byte, two state bytes and one marker must
fit the selected process input capacity. Expanded output plus trailer must fit
its output capacity. The host launches a fresh native process for each record.
It never assumes that many small frames bypass one process's total input bound.

Final protected compilation remains constrained by the actual BBC frontend.
Splitting transformation requests cannot remove that compiler limit.
