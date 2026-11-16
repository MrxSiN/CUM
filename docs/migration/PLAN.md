# Whole-project draft: BF/XAX-only CUM (2026-11-16)

DRAFT. Nothing in this page is executed evidence. It is the whole-project
migration shape that `AGENTS.md` requires before new tests, fixes or
optimization, written against the owner's revised master prompt
(`CUM_Master_Engineering_Development_Prompt_XAX_Only_Revised.md`, untracked,
owner-supplied).

## Language policy reconciliation

The revised master prompt asks for XAX-only CUM-owned code and says `AGENTS.md`
must be reconciled first. On 2026-11-16 the owner's direct instruction was:
follow `AGENTS.md` strictly, and rewrite the repository's Python in Brainfuck
and XAX only. `AGENTS.md` therefore stays as it is:

- CUM decisions, transformations, policies and pure byte logic: genuine
  eight-command BF, compiled by the pinned BBC.
- Capabilities BF cannot provide (physical EOF, files, processes, handles,
  hashing APIs, timing, ACLs): canonical XAX graphs, compiled by the pinned XAX
  Windows compiler, authored only through official XAX transactions
  (`xaxc edit` batches, or construction records followed by transactions).
- No other language for CUM-owned executable code, tests or scripts.

Where the prompt says "XAX-only", this draft reads "BF for decisions, XAX for
platform services". The prompt's other rules (draft first, no compiler
workarounds, fresh publication approval, evidence states, AI-cost waiver) are
unchanged. This is recorded as an open owner decision, not a silent relaxation:
if the owner later wants XAX-only, every BF unit below becomes a further
migration item.

## Target architecture

```text
cum_host.exe (XAX)                      generic: never parses source or picks a pass
 ├─ command surface, binary bindings    H3
 ├─ tree store, paths, atomic writes    H4
 ├─ workflow VM, worker state, cache    H5   ← instructions come only from BF programs
 ├─ tool pinning by SHA-256             H6
 ├─ OpenSSL invocation                  H7
 ├─ Git invocation, hostile-clone safe  H8
 ├─ measurement                         H9
 └─ isolation (QEMU host + Linux guest) H10
        │  framed binary requests (H0 byte_framer, H1 worker_response)
        ▼
BF decision programs (src/*.bf)          CUM: routing, policy, transforms, plans
        │
native case runner (XAX)                 H11: runs every check from data records
tests/cases/*.hex  (data)                expected bytes and exits; no test code
tests/bf/*.bf                            BF analysis tools (normalizer, attacks, oracle)
```

Bindings stop being JSON. The host reads one binary record format (`BREC`:
format id, then length-prefixed typed fields), so no XAX JSON parser is needed.
Existing JSON bindings are converted once into `BREC` hex text (data) and
decoded with the existing BF hex codec (`src/hex_codec.bf`).

Check cases are data: a hex text file per area, each case naming a pinned
program, its argv, stdin bytes, and the expected exit code, stdout and files.
The case runner H11 is the only test executor. Standard operator commands are no
longer needed for evidence once H11 passes its own fixtures.

## Replacement map

Classes follow master prompt Section 5: `XAX_CANONICAL`, `BF_CANONICAL`
(added here, per `AGENTS.md`), `TARGET_FIXTURE_DATA`,
`DECLARATIVE_NONEXECUTABLE`, `INDEPENDENT_EXTERNAL_DEPENDENCY`,
`LEGACY_MIGRATION_DEBT`. Every one of the 94 files is `LEGACY_MIGRATION_DEBT`
until its replacement passes parity; the column gives the target.

### Host (`host/`)

