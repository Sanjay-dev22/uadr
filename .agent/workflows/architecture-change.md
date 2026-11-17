---
purpose: Procedure for changing boundaries, patterns, technology, or topology.
read_when: The router selects the architecture-change route.
---
# Workflow: architecture-change

## Objective

Change the architecture deliberately: decision recorded and approved first, implementation second.

## Required context

- The driver for the change (requirement, constraint, or pain) and the parts of the system affected.

## Documents to read

- Output of `uadr.py route architecture-change --path <paths>`; nothing else up front.
- Architecture overview and the decision index.
- Module docs for every affected module.

## Steps

1. State the problem and the forces behind it; confirm the current architecture from code, not only docs (skill: `architecture-discovery`).
2. Map everything affected: modules, data, interfaces, deployment, operations (skill: `dependency-analysis`).
3. Develop at least two options including doing nothing; compare cost, risk, migration path, and reversibility.
4. Draft an ADR with status `proposed`: `python3 .automation/uadr.py new adr "<title>"`.
5. Stop. Obtain human approval of the ADR.
6. After approval, plan an incremental migration where each step leaves the system working.
7. Implement step by step with validation after each; route sub-tasks through their own workflows.
8. Update architecture docs and set the ADR status to `accepted`.

## Files that may be modified

- Before approval: the ADR only.
- After approval: what the accepted ADR covers.

## Validation

- `python3 .automation/uadr.py run all`: every configured command passes.
- `python3 .automation/uadr.py check` passes.
- Each migration step validated before the next begins.

## Completion criteria

- ADR accepted and implemented, or ADR proposed and awaiting decision (report which).
- Completion report delivered in the `.agent/policies/quality.md` format.

## Documentation updates

- ADR in `docs/decisions/`.
- `docs/architecture/` and affected module docs.
- `.agent/routing/modules.json` for new or changed modules.
- `.agent/memory/state.md`.

## Human approval

- Always. No implementation before the ADR is accepted by a human.
