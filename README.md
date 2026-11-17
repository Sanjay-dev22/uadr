<!-- uadr:template-file -->
# Universal Agentic Development Repository (UADR)

An operating framework that makes any repository agent-first. It tells an AI coding agent where to start, what to read, what not to read, how to change code safely, how to prove the change works, and how to leave knowledge for the next agent. It works for new and existing projects, and is independent of language, architecture, and AI provider.

It is not a boilerplate application. It adds three things beside your code: a short entry point with a task router, on-demand workflows and skills, and dependency-free automation that enforces the rules.

## How it works

```text
AGENTS.md (about 570 tokens; with preloaded skill descriptions, about 1,700 measured)
   -> uadr.py route "<task>" --path <file>
        -> one workflow            .agent/workflows/
        -> the module doc(s)       docs/modules/        for the paths being touched
        -> conditional docs        only when their stated condition holds
        -> skills                  .agent/skills/       one at a time, when a step needs it
   -> implement -> uadr.py run all + uadr.py check -> update docs and memory -> completion report
```

The docs an agent is routed to for a typical task are an estimated 1,300 to 1,600 tokens, about 5% of the framework and documentation corpus. See [token efficiency](.agent/guide/token-efficiency.md).

## Measured results

The framework was benchmarked with real agent runs on real upstream bug fixes, judged by hidden tests: 156 runs on [pallets/click](https://github.com/pallets/click) (13,000 lines) and [sympy/sympy](https://github.com/sympy/sympy) (530,000 lines), with two models. Read [benchmark/README.md](benchmark/README.md) before adopting. In short:

- The framework **cost more per task and never saved tokens**: 24% to 86% more than the bare repository on click, 31% more on SymPy.
- Every condition solved every task, so no correctness benefit was shown, and these tasks could not have shown one.
- A seven-line hand-written `AGENTS.md` produced the same test discipline at equal or lower cost.
- Agents ran the router but never opened a workflow or module doc, so the generated per-module docs went unused.
- Not yet measured: vague, symptom-only requests where the agent must first locate the code; multi-session work; governance and safety behaviour.

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

- [Benchmark: method, results, limits](benchmark/README.md)
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
