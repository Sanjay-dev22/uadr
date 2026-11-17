---
purpose: Mode B procedure: adapt an existing repository to the framework without changing the application.
read_when: The router selects the onboard-existing-repo route, or AGENTS.md says onboarding is in progress.
---
# Workflow: onboard-existing-repo

## Objective

Make an existing codebase agent-ready by documenting what is actually there. The application, its layout, and its pipelines stay untouched.

## Required context

- The framework installed with `python3 <uadr>/.automation/uadr.py adopt --target <repo>`.
- `.agent/onboarding/inventory.md` (generated facts) and `.agent/onboarding/migration-report.md` (your working record).

## Documents to read

- Output of `uadr.py route onboard-existing-repo --path <paths>`; nothing else up front.
- `.agent/policies/documentation.md`.
- Existing project docs and instruction files, as each step reaches them.

## Steps

1. Read the inventory. Verify its candidates (languages, entry points, modules, tests, pipelines) against the repository (skill: `repository-exploration`).
2. Read existing documentation and agent instruction files. List what is current, stale, or contradicted by code in the report.
3. Resolve `.agent/onboarding/conflicts/`: merge each pre-existing instruction file with the framework version so `AGENTS.md` stays a thin entry point and project knowledge moves into `docs/`. Get approval before replacing a human-written file.
4. Set real `commands` in `.automation/configuration/uadr.json` from the existing build files and CI; run them and record the result.
5. Derive the architecture from source and write `docs/architecture/overview.md` (skills: `architecture-discovery`, `dependency-analysis`).
6. Register modules along the boundaries the code already has: `uadr.py new module <name> --paths <glob>`; fill each doc from code (skill: `documentation-generation`). Start with the most-changed modules; the rest can follow incrementally.
7. Document APIs, data stores, and integrations that exist, from their definitions in code.
8. Create remaining docs only where a gap blocks agents: setup and build, testing strategy, coding standards as observed in the code.
9. Record risks, debt, and undocumented assumptions (skill: `technical-debt-identification`) in `.agent/memory/known-issues.md`.
10. Update the project block in `AGENTS.md`, run `uadr.py index`, `check`, and `audit`, and complete the migration report: done, gaps, conflicts, recommendations.

## Files that may be modified

- `docs/`, `.agent/`, `.automation/configuration/`, agent instruction files.
- Never source code, build files, existing pipelines, or existing docs' locations.

## Validation

- `python3 .automation/uadr.py check` passes.
- `python3 .automation/uadr.py run all` executed; results recorded as observed, including failures that predate onboarding.
- Spot-check: every entry point and command in the new docs exists in the repository.

## Completion criteria

- Entry point, commands, architecture overview, and at least the core modules documented.
- Every unverified statement marked `UNKNOWN:` or `ASSUMPTION:`.
- Migration report complete; `AGENTS.md` no longer says onboarding is in progress.

## Documentation updates

- Everything above is documentation. Also set `.agent/memory/state.md` to the real project state.
- Delete `.agent/onboarding/conflicts/` once merged; keep the report until gaps are closed.

## Human approval

- Replacing or merging existing human-written instruction or documentation files.
- Any change outside the paths listed above, including moving files or editing CI.
