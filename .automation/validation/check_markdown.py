"""Lightweight, dependency-free Markdown lint for framework-managed files."""
import re
from pathlib import Path

import uadr_lib as lib
from check_links import in_scope

NAME = "markdown"


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    for rel in lib.markdown_files(root):
        if not in_scope(rel, cfg):
            continue
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        if text and not text.endswith("\n"):
            errors.append(f"{rel}: file must end with a newline")
        _, body = lib.parse_frontmatter(text)
        offset = text.count("\n") - body.count("\n")
        fence, h1, last_level = None, 0, 0
        for number, line in enumerate(body.split("\n"), offset + 1):
            stripped = line.lstrip()
            marker = re.match(r"(`{3,}|~{3,})", stripped)
            if marker:
                if fence is None:
                    fence = marker.group(1)[0]
                elif marker.group(1)[0] == fence:
                    fence = None
                continue
            if fence:
                continue
            if line != line.rstrip():
                warnings.append(f"{rel}:{number}: trailing whitespace")
            if "\t" in line:
                warnings.append(f"{rel}:{number}: hard tab")
            heading = re.match(r"(#{1,6})\s+\S", line)
            if heading:
                level = len(heading.group(1))
                if level == 1:
                    h1 += 1
                if last_level and level > last_level + 1:
                    warnings.append(f"{rel}:{number}: heading level jumps from {last_level} to {level}")
                last_level = level
            elif re.match(r"#{1,6}\S", line) and not line.startswith("#!"):
                warnings.append(f"{rel}:{number}: heading needs a space after '#'")
        if fence:
            errors.append(f"{rel}: unclosed code fence")
        if h1 > 1:
            errors.append(f"{rel}: more than one top-level heading")
    return errors, warnings
