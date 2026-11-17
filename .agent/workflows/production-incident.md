---
purpose: Procedure for investigating a problem in a deployed environment.
read_when: The router selects the production-incident route.
---
# Workflow: production-incident

## Objective

Help restore service and find the cause using evidence, without taking any production action unapproved.

## Required context

- Symptom, impact, start time, affected environment, recent deployments or changes, and the evidence available.

## Documents to read

- Output of `uadr.py route production-incident --path <paths>`; nothing else up front.
- Observability and deployment docs.
- The module doc once a suspect component is identified.

## Steps

1. Record symptom, impact, timeline, and what changed recently. Work from evidence supplied or approved for access.
2. Separate mitigation from diagnosis. Propose the fastest safe mitigation (rollback, flag, scale) for a human to approve and execute.
3. Form hypotheses and rank them by fit to the evidence (skill: `root-cause-analysis`).
4. Test hypotheses by reading code, configuration, and logs, and by reproducing outside production.
5. State the root cause only when it explains the full timeline; otherwise report the leading hypotheses and missing evidence.
6. Route the permanent fix through the bugfix workflow, with a regression test.
7. Write a short incident summary: impact, timeline, cause, fix, and preventive actions.

## Files that may be modified

- Nothing in production.
- The fix goes through the bugfix workflow on a branch.

## Validation

- The fix is validated under the bugfix workflow.
- Claims about production are tied to cited evidence.

## Completion criteria

- Mitigation proposed or applied by a human; cause identified or next evidence requested; fix routed.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- `docs/operations/` runbook or troubleshooting entry for this failure mode.
- `.agent/memory/known-issues.md` if the cause is not yet fixed.

## Human approval

- Always, for any production access, command, restart, rollback, deployment, or data change.
