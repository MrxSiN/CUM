# Current validation status

**PARTIAL — the project has a whole-workflow source draft, but it is not complete
or accepted for production.** Native tests now establish several restricted paths;
they also expose a rejected XAX transformation and a missing native command parser.

| Evidence | Observed result |
|---|---|
| Source coverage | PARTIAL — restricted BF/XAX/JVM adapters and full workflow drafted |
| Full discovered suite | PASS — 52 tests, zero failures/errors/skips; crypto and native recovery opt-ins enabled |
| Windows BF compilation | PARTIAL — O0: 17/40; O1: 39/40; counts include two test workers |
| Native host boundary/continuation | PASS — 11 exchange cases and fixed/real 17-event machines |
| BF fixture build/behavior | PASS — seven fixtures, 28 O0/O1 builds and 112 native runs checked against the independent interpreter |
| BF normalization fixture audit | PASS — seven cases retain executable differences under the tested simplifiers/BBC O1 |
| Restricted Java/Kotlin fixtures | PASS — native BF emission, public compiler builds, 21 input pairs per language and bytecode differences |
| Synthetic internal + signed clone recovery | PASS — exact captured bytes/metadata restored after fixture originals were removed; wrong signature/capsule and extra files rejected |
| Native XAX transformation | FAIL — native edit rejects duplicate mutations on one node |
| Full isolated release/recovery | BLOCKED — no available container engine/reviewed image; WSL reports not installed |
| Scalability/performance budgets | NOT STARTED |
| Android/device execution | NOT STARTED |
| Production release acceptance | NOT STARTED |

See [validation detail](VERIFICATION.md) and the immutable
[results record](../evidence/validation-results-2026-10-30.json). Earlier dated
inspection/unit records describe their original checkpoints and remain unchanged.

## Concrete blockers

- `src/command.bf` passes BBC source checking and emits BFX, but both native build
  levels are declined with exit 5. O1 builds the remaining 39 components, including
  the numeric workflow planner. The human command surface is not operational with
  the selected compiler. Neither BBC nor XAX was edited to hide this dependency.
- The BF XAX recipe produces a native `XAX.WORKSPACE.DUPLICATE_MUTATION` rejection
  (`WORKSPACE-MUTATION-TARGET-UNIQUE`). Its framing unit test is not evidence of an
  accepted graph. No candidate graph/build/workspace recovery is accepted.
- The signed recovery integration is a synthetic Windows process test. It copies
  host modules and the native recovery planner and removes original fixture trees,
  but uses system Python/OpenSSL without sandboxing. It does not satisfy the final
  isolated protected-release or complete offline-runtime backup requirements.

BBC checkout: `53783953fd87cbc9308b108d187b7f3fcfedc06d`.
XAX checkout: `f5d07d77614a9ffec17b2271a25447757cbcfd55`.
Installed BBC and the historical Windows XAX seed were pinned and actually used;
they were not rebuilt from the updated XAX source. Exact file identities and
commands are recorded. Current compiler capacities remain dependency observations,
not permanent CUM limits or proof of dynamic scalability.

General Java/Kotlin, arbitrary BF pointer/loop behavior, universal XAX workspaces,
COCK and advanced analysis resistance remain unsupported. Real project licensing,
owner identities, release approval and public publication were not exercised.
