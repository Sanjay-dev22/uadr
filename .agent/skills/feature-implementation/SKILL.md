---
name: feature-implementation
description: Implement new behaviour so it matches the conventions and structure of the surrounding code. Use when writing production code for a feature, enhancement, or API.
---
# Feature implementation

1. **Copy the local pattern.** Find the closest existing feature and mirror its layering, naming, error handling, logging, and configuration. Consistency with the module outranks personal preference.
2. **Work outside in**: contract or interface first, then validation, then logic, then persistence and integration.
3. **Smallest change that works.** No speculative options, abstractions, or unrelated cleanup. Reuse existing helpers before writing new ones.
4. **Handle failure deliberately**: invalid input, missing data, dependency failure, partial completion. Follow the module's existing error strategy.
5. **Configuration and secrets** go through the existing configuration mechanism with safe defaults; never hard-code environment-specific values.
6. **Keep it testable**: pass dependencies in, avoid hidden global state, isolate I/O at the edges.
7. **Build in increments** that compile and pass tests; run the relevant tests after each.
8. **Self-review the diff**: remove debug output, dead code, and accidental changes; confirm every changed line serves the task.

If the existing pattern is clearly harmful, follow it anyway for this change and record the concern as technical debt rather than introducing a second pattern.
