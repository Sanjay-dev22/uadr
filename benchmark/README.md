# UADR benchmark

Measures what the framework actually does to an AI coding agent's cost and output, by running the same real tasks with and without it.

## Method

- **Tasks** are real upstream commits from an open-source repository, mined with `mine_tasks.py`. A commit qualifies when the tests it adds or changes fail on the parent commit and pass on the commit itself (the SWE-bench method). The agent gets the parent checkout, with no git history, and a problem statement. It never sees the upstream fix or its tests.
- **Success** is decided by those hidden tests plus the rest of the project's test suite: all fail-to-pass tests must pass and nothing that passed at the upstream fix may break.
- **Agent**: Claude Code headless (`claude -p`), default tools, same prompt in every condition: the problem statement and "resolve this in the repository in the current directory".
- **Conditions**:
  - `bare`: the repository as upstream has it, with no agent instructions.
  - `minimal`: a seven-line hand-written `AGENTS.md` (layout, test command, "every behaviour change needs a test and a changelog entry").
  - `uadr`, `uadr-v1.1`: the framework, adopted and then onboarded once by a headless agent at a commit older than every task, so its docs cannot leak a fix.
- **Measurements** are the exact token and cost figures the API reports, summed over every model call in a run, plus turns, tool calls, wall time, and change-quality signals taken from the transcript and the diff.

## Results

Repository: [pallets/click](https://github.com/pallets/click) (about 13,000 lines of Python in one package). Six tasks: five bug fixes and one feature, with reference fixes of 3 to 26 source lines. Full tables: [results/click-sonnet-5-5.md](results/click-sonnet-5-5.md), [results/click-haiku-5-5.md](results/click-haiku-5-5.md). Raw per-run records are the `.json` files beside them.

### Sonnet 5.5, 3 repetitions, 72 runs

| | bare | minimal | uadr 1.0 | uadr 1.1 |
| --- | ---: | ---: | ---: | ---: |
| Resolved | 18/18 | 18/18 | 18/18 | 18/18 |
| Mean cost per task | $0.085 | $0.092 | $0.105 | $0.119 |
| Mean input tokens, all calls | 211,865 | 187,317 | 248,264 | 288,005 |
| Mean output tokens | 1,581 | 1,852 | 1,867 | 2,352 |
| Mean turns | 5.6 | 4.7 | 6.0 | 6.8 |
| Mean wall time | 20 s | 21 s | 25 s | 28 s |
| Added a test | 0% | 100% | 44% | 100% |
| Updated the changelog | 0% | 100% | 33% | 100% |
| Context at first model call | 36,902 | 37,249 | 38,684 | 38,568 |

### Haiku 5.5, 2 repetitions, 36 runs

| | bare | minimal | uadr 1.1 |
| --- | ---: | ---: | ---: |
| Resolved | 12/12 | 12/12 | 12/12 |
| Mean cost per task | $0.014 | $0.013 | $0.023 |
| Mean input tokens, all calls | 589,429 | 501,731 | 976,399 |
| Mean turns | 13.6 | 11.8 | 19.8 |
| Added a test | 83% | 100% | 100% |
| Updated the changelog | 42% | 100% | 100% |

### One-time onboarding

Onboarding click with Sonnet 5.5 cost $0.91 and took 5 minutes: 30 turns, 12 module docs, an architecture overview, working commands. It modified no existing file and the gates passed afterwards.

## What the results say

1. **The framework did not reduce token use on these tasks. It increased it.** Against the bare repository, cost per task was 24% higher with version 1.0 and 42% higher with 1.1 on Sonnet, and 86% higher on Haiku. It was never cheaper on any of the six tasks. Because there is no per-task saving, the onboarding cost is not recovered.
2. **It did not improve correctness, and this benchmark could not have shown it if it did.** Every condition resolved every task, so the tasks are too easy to separate the conditions on success rate.
3. **A seven-line `AGENTS.md` matched the framework's measurable quality benefit at lower cost.** Without instructions, Sonnet never added a test or changelog entry. With the short file it always did. Framework 1.0 did so less than half the time, because its entry point delegated that rule to a workflow file the agent did not open.
4. **Agents follow only what is in the entry point.** With 1.0, Sonnet read the state file every time, used the router in 44% of runs, and never opened a workflow or module doc. Version 1.1 moved the done-criteria into `AGENTS.md` and made the router print the deliverables; router use and test and changelog rates all went to 100%, at a further 15% cost.
5. **The always-loaded overhead is larger than the framework's own estimate.** The first model call carried about 1,700 more tokens with the framework than without, not the roughly 550 estimated for `AGENTS.md` alone. The difference is mostly the twelve skill descriptions that skill-aware platforms preload. The audit command now counts them.
6. **A weaker model followed the framework more closely and paid more for it.** Haiku opened module docs in 75% of runs and ran the gates in 92%, which is where its extra turns went.

## What this benchmark does not show

- **Large or multi-module repositories.** Click is small enough that a single search finds the code. Routing and module docs are designed for repositories where that is not true; that case is untested here.
- **Harder or vaguer tasks.** These statements include a reproduction and the expected output. Tasks needing architectural understanding, or with unclear requirements, are untested.
- **Multi-session work, handover, governance, and safety behaviour.** Nothing here exercises memory, approvals, or secret handling.
- **Other agents and other languages.** One agent CLI, two models, one Python repository.
- **Statistical confidence.** Two or three repetitions per cell; per-task variation between repetitions is often larger than the differences between `bare` and `minimal`.

The environment also adds about 37,000 tokens of harness system prompt and tools to every call in every condition, which dilutes relative differences in input tokens.

One task statement was corrected during the benchmark. The first statement for `runner-context-settings` omitted a requirement that a hidden test checks, so every condition failed that one test. Those nine runs were discarded and rerun with the corrected statement.

## Reproduce

Requires the `claude` CLI, `git`, Python 3.9+, and whatever the target repository needs to run its tests (`uv` for click). Agent runs spend real API budget: this whole benchmark cost about $10 including discarded runs.

```bash
git clone --depth 400 https://github.com/pallets/click /tmp/click
python3 benchmark/run_benchmark.py onboard --suite benchmark/tasks/click.json --repo /tmp/click --work /tmp/bench
```

```bash
python3 benchmark/run_benchmark.py run --suite benchmark/tasks/click.json --repo /tmp/click --work /tmp/bench --conditions bare,minimal,uadr --reps 3 --jobs 4
```

```bash
python3 benchmark/report.py --work /tmp/bench --suite benchmark/tasks/click.json --out /tmp/bench/report
```

To benchmark another repository, mine candidate tasks with `mine_tasks.py`, write a problem statement for each chosen commit, and add a suite file under `tasks/`. Runs are resumable: existing result files are skipped.
