---
name: performance-analysis
description: Measure, profile, and improve performance using evidence rather than intuition. Use when investigating slowness, high resource use, or validating an optimisation.
---
# Performance analysis

1. **Define the metric** (latency percentile, throughput, memory, query count) and the workload that represents the problem.
2. **Measure a baseline** several times under stable conditions; record environment, data size, and variance.
3. **Profile** with the stack's profiler, tracing, or timing around suspected stages. Find where the time or memory actually goes.
4. **Look for the usual causes first**: repeated queries in loops, missing indexes, unbounded result sets, repeated computation, synchronous I/O in hot paths, excessive allocation or copying, lock contention, chatty remote calls.
5. **Estimate the gain** before changing code: removing a stage that is 5% of the time cannot yield more than 5%.
6. **Change one thing**, re-measure the same way, and compare against variance. Keep only real improvements.
7. **Check the cost**: complexity, memory, staleness, consistency. A cache needs an invalidation rule and a size bound.
8. **Protect correctness** with the full test suite, and add a benchmark or budget test if the project supports it.

Report baseline, result, method, environment, and remaining bottleneck. Never report an improvement you did not measure.
