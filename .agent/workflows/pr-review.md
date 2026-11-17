---
purpose: Procedure for reviewing a proposed change.
read_when: The router selects the pr-review route.
---
# Workflow: pr-review

## Objective

Give an accurate, prioritised review of a change: correctness first, then security, tests, design, and docs.

## Required context

- The diff, its stated intent, and the linked task or issue.

## Documents to read

- Output of `uadr.py route pr-review --path <paths>`; nothing else up front.
- `.agent/policies/quality.md` and the module docs for changed paths.

## Steps

1. Read the description and identify what the change claims to do.
2. Read the whole diff, then the surrounding code of each non-trivial hunk; do not review hunks in isolation.
3. Check correctness: logic, edge cases, error handling, concurrency, and callers of changed interfaces.
4. Check security against the security policy (skill: `security-analysis`).
5. Check tests: do they cover the change and would they fail without it? Run them if you can.
6. Check design, conventions, and scope (skill: `code-quality-review`); check required docs were updated.
7. Verify each finding against the code before reporting it.
8. Report findings ordered by severity with file, line, reason, and suggested fix. Separate blocking from optional.

## Files that may be modified

- Nothing, unless asked to apply fixes; then only the reviewed change.

## Validation

- State which checks and tests you ran and which you did not.

## Completion criteria

- Every changed file read; findings verified and prioritised; a clear recommendation given.

## Documentation updates

- None by the reviewer. Missing documentation updates are review findings.

## Human approval

- Approving, merging, or closing on behalf of a human.
