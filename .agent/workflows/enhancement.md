---
purpose: Procedure for changing or extending an existing feature.
read_when: The router selects the enhancement route.
---
# Workflow: enhancement

## Objective

Change existing behaviour as requested without breaking current consumers.

## Required context

- The current behaviour, the desired behaviour, and who depends on the current behaviour.

## Documents to read

- Output of `uadr.py route enhancement --path <paths>`; nothing else up front.
- The module doc for the feature's module.

## Steps

1. State current versus desired behaviour in one or two sentences each.
2. Find the implementation and every caller and consumer of what will change (skill: `dependency-analysis`).
3. Read the existing tests; they define behaviour you must preserve or deliberately change.
4. Decide whether the change is backward compatible. If not, stop for approval.
5. Plan the change and the tests to add or adjust.
6. Implement, updating tests so they describe the new behaviour; do not delete tests to make the suite pass.
7. Run validation, review the diff, update docs, and report.

## Files that may be modified

- Source and tests of the feature and its direct callers.
- Docs listed below.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- Unchanged behaviour is still covered by passing tests.

## Completion criteria

- Desired behaviour implemented; no consumer broken unintentionally.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Module doc where behaviour, rules, or configuration changed.
- `CHANGELOG.md` for user-visible changes.

## Human approval

- Breaking change to a public contract or to stored data.
