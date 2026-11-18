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

### Large repository: SymPy, Sonnet 5.5, 2 repetitions, 48 runs

[sympy/sympy](https://github.com/sympy/sympy): about 530,000 lines across dozens of subpackages. Eight bug fixes, one from each of eight subpackages. SymPy's own `AGENTS.md` was removed in every condition so all start from the same code. Scoring runs the changed test files of the real fix. Full table: [results/sympy-sonnet-5-5.md](results/sympy-sonnet-5-5.md).

| | bare | minimal | uadr 1.1 |
| --- | ---: | ---: | ---: |
| Resolved | 16/16 | 16/16 | 16/16 |
| Mean cost per task | $0.138 | $0.176 | $0.170 |
| Mean input tokens, all calls | 350,672 | 451,806 | 460,225 |
| Mean turns | 8.2 | 9.9 | 10.2 |
| Mean model time | 29 s | 40 s | 33 s |
| Added a test | 19% | 100% | 100% |
| Opened a module doc | n/a | n/a | 0% |

Paired by task, the framework cost 31% more than bare (more expensive on 7 of 8 tasks) and 11% more than the short note (more expensive on 6 of 8). Onboarding SymPy cost $5.09 and took 17 minutes (219 turns, 43 module docs, no existing file modified). Against the short note the framework saves about $0.006 per task, so onboarding would take around 865 tasks to repay; against bare it costs more per task and never repays.

### One-time onboarding (click)

Onboarding click with Sonnet 5.5 cost $0.91 and took 5 minutes: 30 turns, 12 module docs, an architecture overview, working commands. It modified no existing file and the gates passed afterwards.

## What the results say

1. **The framework did not reduce token use or cost on either repository.** On click it cost 24% to 86% more than bare. On SymPy, a repository about 40 times larger, it cost 31% more than bare and 11% more than a short hand-written note. It was cheaper than bare on 1 of 8 SymPy tasks.
2. **It did not improve correctness, and these tasks could not have shown it.** All 108 click runs and all 48 SymPy runs resolved their task in every condition.
3. **A seven-line `AGENTS.md` matched the framework's measurable discipline at equal or lower cost.** Without instructions, agents rarely added tests (0% on click, 19% on SymPy). With the short file, or the framework, they always did.
4. **Agents follow only what is in the entry point.** In every framework condition they read the state file and ran the router (94% to 100%), but no run ever opened a workflow file or a module doc, on either repository, even though the router named the correct module doc each time (for example `docs/modules/algebras.md` for a quaternion fix). They went straight to searching the source. The 43 module docs written for SymPy, which cost $5.09 to produce, were never read.
5. **The always-loaded overhead is about 1,700 tokens**, measured at the first model call, larger than the estimate for `AGENTS.md` alone, because skill-aware platforms preload every skill description.
6. **A weaker model followed the framework more closely and paid more for it.** Haiku opened module docs in 75% of runs and ran the gates in 92%, which is where its extra turns went.

## What this benchmark does not show

- **Whether module docs help an agent that does not already know where to look.** Every task statement names the function or class involved (`Quaternion.from_rotation_matrix`, `solve`, `reshape`), so a single search finds the code even in a 530,000-line repository. The situation module docs are designed for, a vague request where the agent must first work out which subpackage is involved, is untested. A fair test would use issue-style descriptions that name only symptoms.
- **Multi-session work, handover, governance, and safety behaviour.** Nothing here exercises memory, approvals, or secret handling.
- **Other agents, languages, and frameworks.** One agent CLI, two models, two Python repositories.
- **Statistical confidence.** Two or three repetitions per cell; per-task variation between repetitions is often larger than the difference between `bare` and `minimal`.

The environment also adds about 37,000 tokens of harness system prompt and tools to every call in every condition, which dilutes relative differences in input tokens.

Two measurement problems were found and fixed during the benchmark. Runs interrupted by a usage limit looked like failures with zero tokens; 26 SymPy runs and one onboarding were discarded and rerun, and the harness now refuses to record unfinished runs. Separately, in 10 of the 16 SymPy framework runs the agent's top-level `usage` field covered only part of the run (reporting about 198,000 input tokens when the true figure was 460,000), so token and turn figures are now taken from `modelUsage` and the transcript. Click figures were checked and agree under both methods. Those same 10 runs also show about 12 minutes of wall time against 16 to 62 seconds of model time, an environment stall, so wall time is reported only alongside model time.

One click task statement was corrected during the benchmark. The first statement for `runner-context-settings` omitted a requirement that a hidden test checks, so every condition failed that one test. Those nine runs were discarded and rerun with the corrected statement.

## Reproduce

Requires the `claude` CLI, `git`, Python 3.9+, and whatever the target repository needs to run its tests (`uv` for click). Agent runs spend real API budget: the click and SymPy benchmarks together cost about $22 including discarded runs and onboarding.

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
