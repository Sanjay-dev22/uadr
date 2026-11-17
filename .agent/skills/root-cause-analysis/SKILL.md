---
name: root-cause-analysis
description: Trace a defect or incident from symptom to underlying cause using evidence and hypothesis testing. Use for bug investigation, failing tests, and production issues.
---
# Root cause analysis

1. **State the failure**: expected, actual, and exact evidence (message, stack trace, input, time, version).
2. **Reproduce** with the smallest input. A failing automated test is the best reproduction. If it is intermittent, find what varies: timing, order, data, environment, concurrency.
3. **Localise**: follow the stack trace or data flow to the first point where state is wrong, not where the error surfaces. Use bisection on inputs, code paths, or commits (`git log`, `git bisect`) when the trail is unclear.
4. **Hypothesise** a cause that would produce exactly this evidence. Prefer the simplest; list alternatives.
5. **Test the hypothesis**: predict something not yet observed and check it. One confirmed prediction beats many consistent observations.
6. **Ask why again**: why was the faulty state possible? Missing validation, wrong assumption, unhandled case, race. Fix at that level.
7. **Check siblings**: search for the same mistake elsewhere.

Report symptom, cause, evidence, and why the fix addresses the cause. If the cause is unconfirmed, say so and name the evidence that would settle it. Do not present a guess as a finding.
