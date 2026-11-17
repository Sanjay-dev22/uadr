---
target: docs/architecture/overview.md
purpose: System architecture of {{PROJECT_NAME}}: components, technology stack, patterns, and constraints.
read_when: A change spans modules, alters a boundary or pattern, or you must locate a responsibility that no module doc claims.
status: draft
---
# Architecture overview

<!-- Fill from verified sources. Delete sections that do not apply. Mark gaps `UNKNOWN:` and inferences `ASSUMPTION:`. Remove this comment when done. -->

## System context

<!-- What the system is, its users, and the external systems it talks to. -->

## Components

| Component | Responsibility | Location | Module doc |
| --- | --- | --- | --- |

## Diagram

```mermaid
flowchart LR
    user([User]) --> app[Application]
    app --> db[(Data store)]
```

## Technology stack

| Concern | Technology | Version | Notes |
| --- | --- | --- | --- |
| Language and runtime | | | |
| Framework | | | |
| Data store | | | |
| Build and packaging | | | |
| Test | | | |
| Hosting | | | |

## Design patterns and conventions

<!-- Only patterns the code consistently follows: layering, dependency direction, error handling, configuration. -->

## Architectural constraints

<!-- Rules a change must not break, each with its reason or ADR. -->

## Cross-cutting concerns

| Concern | Where implemented |
| --- | --- |
| Authentication and authorisation | |
| Configuration | |
| Logging and error handling | |
