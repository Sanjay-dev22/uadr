---
target: docs/architecture/data-flow-and-integrations.md
purpose: How data moves through {{PROJECT_NAME}} and how it integrates with external systems.
read_when: A change affects data crossing module or system boundaries, an external integration, or a trust boundary.
status: draft
---
# Data flow and integrations

<!-- Fill from verified sources. Delete sections that do not apply. Mark gaps `UNKNOWN:` and inferences `ASSUMPTION:`. Remove this comment when done. -->

## Key flows

<!-- One subsection per important flow. Name the entry point and each hop with its path. -->

### Flow: <name>

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Application
    participant D as Data store
    C->>A: request
    A->>D: read or write
    A-->>C: response
```

## External integrations

| System | Direction | Protocol | Purpose | Code location | Failure behaviour |
| --- | --- | --- | --- | --- | --- |

## Trust boundaries

<!-- Where untrusted data enters and where authorisation is enforced. -->

## Data ownership

| Data | Owning module | Other readers |
| --- | --- | --- |
