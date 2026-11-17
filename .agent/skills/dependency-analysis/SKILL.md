---
name: dependency-analysis
description: Determine what a piece of code depends on and what depends on it, internally and externally. Use before changing an interface, moving code, altering a schema, or upgrading a package.
---
# Dependency analysis

1. **Define the target** precisely: symbol, file, endpoint, table, or package.
2. **Inbound (who uses it)**: search for the name, its imports, and indirect references such as string keys, routes, configuration, reflection, dependency-injection registrations, serialised field names, and tests. Search the whole repository, not only the module.
3. **Outbound (what it uses)**: read its imports and calls; note external packages, services, and data it touches.
4. **Cross-boundary consumers**: other services, scripts, pipelines, dashboards, and documented public contracts. If consumers outside the repository are possible, say so; absence of local callers does not prove absence of users.
5. **Third-party packages**: read the manifest and lockfile for the version in use, who requires it (direct or transitive), and how widely the API is used.
6. **Classify impact** for each dependent: unaffected, needs a mechanical update, needs a behaviour decision.

Output a short list: dependents with paths, risk per dependent, and anything you could not rule out.
