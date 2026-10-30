# Current draft checkpoint

The owner requested committing the current work to GitHub after interrupting the
whole-project drafting turn. This checkpoint preserves that work without claiming
that the whole-project draft or its integration is complete.

## Evidence states

| State | Status |
|---|---|
| Implementation source | PARTIAL — substantial draft written |
| Whole-project integration and documentation | PARTIAL — interrupted |
| Native compilation | NOT STARTED |
| Native execution | NOT STARTED |
| Unit tests | NOT STARTED |
| Integration tests | NOT STARTED |
| Exact recovery demonstration | NOT STARTED |
| Trusted signature/provenance verification | NOT STARTED |
| Performance measurements and optimization | NOT STARTED |
| Production release acceptance | NOT STARTED |

Source publication is an explicitly authorized repository action, not a passing
product release gate. No execution or test results are inferred from source files.

## Written source areas

- BF command parsing, routing, workflow plans, scope policies, public projection,
  metadata production, budget decisions and private-digest predicates.
- Multi-cell BF layout processing with balanced-loop/bounds preconditions.
- A linear BF virtualizer and constrained Java/Kotlin integer-module adapters.
- BF-authored guarded XAX transaction assembly plus existing-SDK query integration.
- Generic framed transport, opaque storage, authenticated checkpoints, archives,
  immutable capture, cryptographic-tool invocation and isolated processes.
- Generic public-inventory, Git staging/auditing, private-directory and runtime
  package helpers, together with independent check source and configuration data.

## Remaining work

1. Finish connecting the latest Git transport, portable inventory, trusted clean
   recovery and independent runtime-package components to the BF workflows.
2. Reconcile all bindings and older documentation with the final interfaces.
3. Complete the whole-project source draft before moving to validation.
4. Provision and pin the real BBC compiler, compatible XAX native backend and
   reviewed execution environments; initial inspection found no BBC executable
   or Docker/Podman command in the inspected locations.
5. Build and run the components, execute independent correctness/security/recovery
   checks, then fix demonstrated failures and measure performance.

The Java/Kotlin adapters target the declared `Arithmetic` integer-module grammar.
BF layout processing requires provable static bounds and balanced pointer loops;
virtualization targets linear single-cell programs. XAX structural-edit support
must be demonstrated by the selected native backend. None of these is universal
language support or verified analysis resistance.

Historical inspection/inventory records describe their original authoring point;
they are not a current source manifest or executed acceptance evidence. Older
design notes may lag the latest code and must not override this checkpoint status.
