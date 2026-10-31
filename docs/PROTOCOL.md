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

The `transform.bf` pass is byte-local and preserves loop punctuation. It needs
no open-bracket parse stack across records: BBC validates the final concatenated
source. A loop may span any record boundary. This property must not be assumed
for other passes. Any continuation facts must fit their declared state format;
otherwise a separately specified format is required.

`annotated_filter.bf` uses state A = 1 and state B = 0/1/2 for leading whitespace,
code or whole-line comment. Line state crosses records, including CR/LF boundaries;
arbitrary bytes, including zero, are accepted inside comments. Unsupported code
or mode/state rejects. `presentation.bf` instead uses state A as mode and state B
to retain header/markup context. These workers share framing, not state meanings.
See [annotated BF](ANNOTATED_BF.md) and [presentation](PRESENTATION.md).

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

Per-process capacities must come from verified selected-tool observations, not a
historic BBC constant. Example record payload 512 is an owner-editable transport
budget, not a file-size maximum. Two input bytes per payload byte, two state bytes
and one marker must fit the selected process input budget. Expanded output and
trailer must fit its output budget. Fresh processes per record do not bypass a
per-process restriction. Chunking cannot make an unsupported final build valid.

## Event-machine worker ABI

The multi-cell/JVM kernels use a distinct record:
`177 | event | byte | profile | selector | five facts | sixteen opaque bytes`.
Events are start, data and end. The host reads actual file bytes before choosing
data versus physical end. Zero data is still a data event. Facts report integer
zero/negative, equality to stack-top, stack-empty and explicit integer-budget
exhaustion. Null integer budget reports no integer ceiling. BF assigns every
fact's application meaning and chooses all effects.

Response is `178 | effects | sixteen new opaque bytes | status`. Effects provide
literal output, opaque buffer/stack operations, integer operations or a pinned
kernel handoff. Unknown/truncated effects, rejected status, missing kernels and
explicit storage/time/output budgets abort. This is a generic machine, not a
host parser or camouflage service.

Each physical event may use a fresh native process. Authenticated checkpoints bind
source/config identities, opaque state, dynamically stored integers/stacks/buffers,
input/output positions and output digest. BF end-event checks reject unfinished
parses. Prefix output is not an accepted final file. Restart retains the local
rollback limitation above. Fixed protocol registers/state bytes identify the
machine ABI; they do not bound source length, project size or bracket depth.
# Amended policy record

`resistance_policy.bf` consumes exactly twelve numeric bytes selected from
authenticated records. Its profile, claim, evidence-state and output codes are
defined in [RESISTANCE.md](RESISTANCE.md). Generic opcode 24 accepts either the
existing literal `input_hex` or explicit JSON `input_fields` observations,
rejecting ambiguous sources, non-integer/non-byte values and physical length
mismatch before launching BF. Opcode 19 also supports typed `equal_fields`
comparisons between records. These operations contain no profile policy.
