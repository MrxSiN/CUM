@AGENTS.md

# Claude rules

## Commits

- Do not add Claude as an author, co-author or contributor. No `Co-Authored-By: Claude`
  trailer, no "Generated with Claude Code" line, no Claude identity in author or
  committer fields.
- Only exception: a commit whose changes are limited to benchmark material may
  credit Claude, if the owner asks for it.
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`) with a plain-English
  summary of what changed.

## Pull requests

- The title is one plain sentence that a non-specialist can understand. Say what the
  change does, not internal jargon. Example: "Let BF build Windows command lines and
  start external tools".
- The description has three short sections:
  - **What this adds**: bullets, each saying what the change does and why it matters.
  - **Evidence**: what was actually run and passed, with links to `evidence/` or `docs/`.
  - **Not done yet**: open gaps, failures and anything not accepted.
- Spell out abbreviations on first use. Report only evidence that was actually
  executed; drafted checks are not results.
- Opening, editing or merging a pull request, or pushing, needs fresh owner approval
  (see `AGENTS.md`).

## Documentation

- Update the affected `docs/` pages and `docs/STATUS.md` in the same change.
- Keep files UTF-8. Check for mojibake such as `â€”` before committing.
