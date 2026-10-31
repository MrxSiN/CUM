# Protected project presentation

`presentation.bf` supplies two narrowly defined byte-worker operations. The
application implementation remains genuine eight-command BF. Comments in a
delivered BF file are emitted data; punctuation in a comment is not allowed to
introduce an accidental BF instruction.

Mode 1 emits the command-free annotations `Stream input staging`, `Accumulator
transition` and `Result staging`, once per file, then copies the already protected
instruction stream. The opaque continuation byte records whether the header was
emitted. Each line now starts with `# ` so it is also a whole-line comment in the
explicit annotated dialect. This operation does not count as executable
camouflage: independent normalization must still distinguish the underlying BF
instructions.

Mode 2 encodes ASCII text outside angle-delimited markup with hexadecimal HTML
numeric references. Markup and whitespace remain intact. The fixture domain is
static, simple HTML with no scripts, existing text entities or non-ASCII input.
Existing ampersand entities and non-ASCII bytes are refused. This is reversible
presentation encoding, not a secrecy or advanced resistance mechanism. The
independent checker compares parsed tags, attributes and rendered text; Chrome
screenshots establish the visible result for the synthetic fixture. Unsupported
document behavior must not be inferred from that fixture.

`presentation_flow.bf` selects a native BF layout transform, comment annotation,
explicit document mapping and a content-bound mapping report. Its route request
is `(0, 2)`; its nested flow request is `(1, 2)`. It is a restricted BF-project
presentation flow, not a filename-based host dispatcher. Paths and tool identities
are explicit operands. The generic host never authors the replacement text.

Delivered fixture guides describe the real program's behavior and build dependencies.
Annotated source must first use the [annotation-aware flow](ANNOTATED_BF.md);
ordinary ignored-byte filtering does not implement whole-line comment precedence.
License terms remain intact. The immutable capture retains the original source,
comments, documentation and recovery-only notes, independently of the public
presentation. Exact recovery restores those captured bytes rather than attempting
to reverse the presentation encoding.

The CUM repository's root README uses neutral wording. The engineering documents
remain readable and explicit through [the index](INDEX.md). This editorial choice
does not run the HTML byte-worker pass, change executable behavior, conceal Git
history or remove license/source-delivery requirements.

Input contracts distinguish the octets used by the algorithm from compiler-runtime
read-ahead. The native check records the final cursor position of the supplied
stdin file for original and protected binaries and rejects a mismatch. This is an
observed physical file offset, not a general measure of logical input consumption
for arbitrary programs. Documentation must not promise that trailing stream data
remains available when the tested runtime buffers it.
