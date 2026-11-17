---
purpose: Procedure for schema, migration, and stored-data changes.
read_when: The router selects the database route.
---
# Workflow: database

## Objective

Change the schema safely with a reversible, tested migration that never endangers existing data.

## Required context

- The data change needed, data volume, and which code and systems read or write the affected structures.

## Documents to read

- Output of `uadr.py route database --path <paths>`; nothing else up front.
- Database schema doc and affected module docs.
- Deployment doc if ordering or downtime matters.

## Steps

1. Describe the target schema and why it is needed.
2. Find every reader and writer of the affected structures, including other services and reports (skill: `dependency-analysis`).
3. Design a backward-compatible sequence: expand, migrate, contract. Avoid a single breaking step.
4. Write the migration with the project's migration tool, including the rollback.
5. Classify each statement as destructive or not (drop, truncate, bulk update, type narrowing are destructive).
6. Run migration and rollback on a local or disposable database only; test with representative data.
7. Update code and tests to the new schema.
8. Run validation, update docs, and hand the migration to a human for any shared environment.

## Files that may be modified

- Migration files, data-access code, and tests.
- Database docs.

## Validation

- Migration applies and rolls back cleanly on a disposable database.
- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.

## Completion criteria

- Migration and rollback tested locally; approval requested for shared environments; destructive steps called out.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- `docs/database/`.
- Module docs whose data models changed.
- `docs/operations/` if deploy steps changed.

## Human approval

- Always before running against shared or production data.
- Always for destructive statements, with backup and rollback stated.
