---
purpose: Procedure for restructuring code without changing behaviour.
read_when: The router selects the refactor route.
---
# Workflow: refactor

## Objective

Improve internal structure while observable behaviour stays identical.

## Required context

- The structural problem being solved and the boundary of the refactor.

## Documents to read

- Output of `uadr.py route refactor --path <paths>`; nothing else up front.
- The module doc and coding standards.

## Steps

1. State the goal and the explicit scope; refuse scope creep.
2. Map callers and dependents of everything that will move or change shape (skill: `dependency-analysis`).
3. Verify tests cover the behaviour. If coverage is thin, add characterisation tests first and commit them separately.
4. Run the tests before starting to establish a passing baseline.
5. Refactor in small steps, running tests after each.
6. Review the result against the stated goal (skill: `code-quality-review`).
7. Run validation, update docs, and report.

## Files that may be modified

- Source inside the stated scope and its tests.
- Call sites that must follow a rename or move.

## Validation

- The same tests pass before and after, with no assertions weakened.
- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.

## Completion criteria

- Goal achieved; behaviour unchanged; no functional change mixed in.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Module doc if entry points, important classes, or file layout changed.
- `.agent/routing/modules.json` if paths moved.

## Human approval

- Moving code across module boundaries or changing a public interface.
