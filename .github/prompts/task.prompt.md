---
description: Run any development task through the UADR router and its workflow
---
Task: ${input:task:Describe the task}

Follow `AGENTS.md`. Run `python3 .automation/uadr.py route "<the task>" --path <files you expect to touch>`, read only what it lists, execute the named workflow in `.agent/workflows/`, and finish with the completion report from `.agent/policies/quality.md`.
