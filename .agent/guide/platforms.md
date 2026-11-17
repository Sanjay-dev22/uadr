---
purpose: How each supported coding agent and IDE discovers the framework, and how to add another.
read_when: Human adopters configuring an agent platform; agents only when adding or fixing an adapter.
---
# Agent platform compatibility

All platforms end up at `AGENTS.md`. Platform-specific files exist only where a platform needs a different filename or folder, and they contain pointers, not rules.

| Platform | Instructions it loads | Skills it discovers | Extra configuration shipped |
| --- | --- | --- | --- |
| Claude Code | `CLAUDE.md`, which imports `AGENTS.md` | `.claude/skills/` (link to `.agent/skills/`) | `.claude/settings.json`: allows the UADR CLI, asks before push or history rewrite, denies reading secret files |
| GitHub Copilot (VS Code, coding agent, CLI) | `.github/copilot-instructions.md` (pointer) and `AGENTS.md`; path-scoped `.github/instructions/*.instructions.md` | `.agents/skills/` or `.claude/skills/` | `.github/prompts/*.prompt.md` for task, onboarding, and review |
| OpenAI Codex | `AGENTS.md` | `.agents/skills/` (link to `.agent/skills/`) | None needed |
| Cursor, Windsurf, Gemini CLI, Aider, others | `AGENTS.md` where supported natively | Platform dependent | Add a pointer file if the tool requires its own filename |

Platform conventions change. Confirm the filenames against your tool's current documentation; the framework only relies on the tool reading one Markdown file at the repository root.

## Adding a platform

1. Create the file the tool reads, containing one or two sentences that point to `AGENTS.md`.
2. Add its path to `adapters.instruction_files` in `.automation/configuration/uadr.json`. The `instructions` gate then keeps it thin.
3. If the tool scans its own skills folder, add that folder to `adapters.skill_links` and run `python3 .automation/uadr.py sync-adapters`.

## Skills links on Windows

The skill folders are relative symlinks. If symlinks are unavailable, run `python3 .automation/uadr.py sync-adapters --copy` after every change to `.agent/skills/`. The `structure` gate fails when a copy is stale.

## Agents without shell access

Everything the CLI does for routing is readable data. An agent that cannot run commands reads `.agent/routing/routes.json` for its task type and `.agent/routing/modules.json` for the module doc, then proceeds the same way. Validation must then be run by CI or a human, and the agent reports it as not run.

## Sub-agents and parallel work

Pass a sub-agent the route name, the paths, and the acceptance criteria. It loads its own minimal context through the same entry point, which keeps each context small.
