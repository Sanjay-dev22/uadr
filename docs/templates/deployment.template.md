---
target: docs/operations/deployment.md
purpose: How {{PROJECT_NAME}} is deployed, configured per environment, and rolled back.
read_when: A change affects deployment, environment configuration, or release ordering; or during an incident.
status: draft
---
# Deployment

<!-- Fill from verified sources. Delete sections that do not apply. Mark gaps `UNKNOWN:` and inferences `ASSUMPTION:`. Remove this comment when done. -->

Agents never deploy or roll back outside a local environment without approval (`.agent/policies/approvals.md`).

## Environments

| Environment | Purpose | How deployed | Approval |
| --- | --- | --- | --- |

## Pipeline

<!-- Pipeline definition path, stages, and what triggers each. -->

## Environment configuration

| Setting | Source | Differs per environment |
| --- | --- | --- |

## Release procedure

1. <!-- steps -->

## Rollback procedure

1. <!-- steps, including data and migration considerations -->
