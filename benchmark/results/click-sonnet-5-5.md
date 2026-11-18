# Benchmark results: click

Repository: https://github.com/pallets/click. Agent: `claude -p` (Claude Code headless), model `claude-sonnet-5-5`. 6 tasks x 5 conditions, 90 runs. Success is decided by hidden tests taken from the real upstream fix. Token and cost figures are the exact values reported by the API, summed over every model call in a run.


## Summary by condition

| Metric | bare | minimal | lean | uadr | uadr-v1.1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Runs | 18 | 18 | 18 | 18 | 18 |
| Resolved (hidden tests pass, no regressions) | 18/18 | 18/18 | 18/18 | 18/18 | 18/18 |
| Runs with regressions | 0 | 0 | 0 | 0 | 0 |
| Mean cost per run (USD) | 0.085 | 0.092 | 0.106 | 0.105 | 0.119 |
| Mean total input tokens (all calls) | 211,865 | 187,317 | 227,344 | 248,264 | 288,005 |
|   of which cache reads | 199,424 | 173,266 | 211,867 | 232,551 | 270,878 |
|   of which cache writes | 12,430 | 14,042 | 15,467 | 15,701 | 17,114 |
| Mean output tokens | 1,581 | 1,852 | 2,262 | 1,867 | 2,352 |
| Context at first model call (tokens) | 36,902 | 37,249 | 38,113 | 38,684 | 38,568 |
| Peak context (tokens) | 40,513 | 41,531 | 42,931 | 43,190 | 44,602 |
| Mean turns | 5.4 | 4.7 | 5.6 | 5.9 | 6.8 |
| Mean tool calls | 4.6 | 3.7 | 4.6 | 5.0 | 5.8 |
| Mean model (API) time (s) | 12 | 13 | 15 | 14 | 17 |
| Mean wall time (s), includes environment stalls | 20 | 21 | 29 | 25 | 28 |
| Ran tests itself | 94% | 100% | 100% | 100% | 100% |
| Added or changed tests | 0% | 100% | 100% | 44% | 100% |
| Updated changelog | 0% | 100% | 100% | 33% | 100% |
| Updated project docs | 0% | 0% | 6% | 0% | 0% |
| Source lines changed / reference fix | 0.96x | 1.05x | 1.37x | 1.12x | 1.04x |
| Touched files outside source, tests, docs, changelog | 0% | 0% | 0% | 0% | 0% |

Framework adherence in `lean`: read project state in 0% of runs, used the router in 0%, opened the workflow in 0%, opened a module doc in 0%, ran `uadr.py check` in 0%.

Framework adherence in `uadr`: read project state in 100% of runs, used the router in 44%, opened the workflow in 0%, opened a module doc in 0%, ran `uadr.py check` in 0%.

Framework adherence in `uadr-v1.1`: read project state in 100% of runs, used the router in 100%, opened the workflow in 0%, opened a module doc in 0%, ran `uadr.py check` in 22%.

## Per task (mean over repetitions)

| Task | Type | bare: resolved | minimal: resolved | lean: resolved | uadr: resolved | uadr-v1.1: resolved | bare: cost | minimal: cost | lean: cost | uadr: cost | uadr-v1.1: cost | bare: input tok | minimal: input tok | lean: input tok | uadr: input tok | uadr-v1.1: input tok |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| write-usage-empty-args | bugfix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.06 | $0.07 | $0.09 | $0.07 | $0.09 | 112,586 | 127,563 | 157,778 | 145,787 | 201,441 |
| choice-completion-normalize | bugfix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.07 | $0.09 | $0.10 | $0.10 | $0.12 | 153,230 | 239,128 | 269,696 | 233,460 | 296,370 |
| parameter-source-early | bugfix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.09 | $0.09 | $0.12 | $0.11 | $0.12 | 222,676 | 168,397 | 274,962 | 249,233 | 312,470 |
| progressbar-final-position | bugfix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.09 | $0.10 | $0.11 | $0.11 | $0.14 | 248,824 | 212,437 | 231,510 | 237,106 | 347,524 |
| show-envvar-sequence | bugfix | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.09 | $0.10 | $0.10 | $0.10 | $0.12 | 250,534 | 200,352 | 190,048 | 221,429 | 295,741 |
| runner-context-settings | feature | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.11 | $0.11 | $0.12 | $0.14 | $0.13 | 283,341 | 176,027 | 240,072 | 402,569 | 274,486 |

## Framework versus baselines (paired by task)

| Framework | Compared with | Cost | Total input tokens | Output tokens | Turns | Tasks where framework was cheaper |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| lean | bare | +27% | +16% | +57% | +10% | 0/6 |
| lean | minimal | +16% | +23% | +24% | +19% | 0/6 |
| uadr | bare | +24% | +20% | +20% | +13% | 0/6 |
| uadr | minimal | +13% | +35% | -2% | +29% | 0/6 |
| uadr | lean | -2% | +9% | -20% | +8% | 4/6 |
| uadr-v1.1 | bare | +42% | +45% | +58% | +33% | 0/6 |
| uadr-v1.1 | minimal | +30% | +56% | +27% | +45% | 0/6 |
| uadr-v1.1 | lean | +13% | +29% | +4% | +24% | 0/6 |
| uadr-v1.1 | uadr | +15% | +23% | +33% | +20% | 1/6 |

Values are the mean of per-task ratios (framework / baseline - 1). Positive means the framework used more.

## One-time onboarding cost

The framework condition requires onboarding the repository once. Measured for this repository with the same model: **$0.91**, 2,251,050 input tokens, 35,711 output tokens, 29 turns, 5 minutes. Existing project files modified: 0. `uadr.py check` exit code afterwards: 0.

`lean` against `bare`: costs $0.020 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`lean` against `minimal`: costs $0.014 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`uadr` against `bare`: costs $0.019 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`uadr` against `minimal`: costs $0.013 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`uadr-v1.1` against `bare`: costs $0.034 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.

`uadr-v1.1` against `minimal`: costs $0.027 more per task on average, so onboarding is not recovered through token savings on tasks of this kind.
