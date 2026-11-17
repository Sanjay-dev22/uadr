"""Relative Markdown links resolve to existing files."""
import re
from pathlib import Path

import uadr_lib as lib
from check_docs import is_legacy

NAME = "links"
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def in_scope(rel: str, cfg: dict) -> bool:
    if rel.startswith(lib.ONBOARDING_REL + "/") or is_legacy(rel, cfg):
        return False
    return any(lib.glob_match(g, rel) for g in cfg.get("docs", {}).get("lint_paths", ["**"]))


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors = []
    for rel in lib.markdown_files(root):
        if not in_scope(rel, cfg) or rel.endswith(".template.md"):
            continue
        text = lib.strip_code((root / rel).read_text(encoding="utf-8", errors="replace"))
        for number, line in enumerate(text.split("\n"), 1):
            for target in LINK.findall(line):
                if re.match(r"[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
                    continue
                path = target.split("#")[0].split("?")[0]
                base = root if path.startswith("/") else (root / rel).parent
                if not (base / path.lstrip("/")).exists():
                    errors.append(f"{rel}:{number}: broken link -> {target}")
    return errors, []
