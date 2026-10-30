# CUM — Certified Useless Module

Brainfuck-authored source transformation and exact-recovery system under development.

**Status: PARTIAL — unbuilt, untested draft checkpoint.** The whole-project drafting
session was interrupted before final integration and documentation were finished.
This repository is not a production release or evidence that protection, recovery,
signatures or performance gates have passed.

## Draft contents

- Genuine Brainfuck workflow, command, policy and adapter sources in `src/`.
- Multi-cell BF layout transformations for statically bounded, balanced loops.
- Linear BF virtualization and narrow Java/Kotlin integer-module transformations.
- A guarded XAX wrapping-add transaction recipe using the actual `XAXEDIT1` format.
- Separately identified generic host services for binary transport, opaque state,
  snapshots, archives, cryptographic tools, isolation, metadata and Git operations.
- Configuration templates, independent check sources and synthetic fixtures.

All CUM transformation and application decisions belong in Brainfuck. Python host
code supplies generic services; Java/Kotlin files under `tests/projects/` are test
subjects, not CUM implementations. XAX remains a canonical semantic-graph system.

## Current limitations

Adapters have explicit, restricted domains. General Java/Kotlin parsing, arbitrary
BF pointer behavior and universal XAX project support are not established.
The newest Git transport, portable public-inventory, trusted-recovery and runtime
packaging components still need their final integration. Some older documents and
example bindings describe earlier draft interfaces.

No native build, unit suite, integration suite, recovery drill, signature check,
benchmark or release acceptance test has run. Testing, fixes based on test results
and optimization remain deferred under the owner's drafting-first workflow.
See [the current checkpoint status](docs/STATUS.md).

## Layout

| Directory | Purpose |
|---|---|
| `src/` | Authoritative BF application sources |
| `host/` | Generic host and external-tool providers |
| `tests/` | Independent verification sources and fixtures |
| `config/` | Placeholder operand templates, not real credentials |
| `docs/` | Draft contracts and operating notes |
| `evidence/` | Historical source inspection and inventory records |

The native build driver is `python -m host.bytehost.build <binding.json>`.
It invokes an explicitly pinned BBC executable; no production interpreter fallback
is supplied. Provisioning a working compiler, reviewed isolation images, identities
and independently trusted configuration remains necessary before validation.

The owner explicitly authorized this source push to GitHub. That authorization
does not include publishing keys, real private job data, recovery capsules or
captured original projects. Those paths and file types remain ignored.
