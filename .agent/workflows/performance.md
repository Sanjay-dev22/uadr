---
purpose: Procedure for measuring and improving performance.
read_when: The router selects the performance route.
---
# Workflow: performance

## Objective

Improve a measured performance problem and prove the improvement, without changing correctness.

## Required context

- The symptom, the metric, the target, and a workload that reproduces the problem.

## Documents to read

- Output of `uadr.py route performance --path <paths>`; nothing else up front.
- The module doc for the slow path.

## Steps

1. Define the metric and target. If none exists, propose one and confirm.
2. Build a repeatable measurement and record the baseline (skill: `performance-analysis`).
3. Profile to find where the time or memory goes. Do not optimise from intuition.
4. Form a hypothesis for the dominant cost and choose the simplest change that removes it.
5. Make one change at a time and re-measure under the same conditions.
6. Keep changes that move the metric meaningfully; revert the rest.
7. Confirm correctness with the full test suite; add a regression guard if the project has performance tests.
8. Report baseline, result, method, and environment.

## Files that may be modified

- Code on the measured hot path and its tests.
- Benchmarks or performance tests.

## Validation

- Before and after measurements taken with the same method and stated.
- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.

## Completion criteria

- Target met, or best result reported with the remaining bottleneck identified.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Module doc for new caches, limits, or tuning configuration.
- `.agent/memory/known-issues.md` for bottlenecks left in place.

## Human approval

- Adding caches or infrastructure; relaxing consistency or correctness guarantees.
