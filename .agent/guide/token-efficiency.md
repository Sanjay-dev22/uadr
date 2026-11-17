---
purpose: Explains how the framework keeps agent context small, with measured token costs and how to re-measure.
read_when: Human adopters evaluating cost; agents only when changing budgets or the routing design.
---
# Token efficiency

## Read this first: measured results

The figures further down are estimates of the documents an agent is routed to. Real agent runs tell a less favourable story, reported in full in `benchmark/README.md`:

- On six real bug-fix and feature tasks in a 13,000-line repository, the framework increased cost per task by 24% to 42% with Sonnet 5.5 and by 86% with Haiku 5.5, compared with the same repository without it.
- The always-loaded overhead, measured at the first model call, was about 1,700 tokens, not the roughly 550 of `AGENTS.md` alone. Platforms that support skills preload every skill's name and description.
- That overhead is paid again on every model call of a task, and routing adds turns. On tasks an agent can solve in five turns with a single search, these costs outweigh anything progressive loading saves.

Progressive loading limits how much documentation an agent reads. It does not make an agent cheaper than one that needs no documentation at all, and the benchmark has not yet tested repositories large enough for documentation to be necessary.

## Mechanism

An agent's context is built in tiers, each loaded only when the previous one points to it:

| Tier | What | Loaded | Cost (template, estimated) |
| --- | --- | --- | --- |
| 0 | `AGENTS.md`, plus skill names and descriptions on skill-aware platforms | Always, by the platform | ~570 + ~490 estimated; ~1,700 measured |
| 1 | `.agent/memory/state.md` and the router's output | Every task | ~100 to 250 tokens |
| 2 | One workflow | Every task | ~430 to 610 tokens (onboarding: ~890) |
| 3 | Module doc for the touched paths | Before changing code | ~300 to 800 tokens each, project dependent |
| 4 | Conditional docs, one skill at a time | Only when a stated condition holds | ~290 to 370 tokens per skill |
| 5 | Source code | Targeted search, then the files being edited | Task dependent |

Five things keep this small:

1. **The entry point routes instead of explaining.** `AGENTS.md` holds rules and pointers only. A gate fails the build if it exceeds its budget.
2. **The router returns a reading list, not documents.** `uadr.py route` prints roughly 150 tokens naming the workflow, the module doc, and conditional docs with their conditions, so the agent does not need to read the 2,500-token route table.
3. **Module docs are isolated.** `modules.json` maps a path to exactly one doc. Touching billing never loads the users doc.
4. **Conditions are explicit.** Architecture, API, database, and decision docs are listed under "read only if" with the condition, so the default is not to read them.
5. **Nothing is duplicated.** Platform adapters are pointers, the index is generated, and the `instructions` gate reports sentences repeated across instruction files.

## Estimated document cost

Estimated with `python3 .automation/uadr.py audit` at framework version 1.0.0. Estimates use four characters per token; real tokenizer counts typically differ by up to 15 percent.

| Measure | Template | Sample onboarded repository (two modules) |
| --- | --- | --- |
| Always loaded (`AGENTS.md`) | 543 | 561 |
| Start of task (`AGENTS.md` + state) | 642 | 683 |
| Typical bug fix before reading code | 1,150 | 1,489 |
| Typical feature before reading code | 1,249 | 1,588 |
| Worst-case bootstrap (largest workflow) | 1,535 | 1,576 |
| Entire framework and docs corpus | about 26,000 | about 27,000 |
| Share of corpus loaded per typical task | about 5% | about 6% |

The sample repository figures come from the walkthroughs in this folder. As a project grows, the corpus grows with the number of modules and docs, while the per-task cost stays roughly constant because only one module doc is loaded.

## Budgets

`context_budget` in `.automation/configuration/uadr.json` sets the limits. The `context` gate and `audit --check` enforce them in CI.

| Budget | Default | Applies to |
| --- | --- | --- |
| `entry_point_tokens` | 700 | `AGENTS.md` |
| `bootstrap_tokens` | 3,000 | `AGENTS.md` + state + largest workflow |
| `workflow_tokens` | 950 | Each workflow |
| `skill_tokens` | 700 | Each skill |
| `memory_file_tokens` | 900 | Each memory file |
| `adapter_lines` | 15 | Each platform pointer file |

## Keeping it efficient

- Keep module docs to what an agent needs to change the module safely. If a module doc passes roughly 1,000 tokens, the module is probably two modules.
- Put a fact in the most specific doc that owns it, and link from elsewhere.
- Prune memory: `state.md` keeps ten recent changes, and `handover.md` is cleared when work completes.
- Re-run `python3 .automation/uadr.py audit` after adding workflows, skills, or large docs.
