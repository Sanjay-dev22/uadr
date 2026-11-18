# AGENTS.md

Entry point for every AI coding agent, and the only always-loaded file. Keep it short; route to detail.

## Repository

<!-- uadr:project:start -->
UADR framework template: an agent operating framework with no application code yet.
To adopt it, follow `.agent/workflows/init-greenfield.md` (new project) or `.agent/workflows/onboard-existing-repo.md` (existing code).
<!-- uadr:project:end -->

## Every task

1. Read `.agent/memory/state.md` (current state and active work).
2. Route it: `python3 .automation/uadr.py route "<task>" --path <file-or-dir>`. The output names the workflow, the module doc for those paths, and what the task must deliver.
3. Scale reading to the task. A small change inside one module needs only the router output and the code. Open the workflow and the module doc when the change spans files, alters behaviour other code depends on, or the area is unfamiliar. Open a skill in `.agent/skills/` only when a workflow step calls for it.

Never read `docs/` wholesale; `docs/index.md` lists each doc with when to read it.

## Done means

- Every behaviour change has an automated test that fails without it. A bug fix starts from a failing test.
- You ran the tests with `python3 .automation/uadr.py run test` (`run all` adds lint, static analysis, build) and report the real result. Anything you did not run is reported as not run, with the reason.
- User-visible changes are in the project's changelog, and affected docs are updated in the same change (`.agent/policies/documentation.md`).
- If you changed docs or `.agent/` files, `python3 .automation/uadr.py check` passes.
- The final message is the completion report from `.agent/policies/quality.md`.

## Rules

- Investigate before modifying: read the code and its callers first. Never invent architecture; mark gaps `UNKNOWN:` and guesses `ASSUMPTION:`.
- Record only durable facts in `.agent/memory/`.
- Never read, print, commit, or transmit secrets; never weaken a security check (`.agent/policies/security.md`).
- Stop for human approval before: production access or deployment, destructive data or schema operations, infrastructure changes, architecture decisions, new dependencies, changes to auth or security controls, rewriting git history. Full list: `.agent/policies/approvals.md`.
