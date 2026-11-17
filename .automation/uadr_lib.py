"""Shared helpers for UADR automation. Standard library only."""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_REL = ".automation/configuration/uadr.json"
ROUTES_REL = ".agent/routing/routes.json"
MODULES_REL = ".agent/routing/modules.json"
SKILLS_REL = ".agent/skills"
WORKFLOWS_REL = ".agent/workflows"
TEMPLATES_REL = "docs/templates"
ONBOARDING_REL = ".agent/onboarding"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_config(root: Path = ROOT) -> dict:
    return read_json(root / CONFIG_REL)


def load_routes(root: Path = ROOT) -> dict:
    return read_json(root / ROUTES_REL)


def load_modules(root: Path = ROOT) -> list[dict]:
    return read_json(root / MODULES_REL).get("modules", [])


def est_tokens(text: str) -> int:
    """Heuristic: ~4 characters per token for English prose and code (+-15%)."""
    return math.ceil(len(text) / 4)


def file_tokens(path: Path) -> int:
    try:
        return est_tokens(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a leading '---' block of simple 'key: value' lines."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "#")):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    body = text[end + 4:]
    return meta, body.lstrip("\n")


def render_frontmatter(meta: dict) -> str:
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in meta.items()) + "---\n"


def glob_match(pattern: str, path: str) -> bool:
    """Match a repo-relative posix path. Plain paths match as prefix; ** crosses dirs."""
    pattern = pattern.strip("/")
    if not any(c in pattern for c in "*?"):
        return path == pattern or path.startswith(pattern + "/")
    rx, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            rx += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            rx += ".*"
            i += 2
        elif pattern[i] == "*":
            rx += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            rx += "[^/]"
            i += 1
        else:
            rx += re.escape(pattern[i])
            i += 1
    return re.fullmatch(rx, path) is not None


def module_for_path(path: str, modules: list[dict]) -> dict | None:
    """Return the module whose most specific path pattern matches."""
    best, best_len = None, -1
    for mod in modules:
        for pat in mod.get("paths", []):
            if glob_match(pat, path) and len(pat) > best_len:
                best, best_len = mod, len(pat)
    return best


def list_files(root: Path = ROOT, ignore_dirs: list[str] | None = None) -> list[str]:
    """Repo-relative posix paths of regular files (git-aware, never follows symlinks)."""
    if ignore_dirs is None:  # a target that has not adopted the framework yet uses this checkout's settings
        ignore_dirs = load_config(root if (root / CONFIG_REL).is_file() else ROOT).get("ignore_dirs", [])
    ignore = set(ignore_dirs)
    ignore.add(".git")
    paths: list[str] = []
    if (root / ".git").exists():
        try:
            out = subprocess.run(
                ["git", "ls-files", "-co", "--exclude-standard"],
                cwd=root, capture_output=True, text=True, check=True,
            ).stdout
            paths = [p for p in out.splitlines() if p]
        except (OSError, subprocess.CalledProcessError):
            paths = []
    if not paths:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ignore]
            rel = Path(dirpath).relative_to(root)
            paths.extend((rel / f).as_posix() for f in filenames)
    result = []
    for p in paths:
        if any(part in ignore for part in p.split("/")[:-1]):
            continue
        full = root / p
        if full.is_file() and not full.is_symlink():
            result.append(p)
    return sorted(result)


def markdown_files(root: Path = ROOT) -> list[str]:
    return [p for p in list_files(root) if p.endswith(".md")]


def strip_code(text: str) -> str:
    """Blank out fenced code blocks and inline code, preserving line count."""
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            out.append("")
        elif in_fence:
            out.append("")
        else:
            out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
