"""Configuration files parse and the routing registry is internally consistent."""
import json
from pathlib import Path

import uadr_lib as lib

NAME = "config"
ROUTE_KEYS = ["when", "keywords", "workflow", "read", "consider", "skills", "approval"]


def run(root: Path, cfg: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    for key in ("framework_version", "project", "commands", "docs", "required_files", "context_budget"):
        if key not in cfg:
            errors.append(f"{lib.CONFIG_REL}: missing key '{key}'")
    if cfg.get("project", {}).get("mode") not in ("template", "greenfield", "existing"):
        errors.append(f"{lib.CONFIG_REL}: project.mode must be template, greenfield, or existing")
    if cfg.get("project", {}).get("mode") != "template" and not cfg.get("commands", {}).get("test"):
        warnings.append(f"commands.test is not configured in {lib.CONFIG_REL}: agents cannot verify changes")

    for rel in lib.list_files(root):
        if rel.endswith(".json") and rel.startswith((".agent/", ".automation/", ".claude/", ".github/", ".vscode/")):
            try:
                json.loads((root / rel).read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                errors.append(f"{rel}: invalid JSON ({exc})")
    try:
        data, modules = lib.load_routes(root), lib.load_modules(root)
    except (OSError, json.JSONDecodeError):
        return errors + ["routing registry unreadable"], warnings

    routed = set()
    for name, route in data.get("routes", {}).items():
        where = f"{lib.ROUTES_REL}: route '{name}'"
        for key in ROUTE_KEYS:
            if key not in route:
                errors.append(f"{where} missing '{key}'")
        workflow = route.get("workflow", "")
        routed.add(workflow)
        if not (root / workflow).is_file():
            errors.append(f"{where} workflow not found: {workflow}")
        for skill in route.get("skills", []):
            if not (root / lib.SKILLS_REL / skill / "SKILL.md").is_file():
                errors.append(f"{where} skill not found: {skill}")
        for item in list(route.get("read", [])) + list(route.get("consider", {})):
            if item == "@module":
                continue
            if not item.startswith(("docs/", ".agent/")):
                errors.append(f"{where} doc reference must be under docs/ or .agent/: {item}")
            elif item.startswith(".agent/") and not (root / item).is_file():
                errors.append(f"{where} framework doc not found: {item}")
    for rel in data.get("always", []):
        if not (root / rel).is_file():
            errors.append(f"{lib.ROUTES_REL}: 'always' doc not found: {rel}")
    for path in sorted((root / lib.WORKFLOWS_REL).glob("*.md")):
        rel = f"{lib.WORKFLOWS_REL}/{path.name}"
        if rel not in routed:
            errors.append(f"{rel} is not reachable from any route")

    names = set()
    for mod in modules:
        name = mod.get("name", "?")
        if name in names:
            errors.append(f"{lib.MODULES_REL}: duplicate module '{name}'")
        names.add(name)
        if not mod.get("paths"):
            errors.append(f"{lib.MODULES_REL}: module '{name}' has no paths")
        if not (root / mod.get("doc", "")).is_file():
            errors.append(f"{lib.MODULES_REL}: module '{name}' doc not found: {mod.get('doc')}")
        for pat in mod.get("paths", []):
            base = pat.split("*")[0].rstrip("/")
            if base and not (root / base).exists():
                warnings.append(f"{lib.MODULES_REL}: module '{name}' path does not exist: {pat}")
    return errors, warnings
