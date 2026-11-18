---
name: technical-debt-identification
description: Identify, evidence, and prioritise technical debt and risk. Use during onboarding or when assessing code health.
---
# Technical debt identification

1. **Look for signals**, each with evidence:
   - Change risk: large or deeply nested units, duplication, cyclic dependencies, modules everything depends on.
   - Safety net: untested critical paths, skipped or flaky tests, no CI gate.
   - Currency: end-of-life runtimes, deprecated APIs, long-outdated or vulnerable dependencies.
   - Operability: missing logging, no health checks, manual deployment steps, configuration in code.
   - Knowledge: undocumented modules, misleading docs, `TODO`/`FIXME`/`HACK` markers, code nobody can explain.
2. **Use history where available**: files that change often and are complex carry the most risk (`git log --format= --name-only | sort | uniq -c | sort -rn`).
3. **Assess each item**: impact if left, likelihood of causing a problem, and rough effort to fix.
4. **Prioritise** by impact and likelihood against effort; separate must-address risks from tolerable debt.
5. **Record** concise entries in `.agent/memory/known-issues.md`: what, where, why it matters, suggested remedy. Link an ADR or issue for large items.

Report observations, not judgements about authors. Do not fix debt outside the current task; record it.
