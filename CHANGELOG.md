<!-- uadr:template-file -->
# Changelog

Notable changes to the UADR framework. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 1.1.0

### Added

- Benchmark harness (`benchmark/`): mines real upstream fixes as tasks, runs a headless agent with and without the framework, and scores with hidden tests. Results for pallets/click with two models are included.
- `uadr.py route` prints what the task must deliver, read from the workflow.
- `uadr.py audit` reports the token cost of preloaded skill descriptions.
- `adopt --upgrade` refreshes the framework rules in `AGENTS.md` while keeping the project block.

### Changed

- `AGENTS.md` states the definition of done directly (test for every behaviour change, real test results, changelog) and tells agents to scale reading to the task. The benchmark showed agents act on the entry point and rarely open a workflow.
- Skill descriptions shortened to reduce always-loaded context.
- `uadr.py check` is required only when docs or framework files change.
- README and the token-efficiency guide now report measured results, including that the framework increased cost on the benchmarked tasks.

## 1.0.0

### Added

- Agent entry point (`AGENTS.md`) with thin adapters for Claude Code and GitHub Copilot.
- Task router with 15 routes, workflows, and 12 on-demand skills.
- Policies for approvals, security, quality, context loading, and documentation.
- Documentation templates with generated index and module registry.
- Automation CLI: route, run, check, audit, new, index, scan, adopt, sync-adapters.
- Greenfield and existing-repository adoption modes.
- CI examples for GitHub Actions and Azure DevOps.
