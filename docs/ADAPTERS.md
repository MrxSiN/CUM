# Adapter source contracts

Adapter acceptance remains PARTIAL. Restricted BF/JVM and four-transaction XAX
fixture paths have native evidence. `adapters.bf` admits IDs 1..5 to drafted routes, not to verified
language support. `routes.bf` chooses the service/operand. The host never chooses
an adapter from a filename. `discovery.bf` classifies paths, while `scope_policy.bf`
requires explicit owner dispositions. Unknown IDs and unsupported syntax reject.

| ID | BF source | Restricted input domain | Structural output |
|---:|---|---|---|
| 1 | `machines/bf_layout.bf` | Nonnegative statically bounded pointer paths; every loop returns to its entry cell | Strided data layout, zero scratch cells, arithmetic transfers |
| 2 | `graphs/add_negate.bf`, `graphs/flow.bf` | Explicitly queried wrapping-add node and supported canonical edit interface | Guarded negate/subtract replacement using real `XAXEDIT1` mutations |
| 3 | `machines/java_int_module.bf`, `java_match_*.bf`, `java_emit.bf` | Declared `Arithmetic.combine(int,int)` module grammar | Wrapping integer carry computation |
| 4 | `machines/kotlin_int_module.bf`, `kotlin_match_*.bf`, `kotlin_emit.bf` | Declared `Arithmetic.combine(Int,Int)` object grammar | Wrapping integer carry computation |
| 5 | `machines/bf_virtualize.bf` | Linear single-cell arithmetic/I/O; no pointer travel or loops | Public BF dispatcher and encoded instruction sequence |

The Java/Kotlin fixtures in `tests/projects/` define the narrow module forms.
Match kernels examine bytes in BF and reject text outside their grammar. This
is not general Java/Kotlin, Android/Xposed, reflection, JNI or resource support.
C/C++/Rust/Python adapters and COCK integration are NOT STARTED. Unsupported
requests must reject rather than count unchanged copied source as protected.

Annotated BF uses the explicit `annotated_flow.bf` entry point before adapter 1's
layout kernel. `annotated_filter.bf` gives whole-line `#` comments precedence over
embedded BF punctuation and rejects unsupported code. It does not expand layout
eligibility or Android shared-library support. See [its contract](ANNOTATED_BF.md).

`transform.bf` remains the separate single-cell arithmetic/I/O/loop worker. It
rejects pointer motion and uses the two-state-byte transport. It is not the
multi-cell route. Its PERFORMANCE profile only filters and cannot satisfy
meaningful structural protection.

Native BF fixture evidence covers seven programs and both public compilation
levels. Java/Kotlin evidence covers the declared Arithmetic fixture, CAMOUFLAGE
native emission, 21 input pairs per language and bytecode differences. These
results do not establish general language support, scalability or release gates.
See `VERIFICATION.md` for exact scope.

## Graph authority

XAX canonical binary graphs remain authoritative. The existing pinned SDK supplies
the explicit node query; its Python inspection/verification dependency is visible
in `host/providers/xax_query.py`. BF emits the transaction recipe. Native XAX
`edit`, `verify`, `resolve` and `build` perform their normal compiler work.

The Windows seed edit writes a candidate, followed by native verification and
expected-source-digest replacement. This is not a general XAX workspace server.
All required graph/workspace/evolution/dependency files must be captured explicitly.
Generic file recovery alone does not prove development-ready workspace recovery.
Backend declines abort; no textual XAX source or SDK build fallback is permitted.

Every pass requires native checks, independent behavior, explicit preconditions,
normalization comparisons, exact recovery and measured budgets. Promotion proceeds
BF first, then XAX, then each additional language. Draft routes do not promote
any milestone.


The earlier duplicate-mutation rejection is retained in historical evidence. The
revised recipe uses four native-verified single-mutation transactions and passes
resolve/build, native-code difference and finite behavior checks on a BBC-authored
wrapping-byte ADD fixture. Stale carrier replay rejects. This establishes that
restricted edit path; other integer types, arbitrary workspaces and development-ready
workspace recovery remain unaccepted. Input must already be an editable build
request. Framing tests alone still cannot establish transaction validity.
