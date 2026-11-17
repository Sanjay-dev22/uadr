# AGENTS.md

Entry point for every AI coding agent. This file is the only always-loaded context: keep it short and route to detail instead of adding it here.

## Repository

<!-- uadr:project:start -->
UADR framework template: an agent operating framework with no application code yet.
To adopt it, follow `.agent/workflows/init-greenfield.md` (new project) or `.agent/workflows/onboard-existing-repo.md` (existing code).
<!-- uadr:project:end -->

## Start every task

1. Read `.agent/memory/state.md` (current state and active work).
2. Route the task: `python3 .automation/uadr.py route "<task description>" --path <file-or-dir>`. It names one workflow, the module doc for those paths, and conditional reading. Same data: `.agent/routing/routes.json`.
3. Read only what the route lists. Open a skill in `.agent/skills/` only when a workflow step calls for it.
4. Execute the workflow: Understand, Plan, Analyze, Implement, Test, Review, Document, Complete.

Do not read `docs/` wholesale; `docs/index.md` lists each doc with when to read it.

## Commands

- Project commands: `python3 .automation/uadr.py run <setup|lint|static|build|test|all>`
- Framework gates: `python3 .automation/uadr.py check`
- New module doc or ADR: `python3 .automation/uadr.py new <module|adr> ...`

## Rules

- Investigate before modifying: read the code and its callers before changing it. Never invent architecture; mark gaps `UNKNOWN:` and guesses `ASSUMPTION:`.
- Never report tests, builds, or checks as passing unless you ran them in this session. If you could not run something, say so and why.
- Update affected docs in the same change (`.agent/policies/documentation.md`). Record only durable facts in `.agent/memory/`.
- Never read, print, commit, or transmit secrets; never weaken a security check (`.agent/policies/security.md`).
- Stop and get human approval before: production access or deployment, destructive data or schema operations, infrastructure changes, architecture decisions, new dependencies, changes to auth or security controls, rewriting git history. Full list: `.agent/policies/approvals.md`.
- Finish with the completion report in `.agent/policies/quality.md`.
