---
purpose: Rules for how much context to load, in what order, and what to leave unread.
read_when: You are unsure whether to read a document, or context is growing large.
---
# Context loading policy

Context is a budget. Load in tiers and stop as soon as you can act safely.

| Tier | Content | When |
| --- | --- | --- |
| 0 | `AGENTS.md` | Always (loaded by the agent platform) |
| 1 | `.agent/memory/state.md`, router output | Start of every task |
| 2 | The one workflow named by the route | After routing |
| 3 | Module doc(s) for the paths you will touch, other `read` docs | Before changing code |
| 4 | `consider` docs, skills, ADRs, other modules' docs | Only when their stated condition is true |
| 5 | Source code | Targeted: search first, then read the relevant files and their direct callers |

## Rules

- Never read a directory of docs end to end. Use `docs/index.md` or the router to pick single files.
- Prefer search (symbol, string, path) over reading whole files; read whole files only when you will edit them.
- Read one module doc per module you touch. Another module's doc is needed only if you call into or change its public surface.
- A missing doc is not a blocker: derive what you need from code, and write the doc only if the task's documentation rules require it.
- Do not reload a document already in context this session unless it changed.
- When delegating to a sub-agent, pass the route name, the paths, and the acceptance criteria rather than your whole context.
- Check the cost of the framework context with `python3 .automation/uadr.py audit`.
