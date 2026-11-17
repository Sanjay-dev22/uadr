---
purpose: Catalogue of documentation templates and how to instantiate them.
read_when: You need to create a project document.
---
# Documentation templates

Files here are templates, not project documentation. They are never loaded as context and are excluded from `docs/index.md`. Real docs live in the other `docs/` folders and are created on demand; an absent doc means "not written yet", not "missing".

Create a doc with `python3 .automation/uadr.py new ...`. The command copies the template to its target path, fills the placeholders, and regenerates the index.

| Template | Command | Target |
| --- | --- | --- |
| `project-overview` | `new doc project-overview` | `docs/project/overview.md` |
| `requirements` | `new doc requirements` | `docs/project/requirements.md` |
| `architecture-overview` | `new doc architecture-overview` | `docs/architecture/overview.md` |
| `data-flow-and-integrations` | `new doc data-flow-and-integrations` | `docs/architecture/data-flow-and-integrations.md` |
| `adr` | `new adr "<title>"` | `docs/decisions/NNNN-<slug>.md` |
| `module` | `new module <name> --paths <glob>` | `docs/modules/<name>.md` |
| `api` | `new doc api` | `docs/api/index.md` |
| `database` | `new doc database` | `docs/database/schema.md` |
| `setup-and-build` | `new doc setup-and-build` | `docs/development/setup-and-build.md` |
| `coding-standards` | `new doc coding-standards` | `docs/development/coding-standards.md` |
| `testing-strategy` | `new doc testing-strategy` | `docs/testing/testing-strategy.md` |
| `deployment` | `new doc deployment` | `docs/operations/deployment.md` |
| `observability` | `new doc observability` | `docs/operations/observability.md` |
| `security` | `new doc security` | `docs/security/security.md` |

Use `--out <path>` to place a doc elsewhere, for example to match an existing repository's documentation layout.

## Conventions

- `{{NAME}}` style placeholders are replaced by the command. HTML comments are guidance for the author and must be removed as sections are filled.
- New docs start with `status: draft`. Set `status: verified` once every statement is confirmed and no guidance comments remain.
- Delete sections that do not apply instead of leaving them empty.
