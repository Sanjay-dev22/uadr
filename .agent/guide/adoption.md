---
purpose: Step-by-step guide to adopting the framework in a new or existing repository and operating it afterwards.
read_when: Human adopters; agents are directed to the init-greenfield or onboard-existing-repo workflow instead.
---
# Adoption guide

Requirements: Git and Python 3.9 or later. No packages are installed.

## Mode A: new project

Either create a repository from this template and run, inside it:

```bash
python3 .automation/uadr.py adopt --target . --name "My Project" --description "One line about it"
```

or, from a checkout of the framework, initialise a new directory:

```bash
python3 .automation/uadr.py adopt --target ../my-project --name "My Project" --description "One line about it"
```

This sets the project name, clears the template's commands, creates five starter docs as drafts (project overview, architecture overview, setup and build, coding standards, testing strategy), writes a project README, and links the skills. Then tell your agent:

> Follow `.agent/workflows/init-greenfield.md`. The project is ... (purpose, users, constraints).

The agent proposes the stack and architecture as ADRs for your approval, scaffolds the project, configures the commands, and fills the drafts.

## Mode B: existing repository

From a checkout of the framework:

```bash
python3 .automation/uadr.py adopt --target /path/to/your/repo
```

What this does and does not do:

- Adds `.agent/`, `.automation/`, `docs/templates/`, `docs/index.md`, and the adapter files.
- Never overwrites, moves, or edits an existing file. If a file such as `AGENTS.md` or `CONTRIBUTING.md` already exists, yours is kept and the framework version is placed in `.agent/onboarding/conflicts/` for a deliberate merge.
- Registers Markdown that was already present as legacy (`docs.legacy_paths`), so the gates do not fail on documents written before adoption.
- Writes `.agent/onboarding/inventory.md` (languages, manifests, entry points, module candidates, tests, pipelines and the commands they run, existing docs) and starts `.agent/onboarding/migration-report.md`.

Then tell your agent:

> Follow `.agent/workflows/onboard-existing-repo.md`.

The agent verifies the inventory against the code, configures and runs the real commands, writes the architecture overview from source, registers and documents modules, records conflicts between old docs and the code, and completes the migration report. Review the report: its assumptions and unknowns are the questions only you can answer.

Adoption is incremental. After the commands are configured and the first module is documented, agents can already work in that module. Undocumented areas are handled from code, and each task that touches one is an opportunity to document it.

## Day-to-day use

Give the agent a task with acceptance criteria (the issue template helps). The agent does the rest:

```bash
python3 .automation/uadr.py route "fix rounding error in invoice totals" --path src/billing/invoice.py
python3 .automation/uadr.py run all
python3 .automation/uadr.py check
```

| Command | Purpose |
| --- | --- |
| `route [task] [--path p] [--list]` | Workflow and minimum reading list for a task |
| `run <setup\|lint\|static\|build\|test\|all> [--strict]` | Project commands from `uadr.json` |
| `check [--only a,b] [--strict]` | Gates: structure, config, docs, links, markdown, instructions, secrets, context |
| `audit [--check] [--json]` | Token cost per tier and per route |
| `new module\|adr\|doc ...` | Create a doc from a template and update the index |
| `index [--check]` | Regenerate `docs/index.md` |
| `scan [--target dir] [--stdout\|--json]` | Repository inventory |
| `adopt --target dir [--mode] [--upgrade]` | Install or upgrade the framework |
| `sync-adapters [--copy]` | Relink skills into platform folders |

## Configuration

Everything project-specific is in `.automation/configuration/uadr.json`:

- `commands`: the shell commands for setup, format, lint, static analysis, build, and test. This is the only place a stack is named.
- `context_budget`: token limits enforced by the `context` gate.
- `required_files`, `docs.lint_paths`, `docs.legacy_paths`, `secrets.allow_paths`, `ignore_dirs`: scope of the gates.
- `adapters`: platform pointer files and skill link folders.

## Continuous integration

- GitHub Actions: `.github/workflows/uadr-checks.yml` runs the framework gates and the project commands. Add your toolchain setup step where marked.
- Azure DevOps: copy `.automation/configuration/azure-pipelines.example.yml` to `azure-pipelines.yml`.
- Any other system: run `python3 .automation/uadr.py check` and `python3 .automation/uadr.py run all --strict`.

Existing pipelines are left alone; the UADR workflow runs beside them.

## Governance

`.agent/policies/approvals.md` lists what an agent may do alone and what needs you. Enforce it outside the agent as well: protect the main branch, require review on pull requests, keep production credentials out of agent environments, and require CI to pass.

## Upgrading the framework

From a newer framework checkout:

```bash
python3 .automation/uadr.py adopt --target /path/to/your/repo --upgrade
```

Workflows, skills, policies, templates, scripts, and the guide are replaced. `AGENTS.md`, routing, memory, configuration, and all project docs are never touched. Review the diff and run the checks before committing.

## Removing the framework

Delete `.agent/`, `.agents/`, `.automation/`, `docs/templates/`, the adapter files, and `.github/workflows/uadr-checks.yml`. Project docs under `docs/` are ordinary Markdown and remain useful.
