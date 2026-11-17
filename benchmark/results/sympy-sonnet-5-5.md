# Benchmark results: sympy

Repository: https://github.com/sympy/sympy. Agent: `claude -p` (Claude Code headless), model `claude-sonnet-5-5`. 8 tasks x 3 conditions, 48 runs. Success is decided by hidden tests taken from the real upstream fix. Token and cost figures are the exact values reported by the API, summed over every model call in a run.


## Summary by condition

| Metric | bare | minimal | uadr |
| --- | ---: | ---: | ---: |
| Runs | 16 | 16 | 16 |
| Resolved (hidden tests pass, no regressions) | 16/16 | 16/16 | 16/16 |
| Runs with regressions | 0 | 0 | 0 |
| Mean cost per run (USD) | 0.138 | 0.176 | 0.170 |
| Mean total input tokens (all calls) | 350,672 | 451,806 | 460,225 |
|   of which cache reads | 333,984 | 432,360 | 439,616 |
|   of which cache writes | 16,671 | 19,425 | 20,588 |
| Mean output tokens | 3,774 | 5,461 | 4,335 |
| Context at first model call (tokens) | 37,001 | 37,380 | 38,750 |
| Peak context (tokens) | 44,522 | 46,914 | 48,078 |
| Mean turns | 8.2 | 9.9 | 10.2 |
| Mean tool calls | 7.2 | 8.9 | 8.6 |
| Mean model (API) time (s) | 29 | 40 | 33 |
| Mean wall time (s), includes environment stalls | 95 | 82 | 494 |
| Ran tests itself | 100% | 100% | 100% |
| Added or changed tests | 19% | 100% | 100% |
| Updated changelog | 0% | 0% | 0% |
| Updated project docs | 0% | 0% | 0% |
| Source lines changed / reference fix | 1.10x | 1.24x | 1.27x |
| Touched files outside source, tests, docs, changelog | 0% | 0% | 0% |

Framework adherence in `uadr`: read project state in 100% of runs, used the router in 94%, opened the workflow in 0%, opened a module doc in 0%, ran `uadr.py check` in 0%.

## Per task (mean over repetitions)

| Task | Type | bare: resolved | minimal: resolved | uadr: resolved | bare: cost | minimal: cost | uadr: cost | bare: input tok | minimal: input tok | uadr: input tok |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| quaternion-180-rotation | bugfix | 2/2 | 2/2 | 2/2 | $0.08 | $0.11 | $0.12 | 115,404 | 220,808 | 274,829 |
| subs-derivative-free-symbols | bugfix | 2/2 | 2/2 | 2/2 | $0.22 | $0.51 | $0.31 | 517,705 | 1,430,363 | 905,214 |
| str-duplicate-parentheses | bugfix | 2/2 | 2/2 | 2/2 | $0.25 | $0.17 | $0.19 | 749,092 | 402,280 | 508,555 |
| mod-negative-ratio | bugfix | 2/2 | 2/2 | 2/2 | $0.10 | $0.09 | $0.12 | 254,968 | 193,104 | 330,144 |
| convolution-empty-input | bugfix | 2/2 | 2/2 | 2/2 | $0.09 | $0.13 | $0.13 | 197,653 | 370,828 | 320,631 |
| interval-times-infinity | bugfix | 2/2 | 2/2 | 2/2 | $0.17 | $0.17 | $0.20 | 552,074 | 449,270 | 606,581 |
| reshape-validation | bugfix | 2/2 | 2/2 | 2/2 | $0.09 | $0.12 | $0.16 | 176,465 | 264,839 | 417,786 |
| solve-no-symbols | bugfix | 2/2 | 2/2 | 2/2 | $0.11 | $0.11 | $0.13 | 242,018 | 282,952 | 318,061 |

## Framework versus baselines (paired by task)

| Framework | Compared with | Cost | Total input tokens | Output tokens | Turns | Tasks where framework was cheaper |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| uadr | bare | +31% | +56% | +28% | +45% | 1/8 |
| uadr | minimal | +11% | +22% | -1% | +16% | 2/8 |

Values are the mean of per-task ratios (framework / baseline - 1). Positive means the framework used more.

## One-time onboarding cost

The framework condition requires onboarding the repository once. Measured for this repository with the same model: **$5.09**, 17,647,134 input tokens, 185,099 output tokens, 219 turns, 17 minutes. Existing project files modified: 0. `uadr.py check` exit code afterwards: 0.

`uadr` against `bare`: costs $0.032 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`uadr` against `minimal`: saves $0.006 per task on average, so onboarding pays for itself after about 865 tasks.
