# Whole-project draft: XAX-only CUM (2026-11-16)

DRAFT. Nothing in this page is executed evidence. It is the whole-project
migration shape that `AGENTS.md` requires before new tests, fixes or
optimization, written against the owner's revised master prompt
(`CUM_Master_Engineering_Development_Prompt_XAX_Only_Revised.md`, kept local).

## Language policy

On 2026-11-16 the owner directed that the master prompt overrides the former
Brainfuck-first rule, and `AGENTS.md` was updated locally to match:

- Every CUM-owned executable (decision core, transformations, host, tests,
  benchmarks, migration tools, CLI) is a canonical XAX graph, compiled by the
  pinned XAX Windows compiler and changed only through official XAX
  transactions (native `xaxc edit` batches).
- Brainfuck is a protected input language and fixture data only. BBC is the
  external compiler for BF input projects and fixtures, not for CUM code.
- A capability the installed XAX cannot provide is BLOCKED; no fallback to BF
  or any other language.

The 57 CUM-owned BF programs under `src/` and the 2 BF test workers under
`tests/workers/` therefore join the 94 foreign files as migration debt
(153 files in all). The 10 BF programs under `tests/fixtures/` are
`TARGET_FIXTURE_DATA`: they are inputs that CUM protects or compiles, not CUM logic.

## Target architecture

```text
cum_host.exe (XAX, generic)             never parses source or picks a pass
 ├─ command surface, binary bindings    H3
 ├─ tree store, paths, atomic writes    H4
 ├─ workflow VM, worker state, cache    H5   ← instructions come only from the core
 ├─ tool pinning by SHA-256             H6
 ├─ OpenSSL invocation                  H7
 ├─ Git invocation, hostile-clone safe  H8
 ├─ measurement                         H9
 └─ isolation (QEMU host + Linux guest) H10
        │  framed binary requests (H0 byte_framer, H1 worker_response)
        ▼
cum_core (XAX, CUM decisions)           C1–C6: routing, policy, transforms, plans
        │
cum_check.exe (XAX)                     H11: runs every check from data records
tests/cases/*.hex  (data)               expected bytes and exits; no test code
tests/tools (XAX)                       T1–T3: normalizer, attacks, reference interpreter
```

Bindings stop being JSON. The host reads one binary record format (`BREC`:
format id, then length-prefixed typed fields), so no XAX JSON parser is needed.

Check cases are data: a hex text file per area, each case naming a pinned
program, its argv, stdin bytes, and the expected exit code and stdout. H11
decodes the hex itself and is the only test executor. Standard operator commands
are no longer needed for evidence once H11 passes its own fixtures.

## Replacement map

Classes follow master prompt Section 5: `XAX_CANONICAL`, `TARGET_FIXTURE_DATA`,
`DECLARATIVE_NONEXECUTABLE`, `INDEPENDENT_EXTERNAL_DEPENDENCY`,
`LEGACY_MIGRATION_DEBT`. Every file below is `LEGACY_MIGRATION_DEBT` until its
replacement passes parity; the column gives the target.

### CUM decision core (`src/**/*.bf`, 57 files)

| Legacy BF programs | Replacement unit | Parity check |
|---|---|---|
| `cum.bf`, `command.bf`, `routes.bf`, `adapters.bf`, `echo.bf` | C1 command routing and adapter admission | same command bytes for every recorded request |
| `scope_policy.bf`, `path_policy.bf`, `leak_policy.bf`, `private_select.bf`, `discovery.bf`, `git_attributes.bf`, `gates.bf`, `resistance_policy.bf`, `budget_policy.bf` | C2 policies | same approve/refuse byte on every recorded case |
| `*_flow.bf`, `project.bf`, `snapshot.bf`, `maintenance.bf`, `clean_recovery.bf`, `scoped_clean_recovery.bf`, `project_recovery.bf` | C3 workflow plans (VM instruction streams) | identical instruction streams |
| `transform.bf`, `filter.bf`, `annotated_filter.bf`, `presentation.bf`, `machines/bf_*.bf`, `graphs/*.bf` | C4 BF-target transformations | same protected output bytes, then behavior parity of both builds |
| `machines/java_*.bf`, `machines/kotlin_*.bf` | C5 Java/Kotlin restricted adapters | same emitted modules |
| `hex_codec.bf`, `windows_args.bf` | C6 byte codecs (shared by host and H11) | existing 24 + 32 vectors |
| `tests/workers/fixed.bf`, `fixed_machine.bf` | host-compliance fixed workers, rebuilt as XAX | same fixed responses |

