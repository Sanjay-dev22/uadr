---
purpose: Procedure for adding or repairing automated tests.
read_when: The router selects the tests route.
---
# Workflow: tests

## Objective

Increase confidence in existing behaviour with reliable, meaningful tests, without changing production behaviour.

## Required context

- The behaviour to cover and the reason (gap, flaky test, upcoming change).

## Documents to read

- Output of `uadr.py route tests --path <paths>`; nothing else up front.
- Testing strategy and the module doc.

## Steps

1. Identify the behaviour and its current coverage by reading existing tests.
2. Choose the lowest test level that can prove the behaviour, per the testing strategy.
3. Follow the existing test layout, naming, fixtures, and helpers (skill: `test-generation`).
4. Write tests for normal, boundary, and failure cases; assert outcomes, not implementation details.
5. Prove each test can fail: temporarily break the behaviour or check the assertion, then restore.
6. For a flaky test, find the non-determinism (time, order, shared state, network) and remove it; do not add retries.
7. If a test exposes a real defect, report it and route it as a bugfix rather than changing production code here.

## Files that may be modified

- Test files, fixtures, and test helpers only.
- Testing docs.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- New tests pass repeatedly and were shown to fail when behaviour is broken.
- `python3 .automation/uadr.py check` passes.

## Completion criteria

- Target behaviour covered by deterministic tests; production code unchanged.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Module doc testing section if how to test the module changed.
- Testing strategy if a new kind of test or fixture was introduced.

## Human approval

- Deleting or disabling existing tests; changing production code.
