---
purpose: Rules for when and how agents create and update documentation, and how docs stay a single source of truth.
read_when: A change affects documented behaviour, you are creating a doc, or you are onboarding a repository.
---
# Documentation policy

## What to update

| Change | Update |
| --- | --- |
| Module behaviour, entry points, data models, configuration, business rules | That module's doc in `docs/modules/` |
| New module or moved code | `uadr.py new module`, or edit `.agent/routing/modules.json` paths |
| Public interface | `docs/api/` |
| Schema or migration | `docs/database/` |
| Build, setup, or test commands | `docs/development/`, `docs/testing/`, and `commands` in `.automation/configuration/uadr.json` |
| Architecture, technology, or cross-cutting pattern | New ADR in `docs/decisions/`, then `docs/architecture/` |
| Deploy, config, or runbook change | `docs/operations/` |
| User-visible change | `CHANGELOG.md` |
| Project state, new limitation, new debt | `.agent/memory/` under its rules |

A change that alters none of these needs no documentation update; say so in the completion report.

## How to write

- Every doc starts with frontmatter: `purpose`, `read_when`, and `status` (`draft`, `verified`, or `deprecated`). `docs/index.md` is generated from it with `python3 .automation/uadr.py index`; never edit the index by hand.
- Create docs from `docs/templates/` with `uadr.py new`. Delete template sections that do not apply; do not leave empty headings.
- Document only what you verified in source, configuration, or by running the system. Write `UNKNOWN: <question>` for gaps and `ASSUMPTION: <claim> (basis)` for inferences. Set `status: verified` only when no unverified section remains.
- One fact, one place. Link to the owning doc instead of restating it. Instruction files for specific agents stay thin pointers to `AGENTS.md`.
- Describe the current system. History belongs in ADRs, the changelog, and git.
- Where an existing doc contradicts the code, the code is the evidence: fix the doc, or record the conflict if intent is unclear. Never overwrite a human-written doc without reading it.
- Keep module docs focused on one module so they can be loaded alone.
