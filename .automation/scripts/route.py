"""Task router: print the workflow and the minimum documents for a task."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import uadr_lib as lib


def classify(text: str, routes: dict) -> list[tuple[int, str]]:
    text = text.lower()
    scored = []
    for name, route in routes.items():
        score = 0
        for kw in route.get("keywords", []):
            if re.search(r"\b" + re.escape(kw.lower()), text):
                score += 2 if " " in kw else 1
        if score:
            scored.append((score, name))
    return sorted(scored, key=lambda s: (-s[0], s[1]))


def describe(rel: str, root: Path) -> str:
    path = root / rel
    if path.is_file():
        return f"{rel}  (~{lib.file_tokens(path)} tok)"
    return f"{rel}  (not written yet - skip; create it only if this task needs it)"


def deliverables(root: Path, workflow: str) -> list[str]:
    """Completion criteria and documentation updates, read from the workflow so they exist in one place."""
    path = root / workflow
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    lines = []
    for heading in ("Completion criteria", "Documentation updates"):
        match = re.search(rf"^## {heading}\n\n(.*?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
        if match:
            lines += [ln[2:] for ln in match.group(1).splitlines() if ln.startswith("- ")]
    return lines


def module_lines(paths: list[str], root: Path) -> list[str]:
    modules = lib.load_modules(root)
    if not paths:
        if not modules:
            return ["module doc: none registered yet (see .agent/routing/modules.json)"]
        return ["module doc: re-run with --path <file> for each area you will touch"]
    lines, seen = [], set()
    for p in paths:
        mod = lib.module_for_path(p.strip("./"), modules)
        if mod is None:
            lines.append(f"no module registered for {p} - explore the code, then register one "
                         f"(uadr.py new module <name> --paths <glob>)")
        elif mod["name"] not in seen:
            seen.add(mod["name"])
            lines.append(describe(mod["doc"], root) + f"  [module: {mod['name']}]")
    return lines


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py route", description=__doc__)
    ap.add_argument("task", nargs="?", help="route name, or a free-text task description")
    ap.add_argument("--path", action="append", default=[], help="file or directory you expect to touch (repeatable)")
    ap.add_argument("--list", action="store_true", help="list all routes")
    args = ap.parse_args(argv)
    data = lib.load_routes(root)
    routes = data["routes"]

    if args.list or not args.task:
        for name, route in routes.items():
            print(f"{name:<24} {route['when']}")
        return 0

    name = args.task if args.task in routes else None
    if name is None:
        ranked = classify(args.task, routes)
        if not ranked:
            print("No route matched. Pick one explicitly:")
            for rname, route in routes.items():
                print(f"  {rname:<24} {route['when']}")
            return 1
        name = ranked[0][1]
        others = [n for s, n in ranked[1:4]]
        if others:
            print(f"Best match: {name}. Also plausible: {', '.join(others)}. "
                  f"Choose by the 'when' line; re-run with the route name to switch.\n")

    route = routes[name]
    print(f"Route: {name} - {route['when']}")
    print(f"Workflow: {describe(route['workflow'], root)}")
    print("Read first:")
    for rel in data.get("always", []):
        print(f"  - {describe(rel, root)}")
    for item in route.get("read", []):
        for line in (module_lines(args.path, root) if item == "@module" else [describe(item, root)]):
            print(f"  - {line}")
    consider = [("module doc" if item == "@module" else item, cond)
                for item, cond in route.get("consider", {}).items()
                if item == "@module" or (root / item).is_file()]
    if consider:
        print("Read only if:")
        for label, cond in consider:
            print(f"  - {label}  <- {cond}")
    if route.get("skills"):
        print("Skills (load one only when a step needs it):")
        for skill in route["skills"]:
            print(f"  - {lib.SKILLS_REL}/{skill}/SKILL.md")
    must = deliverables(root, route["workflow"])
    if must:
        print("Deliver:")
        for line in must:
            print(f"  - {line}")
    print(f"Human approval: {route.get('approval', 'see .agent/policies/approvals.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
