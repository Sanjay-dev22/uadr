---
purpose: Defines which actions an agent may take alone and which require explicit human approval.
read_when: A task touches production, data, infrastructure, security controls, dependencies, architecture, or git history.
---
# Human approval policy

Approval means an explicit instruction from an authorised human in the current task (issue, PR comment, or chat) that names the action. Approval is not transferable to other actions, and silence is not approval. When approval is needed: stop, state the action, its blast radius, and the rollback, then wait.

| Area | Agent may do alone | Requires approval |
| --- | --- | --- |
| Code | Edit within the routed modules, add tests, fix lint | Changes outside the task's modules; deleting or disabling tests |
| Architecture | Propose options, draft an ADR with status `proposed` | Implementing a new module, boundary, pattern, or technology |
| Dependencies | Patch and minor upgrades that pass tests | New dependency, major upgrade, licence change, new package source |
| Public contracts | Additive, backward-compatible changes | Breaking changes, removals, new unauthenticated interfaces |
| Database | Write migrations and run them on a local or disposable database | Running on shared or production data; drop, truncate, bulk update or delete, type narrowing |
| Infrastructure | Read configuration, draft changes | Applying infrastructure, CI/CD, permission, or network changes |
| Deployment | Build and verify artefacts | Any deployment or rollback outside a local environment |
| Production | Read documentation and sanitised logs supplied by a human | Any access, command, restart, data read or write in production |
| Security | Report findings, fix within existing controls | Changing authentication, authorisation, cryptography, or disabling a check |
| Secrets | Reference secrets by name through the configured secret store | Creating, rotating, or viewing secret values |
| Git | Commit to a task branch, open a draft PR | Force push, history rewrite, merge to a protected branch, tagging a release |
| Framework | Fix docs, add modules to the registry | Changing `AGENTS.md` rules, policies, or approval gates |

If an action is not listed and is hard to reverse or visible outside the repository, treat it as requiring approval.
