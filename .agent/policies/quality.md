---
purpose: Definition of done, honest-reporting rules, and the completion report format.
read_when: Before declaring any task complete, and when reviewing a change.
---
# Quality policy

## Definition of done

A task is done when all of the following hold:

1. The acceptance criteria are met and nothing outside the task's scope changed.
2. New or changed behaviour has automated tests, and a bug fix has a test that fails without the fix.
3. `python3 .automation/uadr.py run all` was executed and every configured command passed.
4. `python3 .automation/uadr.py check` passed.
5. Affected documentation is updated in the same change.
6. No secrets, debug code, commented-out code, or unrelated formatting changes are in the diff.
7. Required approvals were obtained and are referenced.

## Honest reporting

- Report a command as passed only if you ran it in this session and saw it pass.
- A command reported `NOT CONFIGURED` or one you could not run is reported as **not run**, with the reason.
- Report failures with the relevant output. Never delete, skip, or weaken a test to obtain a pass.
- Distinguish verified facts from assumptions.

## Completion report

End every task with this report (also the PR description body):

```text
Summary: <what changed and why, 1-3 sentences>
Route: <route name>   Modules: <names>
Changes: <files or areas touched>
Validation:
  test: <passed | failed | not run - reason>
  build / lint / static: <passed | failed | not run - reason>
  uadr check: <passed | failed | not run - reason>
Docs updated: <paths, or "none needed" with reason>
Approvals: <who approved what, or "none required">
Risks and follow-ups: <remaining risk, UNKNOWN / ASSUMPTION items, debt created>
```
