"""Agent instructions are consistent: thin entry point, thin adapters, complete workflows, valid skills."""
import re
from collections import defaultdict
from pathlib import Path

import uadr_lib as lib

NAME = "instructions"
WORKFLOW_SECTIONS = ["Objective", "Required context", "Documents to read", "Steps", "Files that may be modified",
                     "Validation", "Completion criteria", "Documentation updates", "Human approval"]
ENTRY_MUST_REFERENCE = [".agent/memory/state.md", "uadr.py route", ".agent/policies/approvals.md",
                        ".agent/policies/security.md", ".agent/policies/documentation.md", "uadr.py run", "uadr.py check"]


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    budget = cfg["context_budget"]

    entry = root / "AGENTS.md"
    entry_text = entry.read_text(encoding="utf-8") if entry.is_file() else ""
    for needle in ENTRY_MUST_REFERENCE:
        if needle not in entry_text:
            errors.append(f"AGENTS.md must reference '{needle}'")
    for ref in set(re.findall(r"`((?:\.agent|\.automation)/[^`\s<>*]+)`", entry_text)):
        if not (root / ref).exists():
            errors.append(f"AGENTS.md references a missing path: {ref}")

    adapters = []
    for pattern in cfg.get("adapters", {}).get("instruction_files", []):
        adapters += sorted(p.relative_to(root).as_posix() for p in root.glob(pattern))
    for rel in adapters:
        _, body = lib.parse_frontmatter((root / rel).read_text(encoding="utf-8"))
        lines = [ln for ln in body.splitlines() if ln.strip()]
        if len(lines) > budget["adapter_lines"]:
            errors.append(f"{rel}: adapter has {len(lines)} lines (max {budget['adapter_lines']}). "
                          f"Move content to AGENTS.md or .agent/ and keep a pointer")
        if "AGENTS.md" not in body and ".agent/" not in body:
            errors.append(f"{rel}: adapter must point to AGENTS.md or .agent/ instead of holding its own rules")

    for path in sorted((root / lib.WORKFLOWS_REL).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
        if headings != WORKFLOW_SECTIONS:
            missing = [s for s in WORKFLOW_SECTIONS if s not in headings]
            errors.append(f"{lib.WORKFLOWS_REL}/{path.name}: sections must be exactly the nine standard ones in order"
                          + (f" (missing: {', '.join(missing)})" if missing else ""))
        for ref in set(re.findall(r"`(\.agent/[^`\s<>*]+)`", text)):
            if not (root / ref).exists() and not ref.startswith(lib.ONBOARDING_REL):
                errors.append(f"{lib.WORKFLOWS_REL}/{path.name}: references a missing path: {ref}")
        for skill in set(re.findall(r"skills?: `([a-z-]+)`", text)) | set(re.findall(r", `([a-z-]+)`\)", text)):
            if not (root / lib.SKILLS_REL / skill / "SKILL.md").is_file():
                errors.append(f"{lib.WORKFLOWS_REL}/{path.name}: names unknown skill '{skill}'")

    for path in sorted((root / lib.SKILLS_REL).glob("*")):
        if not path.is_dir():
            continue
        skill = path / "SKILL.md"
        rel = f"{lib.SKILLS_REL}/{path.name}/SKILL.md"
        if not skill.is_file():
            errors.append(f"{rel} missing")
            continue
        meta, _ = lib.parse_frontmatter(skill.read_text(encoding="utf-8"))
        if meta.get("name") != path.name:
            errors.append(f"{rel}: frontmatter 'name' must equal the folder name")
        description = meta.get("description", "")
        if not description or len(description) > 1024:
            errors.append(f"{rel}: 'description' is required (max 1024 chars) and must say when to use the skill")
        elif not re.search(r"\buse (when|for|before|during|after)\b", description.lower()):
            warnings.append(f"{rel}: description should state when to use the skill ('Use when ...')")

    # Single source of truth: the same long sentence should not live in two instruction files.
    seen = defaultdict(set)
    instruction_files = ["AGENTS.md"] + adapters + [
        p for p in lib.markdown_files(root)
        if p.startswith(".agent/") and not p.startswith((".agent/templates/", ".agent/guide/", lib.ONBOARDING_REL))]
    for rel in instruction_files:
        if not (root / rel).is_file():
            continue
        for line in lib.strip_code((root / rel).read_text(encoding="utf-8")).splitlines():
            line = line.strip(" -*0123456789.|")
            if len(line) >= 90:
                seen[line].add(rel)
    for line, files in seen.items():
        if len(files) > 1:
            warnings.append(f"duplicated instruction in {', '.join(sorted(files))}: \"{line[:70]}...\"")
    return errors, warnings
