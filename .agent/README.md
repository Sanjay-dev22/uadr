---
purpose: Map of the agent operating framework and onboarding for an agent new to this repository.
read_when: First session in this repository, or when you cannot find where a framework rule lives.
---
# Agent framework map

`AGENTS.md` is the entry point. Everything here is loaded on demand.

| Path | Holds | Load when |
| --- | --- | --- |
| `routing/routes.json` | Task type to workflow, required docs, skills, approval gate | Every task, through `uadr.py route` |
| `routing/modules.json` | Source path to module doc registry | Through `uadr.py route --path` |
| `workflows/` | One procedure per task type | The one your route names |
| `skills/` | Reusable techniques in Agent Skills format | A workflow step names it |
| `policies/` | Approvals, security, quality, context loading, documentation rules | A rule in `AGENTS.md` points to it |
| `memory/` | Durable project state, handover, known issues | `state.md` every task; others when routed |
| `templates/` | Plan, completion report, handover, migration report skeletons | Producing that artifact |
| `guide/` | Human-facing framework documentation | Changing the framework itself |
| `onboarding/` | Inventory and migration report (existing-repo adoption only) | During onboarding |

Project knowledge lives in `docs/` (what the system is). This directory holds how agents work. Automation lives in `.automation/`.

## Lifecycle

Every workflow follows the same eight stages:

1. **Understand** the requirement and restate the acceptance criteria.
2. **Plan**: identify modules, load routed context, write a short plan (`templates/plan.template.md` for multi-file work).
3. **Analyze** the existing implementation, callers, tests, risks, and dependencies.
4. **Implement** the smallest change that satisfies the criteria.
5. **Test** with the project commands; add tests for new behaviour.
6. **Review** your own diff against `policies/quality.md` and `policies/security.md`.
7. **Document** per `policies/documentation.md`.
8. **Complete** with the completion report, and update memory if durable facts changed.

## First session checklist

1. Read `AGENTS.md`, then `memory/state.md` and `memory/handover.md`.
2. Run `python3 .automation/uadr.py route --list` to see the task types.
3. Run `python3 .automation/uadr.py run all` to learn which project commands are configured.
4. Start the task through the router. Do not pre-read `docs/`.
