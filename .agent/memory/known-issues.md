---
purpose: Known technical limitations and outstanding technical debt.
read_when: A symptom may be a known limitation, or you are planning work in an area with recorded debt.
---
# Known issues

## Limitations

- Token counts from `uadr.py audit` are a four-characters-per-token estimate, not a tokenizer count.
- The secret scan is pattern based; it complements a dedicated scanner and does not replace one.

- Benchmarked on small tasks, the framework raises cost per task by 24% to 86% and shows no correctness gain (`benchmark/README.md`). Do not claim token savings.
- Agents rarely open workflow files on small tasks; anything that must always happen belongs in `AGENTS.md` or the router output.

## Technical debt

- None recorded.
