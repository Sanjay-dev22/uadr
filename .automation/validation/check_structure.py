"""Required files exist and skill adapter folders mirror .agent/skills."""
import filecmp
from pathlib import Path

import uadr_lib as lib

NAME = "structure"


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    for rel in cfg.get("required_files", []):
        if not (root / rel).is_file():
            errors.append(f"required file missing: {rel}")
    source = root / lib.SKILLS_REL
    skills = sorted(p.parent.name for p in source.glob("*/SKILL.md"))
    for rel in cfg.get("adapters", {}).get("skill_links", []):
        link = root / rel
        if not link.exists():
            errors.append(f"{rel} missing or broken: run python3 .automation/uadr.py sync-adapters")
        elif link.resolve() != source.resolve():
            copied = sorted(p.parent.name for p in link.glob("*/SKILL.md"))
            stale = copied != skills or any(
                not filecmp.cmp(source / s / "SKILL.md", link / s / "SKILL.md", shallow=False) for s in skills)
            if stale:
                errors.append(f"{rel} is a stale copy of {lib.SKILLS_REL}: run python3 .automation/uadr.py sync-adapters --copy")
    onboarding = root / lib.ONBOARDING_REL
    if (onboarding / "conflicts").is_dir():
        pending = [p.relative_to(onboarding / "conflicts").as_posix()
                   for p in (onboarding / "conflicts").rglob("*") if p.is_file()]
        warnings.append(f"{len(pending)} adoption conflict(s) awaiting merge in {lib.ONBOARDING_REL}/conflicts: "
                        + ", ".join(pending[:5]))
    elif onboarding.is_dir():
        warnings.append(f"{lib.ONBOARDING_REL}/ still present: onboarding not finished (delete it when the report has no gaps)")
    return errors, warnings
