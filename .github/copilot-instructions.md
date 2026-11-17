# Copilot instructions

The canonical agent instructions for this repository are in `AGENTS.md` at the repository root. Read it first and follow it exactly; this file adds no rules of its own.

In short: route every task with `python3 .automation/uadr.py route "<task>" --path <file>`, read only what the route lists, validate with `python3 .automation/uadr.py run all` and `python3 .automation/uadr.py check`, and stop for human approval where `.agent/policies/approvals.md` requires it.
