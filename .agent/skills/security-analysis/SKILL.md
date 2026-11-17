---
name: security-analysis
description: Find and assess security weaknesses in code - input handling, authn/authz, secrets, data exposure, dependencies. Use for security reviews, API work, and reviewing changes that touch trust boundaries.
---
# Security analysis

1. **Map the attack surface** in scope: every entry point that accepts external data (requests, messages, files, CLI, environment, third-party responses).
2. **Trace input to sinks**: queries, commands, file paths, templates, deserialisers, redirects, outbound requests. Flag any path lacking validation or safe APIs.
3. **Authentication and authorisation**: for each operation, where is identity established and where is permission checked? Look for checks missing on one path, checks done only client side, and object references not tied to the caller.
4. **Secrets and data**: hard-coded credentials, secrets or personal data in logs and errors, overly broad responses, weak or home-made cryptography, missing transport or storage protection.
5. **Dependencies and configuration**: known-vulnerable versions, debug modes, permissive CORS, default credentials, verbose errors.
6. **Verify each finding** by reading the full path; discard those blocked by an upstream control.
7. **Rate** by impact and likelihood: critical, high, medium, low.

Report location, impact, evidence, and remediation per finding. Never include working exploit payloads or secret values. Rules are in `.agent/policies/security.md`.
