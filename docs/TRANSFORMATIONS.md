# Executable BF transformation draft

## Accepted semantic domain

Source consists of arithmetic, I/O and loops at logical cell zero, with any
ignored non-command bytes. Any `>` or `<` is rejected, including inside a loop
that might be skipped. Matched brackets are validated independently by BBC.
Cells must be zero-initialized wrapping unsigned bytes, EOF must read zero, and
the installed runtime must provide at least three safe physical cells.

This excludes ordinary multi-cell BF applications. No claim of general Brainfuck
protection is made. The restricted domain avoids silently changing tape-boundary
failures by doubling strides or stealing live neighboring cells.

## Pass contracts

All scratch cells begin and end each replacement at zero; pointer begins and ends
at data cell zero. I/O and original loop delimiters are copied exactly. Ignored
bytes are removed by BF. Input/output counts and ordering remain unchanged.

| Profile | Increment representative | Required scratch |
|---|---|---|
| FAST | `[->+<]>+[-<+>]<` | cell 1 |
| CAMOUFLAGE, selector zero | `>+<[->+<]>[-<+>]<` | cell 1 |
| CAMOUFLAGE, selector nonzero | `[->-<]>-[-<->]<` | cell 1 |
| MAXIMUM | `>>+<<[->>+<<]>>[-<<+>>]<<` | cell 2 |
| PERFORMANCE | `+` | none |

Decrement uses the opposite one-step adjustment to the scratch representation.
These are separately inspectable arithmetic transfer constructions, not ignored
comments. MAXIMUM denotes a requested profile, not measured superior protection.

For the positive-transfer construction, transferring x to scratch establishes
`data=0, scratch=x`. Adjusting scratch then transferring back yields x±1 modulo
256 with scratch zero. For the negative-transfer construction, scratch becomes
−x, receives the opposite adjustment, and is transferred back subtractively.
For every replacement, transfer loops terminate within the byte domain. Invariant
composition preserves original loop zero tests, termination behavior, data,
pointer and I/O. The scratch/tape precondition is essential.

These arguments are draft semantic reasoning, not executed evidence. Resource
budgets can still reject larger protected output or longer execution. Compilation
failure must abort preparation even if the original compiles.

## Mandatory resistance checks

The independent checker removes ignored characters, then asks the real BBC O1
pipeline for BFX on original and protected source. Identical filtered source or
identical BFX fails the baseline gate. Preserve BFX hashes, compiler identity and
reports. Later audits must add more independent simplifiers and graph inspection.
The current checker is a minimal baseline and does not establish strong practical
analysis resistance. Transfer loops are recognizable and may be reconstructed.

PERFORMANCE is currently identity filtering and deliberately fails meaningful
structural-change acceptance. No profile can bypass normalization, correctness,
licensing, confidentiality, recovery or budget gates.

## Deferred passes

General tape relocation, loop/state restructuring, graph transformations,
virtualization and stronger diversification are NOT STARTED. They need BF-owned
preconditions and state, compiler capability evidence, separate semantic arguments,
native/differential checks and exact recovery before adapter admission changes.
