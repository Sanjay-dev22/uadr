---
name: documentation-generation
description: Write accurate project docs from source using the repository's templates. Use when creating or updating module, architecture, or API docs.
---
# Documentation generation

1. **Create from a template**: `python3 .automation/uadr.py new module <name> --paths <glob>`, `new adr "<title>"`, or `new doc <template>`. Templates are listed in `docs/templates/README.md`.
2. **Gather evidence first**: read the code, configuration, and tests for the subject. Every statement should trace to something you read or ran.
3. **Write for an agent with no context**: lead with purpose and entry points, give exact paths and commands, prefer tables and lists to narrative.
4. **Be specific and short**: name the file and symbol rather than describing them. Leave out anything obvious from the code or true of every module.
5. **Mark uncertainty**: `UNKNOWN: <question>` for gaps, `ASSUMPTION: <claim> (basis)` for inferences. Keep `status: draft` until none remain unverified.
6. **Do not duplicate**: link to the doc that owns a fact. Delete template sections that do not apply.
7. **Fill the frontmatter** `purpose` and `read_when` so the router and index can present the doc accurately.
8. **Finish**: run `python3 .automation/uadr.py index` and `python3 .automation/uadr.py check --only docs,links`.

Rules of record are in `.agent/policies/documentation.md`.