| Legacy file | Replacement unit | Language | Parity check |
|---|---|---|---|
| `__init__.py` (3 files) | none (package marker) | — | retire with the package |
| `bytehost/__main__.py`, `runtime_entry.py`, `dispatch.py`, `errors.py` | H3 `cum_host` command surface; error codes as status bytes | XAX | same opcodes, exit codes and error records on the old CLI's cases |
| `bytehost/transport.py` | H0 `byte_framer`, H1 `worker_response` (exist) | XAX | 43 cases already PASS; add frame-header and stale-sequence cases |
| `bytehost/process.py` | H2 `trusted_byte_runner` (exists) + H6 | XAX | 93 + NRQ2 cases already PASS; add `pinned_executable`, environment and argv-file cases |
| `bytehost/storage.py`, `scope.py`, `securestore.py`, `metadata.py`, `projection.py` | H4 `tree_store` | XAX | confined paths, reparse/ADS/8.3/trailing-dot/device-name rejection, atomic replace, inventory digests, owner-only ACL, deny-write capture |
| `bytehost/guards.py`, `discovery.py` | H4 enumerates; existing BF predicates decide (`src/scope_policy.bf`, `src/discovery.bf`) | XAX + BF | same approvals and refusals on the old cases |
| `bytehost/vm.py`, `machine.py`, `worker.py`, `cache.py`, `assembly.py` | H5 `workflow_vm` | XAX | instruction-by-instruction parity on `src/*_flow.bf` plans; resumable state record with integrity check |
| `bytehost/trusted.py`, `build.py`, `bundle.py`, `trusted_recovery.py`, `verify_bundle.ps1` | H6 `tool_pin` (SHA-256 via `bcrypt.dll`, dependency lock, receipts) | XAX | wrong digest, relative path, link/junction, swapped file all refused |
| `bytehost/crypto.py` | H7 `openssl_invoke`; argv from `src/windows_args.bf` | XAX + BF | existing AES-256-GCM CMS + Ed25519 recovery baseline still restores the 97-file scope |
| `bytehost/git_transport.py`, `archive.py` | H8 `git_invoke` (hooks, filters, system/global config disabled) | XAX | staged index, forced add, history and hostile-clone cases |
| `bytehost/metrics.py`, `resources.py` | H9 `measure` | XAX | raw per-sample records; no estimate when a counter is unavailable |
| `bytehost/qemu_isolation.py` | H10 `qemu_host` | XAX | no guest network or shares; disposable image digest |
| `providers/bytevm_agent.py`, `bytevm_seed.py`, `cgroup_run.py` | H10 guest agent | XAX (Linux target) | same job protocol inside the pinned guest |
| `providers/xax_query.py` | none: XAX's own `xaxc edit <store> <selector> <view>` | external | retire once native views cover the queried nodes |
| `tools/StandardCms.java` | BLOCKED: the Bouncy Castle interop peer is a Java library; driving it needs owned Java | — | owner decision: keep PQ interop as historical evidence, or name a non-Java second CMS implementation |

### Tests and tools (`tests/`)

| Legacy file | Replacement unit | Language | Parity check |
|---|---|---|---|
| `reference.py`, `machine_reference.py` | `tests/bf/reference.bf`: BF interpreter in BF (differential oracle) | BF | same output as the Python reference on every fixture program; independence limit: also compiled by BBC |
| `tools/normalize.py` | `tests/bf/normalize.bf`: canonical byte form (runs, clear, affine loops) | BF | equal/unequal pairs from `test_resistance.py` |
| `tools/symbolic.py` | `tests/bf/symbolic.bf`: wrapping-byte data-flow attack | BF | recovers the same shared-state variants the Python attack recovered |
| `tools/cms_fixture.py`, `tools/crypto_probe.py` | H11 cases calling OpenSSL through H7 | data | same accepted/rejected envelopes |
| `test_*.py` (37 files), `*_checks.py`, `vm_*.py`, `prepare_*.py`, `public_release_check.py` | H11 case files `tests/cases/<area>.hex` | data | each old assertion becomes a case; a case list records any assertion with no native equivalent yet |
| `projects/java/Arithmetic.java`, `projects/kotlin/Arithmetic.kt`, `projects/Runner.java` | unchanged | `TARGET_FIXTURE_DATA` | protected-input fixtures; built by external `javac`/`kotlinc` inside H11 cases; never a CUM checker |

