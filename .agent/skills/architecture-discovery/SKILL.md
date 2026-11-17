---
name: architecture-discovery
description: Derive the real architecture of a system from its source - components, boundaries, dependencies, data flow, integrations. Use when writing or verifying architecture docs, or before an architecture change.
---
# Architecture discovery

Derive from code and configuration; use existing docs only as hypotheses to confirm.

1. **Deployable units**: from build, container, and pipeline files, list what runs as a separate process or artefact.
2. **Components**: within each unit, find boundaries the code enforces (packages, projects, namespaces, services, directories with their own manifest). Do not impose layers that are not there.
3. **Dependencies**: for each component, find what it imports or calls. Note direction, cycles, and shared code.
4. **Data**: find stores (connection configuration, migrations, ORM models), who owns each, and who else reads it.
5. **Integrations**: find outbound calls (HTTP clients, SDKs, queues, mail, storage) and inbound interfaces (routes, consumers, schedulers).
6. **Cross-cutting**: authentication, configuration, logging, error handling, and where each is implemented.
7. **Style**: name the pattern only if the code consistently follows it; otherwise describe what you see.

Write the overview as components, responsibilities, and a dependency diagram (Mermaid). Cite a path for each claim. List contradictions between docs and code, and every `UNKNOWN:` and `ASSUMPTION:`.
