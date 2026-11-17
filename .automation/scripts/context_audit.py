"""Context audit: estimate the token cost of what an agent loads, tier by tier.

Estimates use ~4 characters per token. Use --check to enforce the budgets in uadr.json.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import uadr_lib as lib


def audit(root: Path = lib.ROOT) -> dict:
    cfg = lib.load_config(root)
    budget = cfg["context_budget"]
    data = lib.load_routes(root)
    tok = lambda rel: lib.file_tokens(root / rel) if (root / rel).is_file() else 0

    entry = tok("AGENTS.md")
    always = sum(tok(rel) for rel in data.get("always", []))
    modules = lib.load_modules(root)
    module_tokens = [tok(m["doc"]) for m in modules if tok(m["doc"])]
    avg_module = round(sum(module_tokens) / len(module_tokens)) if module_tokens else 0

    routes = {}
    for name, route in data["routes"].items():
        workflow = tok(route["workflow"])
        docs = sum(tok(item) for item in route.get("read", []) if item != "@module")
        needs_module = "@module" in route.get("read", [])
        skills = [tok(f"{lib.SKILLS_REL}/{s}/SKILL.md") for s in route.get("skills", [])]
        routes[name] = {
            "workflow": workflow, "required_docs": docs,
            "module_doc": avg_module if needs_module else 0,
            "typical": entry + always + workflow + docs + (avg_module if needs_module else 0),
            "skills_if_all_loaded": sum(skills),
        }

    md = lib.markdown_files(root)
    framework = sum(tok(p) for p in md if p.startswith(".agent/")) + entry + tok(lib.ROUTES_REL)
    project_docs = sum(tok(p) for p in md if p.startswith("docs/") and not p.startswith(lib.TEMPLATES_REL))
    worst_workflow = max((r["workflow"] for r in routes.values()), default=0)
    result = {
        "entry_point": entry, "always": always, "routes_file": tok(lib.ROUTES_REL),
        "bootstrap": entry + always + worst_workflow,
        "avg_module_doc": avg_module, "routes": routes,
        "everything": {"framework": framework, "project_docs": project_docs},
        "violations": [],
    }

    def limit(label: str, value: int, key: str) -> None:
        if value > budget[key]:
            result["violations"].append(f"{label}: ~{value} tokens exceeds {key}={budget[key]}")

    limit("AGENTS.md", entry, "entry_point_tokens")
    limit("bootstrap (AGENTS.md + state + largest workflow)", result["bootstrap"], "bootstrap_tokens")
    for path in sorted((root / lib.WORKFLOWS_REL).glob("*.md")):
        limit(f"{lib.WORKFLOWS_REL}/{path.name}", lib.file_tokens(path), "workflow_tokens")
    for path in sorted((root / lib.SKILLS_REL).glob("*/SKILL.md")):
        limit(f"{lib.SKILLS_REL}/{path.parent.name}/SKILL.md", lib.file_tokens(path), "skill_tokens")
    for path in sorted((root / ".agent/memory").glob("*.md")):
        if path.name != "README.md":
            limit(f".agent/memory/{path.name}", lib.file_tokens(path), "memory_file_tokens")
    return result


def render(r: dict) -> str:
    lines = [
        "Context audit (estimated tokens, ~4 chars/token)",
        "",
        f"Tier 0  AGENTS.md (always loaded)              {r['entry_point']:>6}",
        f"Tier 1  memory/state.md (every task)           {r['always']:>6}",
        f"        bootstrap incl. largest workflow       {r['bootstrap']:>6}",
        f"        (routes.json if read whole instead of via the router: {r['routes_file']})",
        "",
        f"{'Route':<24}{'workflow':>9}{'req.docs':>9}{'module':>8}{'TYPICAL':>9}{'+all skills':>12}",
    ]
    for name, row in r["routes"].items():
        lines.append(f"{name:<24}{row['workflow']:>9}{row['required_docs']:>9}{row['module_doc']:>8}"
                     f"{row['typical']:>9}{row['skills_if_all_loaded']:>12}")
    everything = r["everything"]["framework"] + r["everything"]["project_docs"]
    typical = [row["typical"] for row in r["routes"].values()]
    avg = round(sum(typical) / len(typical)) if typical else 0
    lines += [
        "",
        "TYPICAL = AGENTS.md + state + workflow + required docs that exist + average module doc.",
        f"Average typical task context: {avg}",
        f"Reading everything instead:   {everything} "
        f"(framework {r['everything']['framework']}, project docs {r['everything']['project_docs']})",
    ]
    if everything:
        lines.append(f"Progressive loading uses about {100 * avg / everything:.0f}% of the full corpus per task.")
    if r["violations"]:
        lines += ["", "BUDGET VIOLATIONS:"] + [f"  - {v}" for v in r["violations"]]
    else:
        lines += ["", "All context budgets satisfied."]
    return "\n".join(lines)


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py audit", description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit non-zero on budget violations")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)
    result = audit(root)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 1 if args.check and result["violations"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
