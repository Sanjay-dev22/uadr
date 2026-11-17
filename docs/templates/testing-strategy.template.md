---
target: docs/testing/testing-strategy.md
purpose: Test levels, conventions, test data, and execution commands for {{PROJECT_NAME}}.
read_when: Deciding what kind of test to write, where to put it, or how to run a subset.
status: draft
---
# Testing strategy

<!-- Fill from verified sources. Delete sections that do not apply. Mark gaps `UNKNOWN:` and inferences `ASSUMPTION:`. Remove this comment when done. -->

## Levels

| Level | Covers | Location | Framework | Runs in CI |
| --- | --- | --- | --- | --- |
| Unit | | | | |
| Integration | | | | |
| End-to-end | | | | |

## Commands

| Goal | Command |
| --- | --- |
| All tests | `python3 .automation/uadr.py run test` |
| One file or test | |
| With coverage | |

## Conventions

<!-- Naming, structure, fixtures and factories, mocking policy. -->

## Test data

<!-- How data is created and cleaned up. Synthetic data only. -->

## Expectations

<!-- What must be tested for a change to be accepted; coverage thresholds if enforced. -->
