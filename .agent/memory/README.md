---
purpose: Rules for the project memory files, agent handover, and knowledge maintenance.
read_when: Before writing to any file in this directory, or when handing work to another session.
---
# Project memory

Memory is a small set of Git-tracked files holding durable knowledge that is not derivable from code or docs. It is not a log of conversations.

| File | Holds | Update when |
| --- | --- | --- |
| `state.md` | Current project state, active tasks, recent significant changes | A task starts, completes, or changes the project's state |
| `handover.md` | Notes for the next session on unfinished work | You stop with work in progress; cleared when that work completes |
| `known-issues.md` | Technical limitations and outstanding technical debt | You discover or resolve one |

Architectural decisions are not memory: they are ADRs in `docs/decisions/`.

## Rules

- Write only what a future agent needs and cannot cheaply rediscover. No transcripts, no step-by-step history, no restating docs.
- Edit in place and replace stale entries. Each file must stay under the `memory_file_tokens` budget in `.automation/configuration/uadr.json`; the check enforces it.
- `state.md` keeps at most ten recent changes; older entries are deleted because git and the changelog hold the history.
- Skip the update when nothing durable changed. Most small fixes change no memory.
- Never store secrets, personal data, or credentials here.

## Handover

When stopping mid-task, replace the contents of `handover.md` using `../templates/handover.template.md`: goal, state of the work, what is verified, the next concrete step, and open questions. When resuming, read it, verify its claims against the working tree, and clear it once the work is complete.
