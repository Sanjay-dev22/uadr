---
purpose: Mode A procedure: start a new project on the framework.
read_when: The router selects the init-greenfield route, or state.md says initialisation is pending.
---
# Workflow: init-greenfield

## Objective

Turn the template into a project repository with real requirements, decided architecture, working commands, and a first module.

## Required context

- Project name, purpose, primary users, and any mandated technology or constraints. Ask for what is missing; do not choose a stack silently.

## Documents to read

- Output of `uadr.py route init-greenfield --path <paths>`; nothing else up front.
- `.agent/policies/documentation.md`.

## Steps

1. Run `python3 .automation/uadr.py adopt --target . --name "<name>" --description "<one line>"` in a repository created from the template (or `--target <new-dir>` from a framework checkout).
2. Fill `docs/project/overview.md` and create requirements with `uadr.py new doc requirements` from what the human provided.
3. Propose the technology stack and architecture with alternatives; record each decision as an ADR and get approval.
4. Fill `docs/architecture/overview.md` from the accepted ADRs.
5. Scaffold the project with the stack's standard tooling and layout. Create only directories that hold files.
6. Set `commands` in `.automation/configuration/uadr.json` and confirm each runs.
7. Add CI from `.github/workflows/uadr-checks.yml` or `.automation/configuration/azure-pipelines.example.yml`.
8. Register the first module with `uadr.py new module`, implement a minimal vertical slice with a test, and fill the draft docs (setup, standards, testing).
9. Update the project block in `AGENTS.md`, then run `uadr.py index`, `check`, and `audit`.

## Files that may be modified

- Everything in the new repository.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- `python3 .automation/uadr.py audit --check` within budget.

## Completion criteria

- Draft docs filled or deliberately deleted; commands configured; first slice builds and tests pass.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- All starter docs, ADRs, `AGENTS.md` project block, `.agent/memory/state.md`.

## Human approval

- Technology stack, architecture, licence, and hosting choices.
