---
name: test-generation
description: Write automated tests that prove behaviour and fail when it breaks, in the project's existing style. Use when adding tests for new code, reproducing a bug, or closing a coverage gap.
---
# Test generation

1. **Learn the local style** from two or three existing tests near the code: framework, file location and naming, fixtures, factories, mocking approach.
2. **List the cases before writing**: the main path, each boundary (empty, zero, one, maximum, null), each invalid input, each failure of a dependency, and any state or ordering rules.
3. **Choose the lowest level** that proves the behaviour. Unit for logic, integration for wiring and data access, end-to-end only for critical journeys.
4. **One behaviour per test**, named for the behaviour and expected outcome. Arrange, act, assert.
5. **Assert outcomes**, not internal calls. Mock only what is slow, non-deterministic, or external.
6. **Make tests deterministic**: control time, randomness, order, and shared state; no reliance on network or on other tests.
7. **Prove the test can fail**: for a bug, run it against the unfixed code; otherwise break the behaviour briefly and confirm the failure, then restore.
8. **Test data** is synthetic and minimal; never real personal data or secrets.

Run with `python3 .automation/uadr.py run test` and report the actual result.
