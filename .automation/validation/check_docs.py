"""Every doc declares its purpose and when to read it; registry, index, and templates are consistent."""
import re
from pathlib import Path

import uadr_lib as lib
import index as index_cmd

NAME = "docs"
STATUSES = {"draft", "verified", "deprecated"}


def is_legacy(rel: str, cfg: dict) -> bool:
    return any(lib.glob_match(g, rel) for g in cfg.get("docs", {}).get("legacy_paths", []))


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    drafts, markers, legacy = [], 0, 0
    for rel in lib.markdown_files(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        meta, body = lib.parse_frontmatter(text)
        if rel.startswith(lib.TEMPLATES_REL + "/") and rel.endswith(".template.md"):
            for key in ("target", "purpose", "read_when", "status"):
                if not meta.get(key):
                    errors.append(f"{rel}: template frontmatter missing '{key}'")
            continue
        in_docs = rel.startswith("docs/")
        in_agent = rel.startswith(".agent/") and not rel.startswith(
            (lib.SKILLS_REL + "/", ".agent/templates/", lib.ONBOARDING_REL + "/"))
        if not (in_docs or in_agent):
            continue
        if is_legacy(rel, cfg):
            legacy += 1
            continue
        for key in ("purpose", "read_when"):
            if not meta.get(key):
                errors.append(f"{rel}: frontmatter missing '{key}'")
        if "{{" in lib.strip_code(body):
            errors.append(f"{rel}: unreplaced template placeholder '{{{{...}}}}'")
        if in_docs and rel not in (index_cmd.INDEX_REL, lib.TEMPLATES_REL + "/README.md"):
            status = meta.get("status")
            if status not in STATUSES:
                errors.append(f"{rel}: frontmatter 'status' must be one of {sorted(STATUSES)}")
            elif status == "draft":
                drafts.append(rel)
            elif status == "verified" and "<!--" in lib.strip_code(body):
                errors.append(f"{rel}: marked verified but still contains template guidance comments")
            markers += len(re.findall(r"\b(UNKNOWN|ASSUMPTION):", lib.strip_code(body)))

    modules = lib.load_modules(root)
    registered = {m.get("doc") for m in modules}
    for path in sorted((root / "docs/modules").glob("*.md")):
        rel = f"docs/modules/{path.name}"
        if rel not in registered:
            warnings.append(f"{rel} is not registered in {lib.MODULES_REL}: the router cannot find it")
    if index_cmd.main(["--check"], root) != 0:
        errors.append("docs/index.md is out of date: run python3 .automation/uadr.py index")
    if drafts:
        warnings.append(f"{len(drafts)} draft doc(s) to complete: " + ", ".join(drafts[:8])
                        + (" ..." if len(drafts) > 8 else ""))
    if markers:
        warnings.append(f"{markers} UNKNOWN/ASSUMPTION marker(s) in project docs await verification")
    if legacy:
        warnings.append(f"{legacy} legacy doc(s) exempt from checks (docs.legacy_paths): review and adopt them incrementally")
    return errors, warnings
