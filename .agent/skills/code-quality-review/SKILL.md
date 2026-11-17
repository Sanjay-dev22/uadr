---
name: code-quality-review
description: Evaluate code or a diff for correctness, clarity, and conventions. Use for pull request review and self-review before completion.
---
# Code quality review

Review in priority order and stop escalating minor points once major ones exist.

1. **Correctness**: does it do what is intended for all inputs? Check boundaries, null and empty cases, error paths, resource cleanup, concurrency, and changed callers.
2. **Scope**: is every change needed for the task? Flag unrelated edits, speculative generality, and leftover debug or dead code.
3. **Tests**: do they exercise the new behaviour and fail without it? Are they deterministic?
4. **Design**: is the code in the right module and layer? Does it reuse existing helpers and patterns? Is anything duplicated?
5. **Readability**: accurate names, small functions, straightforward control flow, comments that explain why.
6. **Conventions**: project coding standards, formatting, and error and logging style. Prefer automated linters over opinion.
7. **Docs**: required updates present and accurate.

For each finding give location, the problem, why it matters, and a concrete suggestion. Label as blocking, should fix, or optional. Verify by reading surrounding code before reporting, and say what you did not check.
