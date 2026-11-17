---
purpose: Procedure for building a capability that does not exist yet.
read_when: The router selects the feature route.
---
# Workflow: feature

## Objective

Deliver a new capability that meets stated acceptance criteria, fits the existing architecture, and is tested and documented.

## Required context

- The requirement and its acceptance criteria. If criteria are missing, write them and confirm before implementing.
- The module(s) that will own the behaviour.

## Documents to read

- Output of `uadr.py route feature --path <paths>`; nothing else up front.
- The module doc for each module you will change.
- The architecture overview only if more than one module is involved.

## Steps

1. Restate the requirement as testable acceptance criteria.
2. Locate the owning module and the closest existing feature; use it as the pattern (skill: `codebase-navigation`).
3. Trace how that feature flows through entry point, logic, data, and tests. Note conventions to follow.
4. Write a plan: files to add or change, data and interface changes, tests, risks, approvals needed (`.agent/templates/plan.template.md`).
5. Request any approval the plan needs before writing code.
6. Implement in small steps, following the existing pattern (skill: `feature-implementation`).
7. Add tests at the level the module already uses; cover the criteria, edge cases, and failure paths (skill: `test-generation`).
8. Run validation, review your own diff, update docs, and report.

## Files that may be modified

- Source and tests in the owning module(s).
- Wiring and configuration needed to expose the feature.
- Docs listed below. Nothing else without stating why.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- Each acceptance criterion is demonstrated by a test or a recorded manual check.

## Completion criteria

- All criteria met and validated.
- No unrelated changes in the diff.
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- Module doc: new entry points, models, rules, configuration.
- `docs/api/` or `docs/database/` if contracts or schema changed.
- `CHANGELOG.md` for user-visible behaviour.
- `.agent/memory/state.md` if this changes what the project can do.

## Human approval

- New dependency, new module, public contract change, schema change: before implementation.
