# Contributing

This repository is developed agent-first. Humans and AI agents follow the same process.

1. **Start at [AGENTS.md](AGENTS.md).** It is the single entry point and routes to everything else.
2. **Describe work as a task** with a type and acceptance criteria (use the issue templates).
3. **Route it:** `python3 .automation/uadr.py route "<task>" --path <files>` names the workflow and the documents to read.
4. **Validate before opening a pull request:**

   ```bash
   python3 .automation/uadr.py run all
   python3 .automation/uadr.py check
   ```

5. **Open a pull request** using the template. Report only checks that were actually run.

Humans own approvals: see [.agent/policies/approvals.md](.agent/policies/approvals.md) for the actions an agent must not take alone. To change the framework itself, read [.agent/guide/architecture.md](.agent/guide/architecture.md) first.
