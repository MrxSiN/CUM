# Whole-line annotated BF

`annotated_filter.bf` is a genuine BF byte worker. Mode 1 uses a second opaque
state byte: 0 for a line with only leading spaces/tabs, 1 for code, and 2 for a
whole-line comment. A `#` in state 0 discards the rest of that line, including BF
punctuation and arbitrary comment bytes. CR or LF starts a new line. Code emits
only the eight BF commands; spaces/tabs are ignored. Inline `#`, other code
characters, BOMs and unknown mode/state values reject. Other control whitespace
is outside this restricted dialect. Bracket and layout eligibility checks remain
the responsibility of the following BF pass and compiler.

The filter preserves line state across records and independent native processes.
The generic host supplies complete pair-framed records and authenticates opaque
continuation state. A legitimate zero byte inside a comment is not physical EOF.
Comment bytes are opaque; this pass does not certify UTF-8 encoding.

`annotated_flow.bf` routes `(0,2)` to nested operand 47. The nested request `(1,2)`
chooses, in order, annotation filtering (operand 5), layout transformation (1),
command-free `#` annotations (2), and a content-bound mapping report (4).
`config/annotated-flow.example.json` supplies deliberately invalid operands for
that sequence. The layout reads the filtered candidate, not the captured annotated
original. Standard-BF routes remain separate and do not guess a dialect from text
or a filename. A release job must explicitly bind the annotated route and retain
the exact original in its authenticated snapshot.

New header lines begin with `# `, contain no BF commands and work under both this
dialect and ordinary eight-command filtering. Header comments do not substitute
for executable structural change. Original comments and documentation remain in
the encrypted capture; filtering does not change the authoritative recovery scope.

The current layout contract still requires nonnegative pointers and every loop
to return to its entry cell. Native compiler declines, incompatible Android ABIs,
missing licensing approval and failed checks stop acceptance. Passing this filter
does not admit arbitrary BF programs, general Android applications or a protected
shared-library release. See the dated Android readiness record for actual builds,
device cases, declined configurations and the selected profile of each probe.