## Gap report against the master prompt

States: PASS, PARTIAL, BLOCKED, FAIL, NOT STARTED. "Recorded" means an earlier
dated result, not rerun on 2026-11-16.

| Area (prompt section) | State | Gap |
|---|---|---|
| Language compliance (5) | PARTIAL | 94 tracked foreign files; 3 XAX host components and BF decisions exist |
| XAX generic host (5, 9) | PARTIAL | H0–H2 recorded PASS; H3–H11 NOT STARTED |
| Framed transport, EOF, zero bytes (8) | PARTIAL | recorded PASS for H0/H1; continuation-state handoff not native |
| Resumable state (7) | NOT STARTED natively | `worker.py` state record only in Python |
| `.cum/` `src/` `.cum-stain/` layout and `.gitignore` contract (4) | NOT STARTED | no `init-workspace`, `status` or project template |
| Staged-index, history, LFS, asset scan (4) | PARTIAL | `src/leak_policy.bf` and Python Git transport; no native H8 |
| External `.cumload` vault (4, 20) | PARTIAL | project identity exists; vault path, at-rest wrapping (DPAPI) and registry pinning NOT STARTED |
| Dependency lock, digest-pinned tools (24) | PARTIAL | Python `pinned_executable`; native H6 NOT STARTED |
| Hostile-input readers (11) | PARTIAL | bounded frames native; manifests, archives, capsule headers still Python |
| Signed provenance, freshness (21) | PARTIAL | Ed25519 signing recorded; release sequence, predecessor digest and rollback rejection NOT STARTED |
| Key custody, security log (22) | NOT STARTED | no key inventory, rotation drill or hash-chained log |
| Recovery (20) | Scoped PASS recorded | 97-file ciphertext-only clone; must be rerun on the native host |
| PQ (20) | Scoped PASS recorded | ML-KEM CMS interop; ordinary prepare classical only; Java peer BLOCKED above |
| BF-target transformation (13) | PARTIAL | BF passes exist; an independent attack recovered shared-state variants |
| Reconstruction resistance (18, 27) | BLOCKED | no A/B/C/D ablation, discovery vs forced inspection |
| Native XAX target projects (14) | NOT STARTED | |
| Other input languages (15) | PARTIAL | restricted Java/Kotlin integer modules only |
| Release gates, publication (23, 31) | NOT STARTED | no transactional release passed |
| Licensing (28) | NOT STARTED | |

## Increment order

Each step is drafted, then compiled and run, then recorded. A legacy file is
retired only after its replacement passes parity and nothing runs the old file.

1. H11 native case runner and the case-file format (decoded by `src/hex_codec.bf`).
   It unblocks every test port without operator scripts.
2. `tests/bf/normalize.bf` and `tests/bf/reference.bf`; retire `normalize.py`,
   `reference.py`, `machine_reference.py` after parity.
3. H6 tool pinning (SHA-256, absolute path, link refusal) and the dependency lock.
4. H4 tree store, then the `.cum/` / `src/` / `.cum-stain/` layout commands
   (`init-workspace`, `status`, `clean-stain`) with BF policy.
5. H8 Git invocation and `publish-audit` (staged index, forced add, history).
6. H3 command surface and `BREC` bindings; H5 workflow VM with resumable state.
7. H7 OpenSSL invocation; rerun the classical recovery baseline natively.
8. Vault `.cumload` with DPAPI wrapping, recipient pinning, freshness, security log.
9. H9, H10; port the remaining test areas; retire the Python host.
10. Resistance evaluation (A/B/C/D), XAX target projects, release transaction.

No step pushes, publishes or changes repository visibility without fresh owner
approval.
