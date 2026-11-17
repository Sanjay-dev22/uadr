---
purpose: Security rules every change must satisfy, independent of language or stack.
read_when: Handling credentials, user input, personal data, dependencies, auth, or any security-routed task.
---
# Security policy

## Secrets and credentials

- Secrets live in the project's secret store or untracked local environment files, never in source, docs, tests, logs, commit messages, or agent output.
- Do not open `.env`, key, or credential files. Use `.env.example` and names only.
- If you encounter a real secret in the repository, stop, report its location without echoing the value, and recommend rotation.
- `python3 .automation/uadr.py check --only secrets` must pass before completion.

## Dependencies

- Prefer the standard library and existing dependencies. New dependencies need approval.
- Pin versions with the ecosystem's lockfile. Never install from an unreviewed source or disable integrity checks.
- Run the project's vulnerability audit if one is configured; report unresolved advisories.

## Input, output, and data

- Validate all external input at the boundary: type, size, range, and format. Reject by default.
- Use parameterised queries and safe APIs; never build queries, shell commands, or markup by concatenating input.
- Encode output for its context. Never deserialize untrusted data with an unsafe loader.
- Collect and log the minimum personal data. Never log secrets, tokens, or full personal records. Do not copy production data into tests or docs.

## Secure coding

- Enforce authorisation on the server side for every operation; do not rely on the client.
- Fail closed. Error messages returned to callers must not reveal internals.
- Use vetted cryptographic libraries with current defaults; never invent cryptography.
- Never bypass, silence, or lower the threshold of a security check, linter rule, or test to make a change pass.

## Production, data, and infrastructure

Production access, destructive database operations, infrastructure modification, and deployments always require approval under `approvals.md`. Prepare a rollback before asking.

## Reporting

A suspected vulnerability is reported privately to the maintainers through the channel in the project's security doc, not in a public issue or PR description.
