---
applyTo: "docs/**/*.md"
---
Project documentation follows `.agent/policies/documentation.md`: frontmatter with `purpose`, `read_when`, `status`; only verified facts; gaps marked `UNKNOWN:`. Create docs with `python3 .automation/uadr.py new`, never edit `docs/index.md` by hand, and never edit files in `docs/templates/` when writing project docs.