### Host (`host/`)

| Legacy file | Replacement unit | Language | Parity check |
|---|---|---|---|
| `__init__.py` (3 files) | none (package marker) | — | retire with the package |
| `bytehost/__main__.py`, `runtime_entry.py`, `dispatch.py`, `errors.py` | H3 `cum_host` command surface; error codes as status bytes | XAX | same opcodes, exit codes and error records on the old CLI's cases |
| `bytehost/transport.py` | H0 `byte_framer`, H1 `worker_response` (exist) | XAX | 43 cases already PASS; add frame-header and stale-sequence cases |
| `bytehost/process.py` | H2 `trusted_byte_runner` (exists) + H6 | XAX | 93 + NRQ2 cases already PASS; add `pinned_executable`, environment and argv-file cases |
| `bytehost/storage.py`, `scope.py`, `securestore.py`, `metadata.py`, `projection.py` | H4 `tree_store` | XAX | confined paths, reparse/ADS/8.3/trailing-dot/device-name rejection, atomic replace, inventory digests, owner-only ACL, deny-write capture |
| `bytehost/guards.py`, `discovery.py` | H4 enumerates; C2 policies decide | XAX | same approvals and refusals on the old cases |
| `bytehost/vm.py`, `machine.py`, `worker.py`, `cache.py`, `assembly.py` | H5 `workflow_vm` | XAX | instruction-by-instruction parity on the C3 plans (first against the legacy BF plans); resumable state record with integrity check |
| `bytehost/trusted.py`, `build.py`, `bundle.py`, `trusted_recovery.py`, `verify_bundle.ps1` | H6 `tool_pin` (SHA-256 via `bcrypt.dll`, dependency lock, receipts) | XAX | wrong digest, relative path, link/junction, swapped file all refused |
| `bytehost/crypto.py` | H7 `openssl_invoke`; argv quoting from C6 | XAX | existing AES-256-GCM CMS + Ed25519 recovery baseline still restores the 97-file scope |
| `bytehost/git_transport.py`, `archive.py` | H8 `git_invoke` (hooks, filters, system/global config disabled) | XAX | staged index, forced add, history and hostile-clone cases |
| `bytehost/metrics.py`, `resources.py` | H9 `measure` | XAX | raw per-sample records; no estimate when a counter is unavailable |
| `bytehost/qemu_isolation.py` | H10 `qemu_host` | XAX | no guest network or shares; disposable image digest |
| `providers/bytevm_agent.py`, `bytevm_seed.py`, `cgroup_run.py` | H10 guest agent | XAX (Linux target) | same job protocol inside the pinned guest |
| `providers/xax_query.py` | none: XAX's own `xaxc edit <store> <selector> <view>` | external | retire once native views cover the queried nodes |
| `tools/StandardCms.java` | BLOCKED: the Bouncy Castle interop peer is a Java library; driving it needs owned Java | — | owner decision: keep PQ interop as historical evidence, or name a non-Java second CMS implementation |

### Tests and tools (`tests/`)

| Legacy file | Replacement unit | Language | Parity check |
|---|---|---|---|
| `reference.py`, `machine_reference.py` | T1 BF reference interpreter (differential oracle for BF targets) | XAX | same output as the Python reference on every fixture program; independent of BBC |
| `tools/normalize.py` | T2 BF normalizer: canonical byte form (runs, clear, affine loops) | XAX | equal/unequal pairs from `test_resistance.py` |
| `tools/symbolic.py` | T3 wrapping-byte data-flow attack | XAX | recovers the same shared-state variants the Python attack recovered |
| `tools/cms_fixture.py`, `tools/crypto_probe.py` | H11 cases calling OpenSSL through H7 | data | same accepted/rejected envelopes |
| `test_*.py` (37 files), `*_checks.py`, `vm_*.py`, `prepare_*.py`, `public_release_check.py` | H11 case files `tests/cases/<area>.hex` | data | each old assertion becomes a case; a case list records any assertion with no native equivalent yet |
| `projects/java/Arithmetic.java`, `projects/kotlin/Arithmetic.kt`, `projects/Runner.java` | unchanged | `TARGET_FIXTURE_DATA` | protected-input fixtures; built by external `javac`/`kotlinc` inside H11 cases; never a CUM checker |

