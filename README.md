<!-- uadr:template-file -->
# Universal Agentic Development Repository (UADR)

An operating framework that makes any repository agent-first. It tells an AI coding agent where to start, what to read, what not to read, how to change code safely, how to prove the change works, and how to leave knowledge for the next agent. It works for new and existing projects, and is independent of language, architecture, and AI provider.

It is not a boilerplate application. It adds three things beside your code: a short entry point with a task router, on-demand workflows and skills, and dependency-free automation that enforces the rules.

## How it works

```text
AGENTS.md (about 540 tokens, the only always-loaded file)
   -> uadr.py route "<task>" --path <file>
        -> one workflow            .agent/workflows/
        -> the module doc(s)       docs/modules/        for the paths being touched
        -> conditional docs        only when their stated condition holds
        -> skills                  .agent/skills/       one at a time, when a step needs it
   -> implement -> uadr.py run all + uadr.py check -> update docs and memory -> completion report
```

A typical task loads about 1,300 to 1,600 tokens of framework and documentation context before reading code, which is around 5% of the full corpus. See [token efficiency](.agent/guide/token-efficiency.md).

## Quick start

Requires Git and Python 3.9 or later. Nothing to install.

**New project (Mode A)**

```bash
python3 .automation/uadr.py adopt --target ../my-project --name "My Project" --description "What it does"
```

Then ask your agent to follow `.agent/workflows/init-greenfield.md`.

**Existing repository (Mode B)**

```bash
python3 .automation/uadr.py adopt --target /path/to/existing/repo
```

Nothing existing is overwritten or moved. Then ask your agent to follow `.agent/workflows/onboard-existing-repo.md`; it documents the system from the actual source and produces a migration report.

Full instructions: [adoption guide](.agent/guide/adoption.md).

## What is in the box

| Area | Contents |
| --- | --- |
| Entry point | [AGENTS.md](AGENTS.md), with thin adapters for Claude Code (`CLAUDE.md`) and GitHub Copilot (`.github/copilot-instructions.md`) |
| Routing | [routes.json](.agent/routing/routes.json): 15 task types mapped to a workflow, required and conditional docs, skills, and an approval gate. [modules.json](.agent/routing/modules.json): source paths mapped to module docs |
| Workflows | Feature, enhancement, bug fix, refactor, architecture change, API, database, dependency upgrade, tests, security review, performance, PR review, production incident, greenfield initialisation, existing-repository onboarding. Each has the same nine sections |
| Skills | Twelve on-demand techniques in Agent Skills format: repository exploration, architecture discovery, dependency analysis, codebase navigation, root-cause analysis, feature implementation, test generation, documentation generation, security analysis, performance analysis, code-quality review, technical-debt identification |
| Policies | [Approvals](.agent/policies/approvals.md), [security](.agent/policies/security.md), [quality](.agent/policies/quality.md), [context loading](.agent/policies/context-loading.md), [documentation](.agent/policies/documentation.md) |
| Memory | [Project state, handover, known issues](.agent/memory/README.md): small, durable, Git-tracked, budget-enforced |
| Doc templates | [Fourteen templates](docs/templates/README.md) covering project, architecture, ADRs, modules, API, database, development, testing, operations, and security, with a generated index |
| Automation | One CLI, `python3 .automation/uadr.py`, with `route`, `run`, `check`, `audit`, `new`, `index`, `scan`, `adopt`, `sync-adapters` |
| Quality gates | Structure, configuration, documentation, links, Markdown, instruction consistency, secret detection, context budget; plus the project's own lint, static analysis, build, and test commands |
| CI | [GitHub Actions workflow](.github/workflows/uadr-checks.yml) and an [Azure DevOps example](.automation/configuration/azure-pipelines.example.yml) |

## Documentation

- [Framework architecture and diagram](.agent/guide/architecture.md)
- [Adoption and usage guide](.agent/guide/adoption.md)
- [Token efficiency and measurements](.agent/guide/token-efficiency.md)
- [Agent platform compatibility](.agent/guide/platforms.md)
- [Walkthrough: building a feature](.agent/guide/walkthrough-feature.md)
- [Walkthrough: fixing a bug](.agent/guide/walkthrough-bugfix.md)

## Verify this checkout

```bash
python3 .automation/uadr.py check          # eight framework gates
python3 .automation/uadr.py run test       # automation self-tests
python3 .automation/uadr.py audit --check  # context token budgets
```

## Principles

Agent first. Minimal context. Progressive disclosure. Single source of truth. Self-discovery from code. Autonomous execution with honest reporting. Durable, small memory. Quality by default. Technology agnostic. Human governance for anything sensitive or irreversible.
