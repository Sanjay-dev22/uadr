---
purpose: Procedure for assessing and fixing security weaknesses.
read_when: The router selects the security-review route.
---
# Workflow: security-review

## Objective

Identify security weaknesses in a defined scope, report them accurately, and fix what is in scope.

## Required context

- The scope (module, change, or finding) and whether the task is review only or review and fix.

## Documents to read

- Output of `uadr.py route security-review --path <paths>`; nothing else up front.
- `.agent/policies/security.md` and the module doc.
- The project security doc if it exists.

## Steps

1. Define scope and the assets and trust boundaries inside it.
2. Map entry points and trace untrusted input to sensitive operations (skill: `security-analysis`).
3. Check authentication, authorisation, input handling, secrets, data exposure, dependencies, and error handling.
4. Run `python3 .automation/uadr.py check --only secrets` and the project's security tooling if configured.
5. For each finding record location, impact, likelihood, evidence, and fix; rate severity. Verify before reporting.
6. Fix in-scope findings within existing controls, each with a test demonstrating the weakness is closed.
7. Report findings privately as the security policy requires; do not put exploit details in public text.

## Files that may be modified

- In review-only mode: nothing.
- In fix mode: code and tests for the in-scope findings.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- Each fix has a test that fails against the vulnerable code.

## Completion criteria

- Findings reported with severity and evidence; in-scope fixes validated; remaining risk listed.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Project security doc for new controls or accepted risks.
- `.agent/memory/known-issues.md` for unfixed non-sensitive weaknesses only.

## Human approval

- Changing authentication, authorisation, or cryptography.
- Any disclosure outside the maintainers; any secret rotation.