## Gap report against the master prompt

States: PASS, PARTIAL, BLOCKED, FAIL, NOT STARTED. "Recorded" means an earlier
dated result, not rerun on 2026-11-16.

| Area (prompt section) | State | Gap |
|---|---|---|
| Language compliance (5) | PARTIAL | 153 CUM-owned non-XAX files (94 foreign + 59 BF); 3 XAX host components exist |
| XAX generic host (5, 9) | PARTIAL | H0–H2 recorded PASS; H3–H11 NOT STARTED |
| Framed transport, EOF, zero bytes (8) | PARTIAL | recorded PASS for H0/H1; continuation-state handoff not native |
| Resumable state (7) | NOT STARTED natively | `worker.py` state record only in Python |
| `.cum/` `src/` `.cum-stain/` layout and `.gitignore` contract (4) | NOT STARTED | no `init-workspace`, `status` or project template |
| Staged-index, history, LFS, asset scan (4) | PARTIAL | legacy BF leak policy and Python Git transport; no native H8 |
| External `.cumload` vault (4, 20) | PARTIAL | project identity exists; vault path, at-rest wrapping (DPAPI) and registry pinning NOT STARTED |
| Dependency lock, digest-pinned tools (24) | PARTIAL | Python `pinned_executable`; native H6 NOT STARTED |
| Hostile-input readers (11) | PARTIAL | bounded frames native; manifests, archives, capsule headers still Python |
| Signed provenance, freshness (21) | PARTIAL | Ed25519 signing recorded; release sequence, predecessor digest and rollback rejection NOT STARTED |
| Key custody, security log (22) | NOT STARTED | no key inventory, rotation drill or hash-chained log |
| Recovery (20) | Scoped PASS recorded | 97-file ciphertext-only clone; must be rerun on the native host |
| PQ (20) | Scoped PASS recorded | ML-KEM CMS interop; ordinary prepare classical only; Java peer BLOCKED above |
| BF-target transformation (13) | PARTIAL | legacy BF-authored passes exist, to be rebuilt as C4; an independent attack recovered shared-state variants |
| Reconstruction resistance (18, 27) | BLOCKED | no A/B/C/D ablation, discovery vs forced inspection |
| Native XAX target projects (14) | NOT STARTED | |
| Other input languages (15) | PARTIAL | restricted Java/Kotlin integer modules only |
| Release gates, publication (23, 31) | NOT STARTED | no transactional release passed |
| Licensing (28) | NOT STARTED | |

## Increment order

Each step is drafted, then compiled and run, then recorded. A legacy file is
retired only after its replacement passes parity and nothing runs the old file.

1. H11 native case runner and the hex case-file format.
   It unblocks every test port without operator scripts.
2. T1 reference interpreter and T2 normalizer; retire `normalize.py`,
   `reference.py`, `machine_reference.py` after parity.
3. H6 tool pinning (SHA-256, absolute path, link refusal) and the dependency lock.
4. H4 tree store, then the `.cum/` / `src/` / `.cum-stain/` layout commands
   (`init-workspace`, `status`, `clean-stain`) with C2 policy.
5. H8 Git invocation and `publish-audit` (staged index, forced add, history).
6. H3 command surface and `BREC` bindings; H5 workflow VM with resumable state.
7. H7 OpenSSL invocation; rerun the classical recovery baseline natively.
8. Vault `.cumload` with DPAPI wrapping, recipient pinning, freshness, security log.
9. H9, H10; port the remaining test areas; retire the Python host.
10. Resistance evaluation (A/B/C/D), XAX target projects, release transaction.

No step pushes, publishes or changes repository visibility without fresh owner
approval.
