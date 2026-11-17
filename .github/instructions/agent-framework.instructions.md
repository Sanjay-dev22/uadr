---
applyTo: ".agent/**,.automation/**,AGENTS.md"
---
These files are the agent operating framework. Changing rules, policies, or approval gates needs human approval (`.agent/policies/approvals.md`). Keep `AGENTS.md` within its token budget, keep one fact in one place, and run `python3 .automation/uadr.py check` and `python3 .automation/uadr.py audit --check` after any edit.
