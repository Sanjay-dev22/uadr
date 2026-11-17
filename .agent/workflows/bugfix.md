---
purpose: Procedure for investigating and resolving a defect.
read_when: The router selects the bugfix route.
---
# Workflow: bugfix

## Objective

Find the root cause of a defect, fix it at the cause, and prevent regression with a test.

## Required context

- Observed behaviour, expected behaviour, and reproduction steps or evidence (error, log, failing input).

## Documents to read

- Output of `uadr.py route bugfix --path <paths>`; nothing else up front.
- The module doc for the failing area.
- `.agent/memory/known-issues.md` if the symptom may be known.

## Steps

1. State expected versus actual behaviour and the evidence.
2. Reproduce the defect, ideally as a failing automated test. If you cannot reproduce, report what you tried before changing anything.
3. Trace from symptom to cause (skill: `root-cause-analysis`). Confirm the cause explains all the evidence.
4. Check where else the same cause occurs and who depends on the faulty behaviour.
5. Fix the cause with the smallest change. Do not patch the symptom or refactor nearby code.
6. Confirm the new test fails without the fix and passes with it.
7. Run validation, review the diff, update docs, and report including the root cause.

## Files that may be modified

- The faulty code and its tests.
- Docs listed below.

## Validation

- The regression test passes with the fix and fails without it.
- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.

## Completion criteria

- Root cause identified and stated.
- Fix validated; regression test in place.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Module doc if documented behaviour or rules were wrong or changed.
- `.agent/memory/known-issues.md`: remove the entry if this was listed; add one if a wider problem remains.
- `CHANGELOG.md` for user-visible fixes.

## Human approval

- The fix needs a data repair, a contract change, or a change outside the failing module.
