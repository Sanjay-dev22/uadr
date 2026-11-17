# Benchmark results: click

Repository: https://github.com/pallets/click. Agent: `claude -p` (Claude Code headless), model `claude-haiku-5-5`. 6 tasks x 3 conditions, 36 runs. Success is decided by hidden tests taken from the real upstream fix. Token and cost figures are the exact values reported by the API, summed over every model call in a run.


## Summary by condition

| Metric | bare | minimal | uadr-v1.1 |
| --- | ---: | ---: | ---: |
| Runs | 12 | 12 | 12 |
| Resolved (hidden tests pass, no regressions) | 12/12 | 12/12 | 12/12 |
| Runs with regressions | 0 | 0 | 0 |
| Mean cost per run (USD) | 0.014 | 0.013 | 0.023 |
| Mean total input tokens (all calls) | 589,429 | 501,731 | 976,399 |
|   of which cache reads | 566,269 | 478,507 | 940,953 |
|   of which cache writes | 23,135 | 23,202 | 35,410 |
| Mean output tokens | 7,695 | 6,571 | 12,531 |
| Context at first model call (tokens) | 37,734 | 38,087 | 39,408 |
| Peak context (tokens) | 51,486 | 51,336 | 63,544 |
| Mean turns | 13.6 | 11.8 | 19.8 |
| Mean tool calls | 12.6 | 10.8 | 18.8 |
| Mean wall time (s) | 72 | 41 | 91 |
| Ran tests itself | 100% | 100% | 100% |
| Added or changed tests | 83% | 100% | 100% |
| Updated changelog | 42% | 100% | 100% |
| Updated project docs | 0% | 0% | 0% |
| Source lines changed / reference fix | 2.25x | 2.20x | 2.28x |
| Touched files outside source, tests, docs, changelog | 0% | 0% | 0% |

Framework adherence in `uadr-v1.1`: read project state in 100% of runs, used the router in 100%, opened the workflow in 42%, opened a module doc in 75%, ran `uadr.py check` in 92%.

## Per task (mean over repetitions)

| Task | Type | bare: resolved | minimal: resolved | uadr-v1.1: resolved | bare: cost | minimal: cost | uadr-v1.1: cost | bare: input tok | minimal: input tok | uadr-v1.1: input tok |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| write-usage-empty-args | bugfix | 2/2 | 2/2 | 2/2 | $0.01 | $0.01 | $0.02 | 195,618 | 286,286 | 945,356 |
| choice-completion-normalize | bugfix | 2/2 | 2/2 | 2/2 | $0.01 | $0.01 | $0.02 | 493,846 | 467,942 | 755,632 |
| parameter-source-early | bugfix | 2/2 | 2/2 | 2/2 | $0.01 | $0.02 | $0.02 | 587,548 | 606,412 | 993,904 |
| progressbar-final-position | bugfix | 2/2 | 2/2 | 2/2 | $0.01 | $0.01 | $0.02 | 467,030 | 530,036 | 843,868 |
| show-envvar-sequence | bugfix | 2/2 | 2/2 | 2/2 | $0.02 | $0.01 | $0.02 | 751,884 | 561,784 | 1,078,444 |
| runner-context-settings | feature | 2/2 | 2/2 | 2/2 | $0.02 | $0.02 | $0.03 | 1,040,648 | 557,927 | 1,241,186 |

## Framework versus baselines (paired by task)

| Framework | Compared with | Cost | Total input tokens | Output tokens | Turns | Tasks where framework was cheaper |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| uadr-v1.1 | bare | +86% | +108% | +109% | +66% | 0/6 |
| uadr-v1.1 | minimal | +85% | +105% | +103% | +72% | 0/6 |

Values are the mean of per-task ratios (framework / baseline - 1). Positive means the framework used more.

## One-time onboarding cost

The framework condition requires onboarding the repository once. Measured for this repository with the same model: **$0.91**, 2,251,050 input tokens, 35,711 output tokens, 30 turns, 5 minutes. Existing project files modified: 0. `uadr.py check` exit code afterwards: 0.

`uadr-v1.1` against `bare`: costs $0.009 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`uadr-v1.1` against `minimal`: costs $0.010 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.
