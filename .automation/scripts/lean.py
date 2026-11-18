"""Generate a lean AGENTS.md from the code: the whole always-loaded context, produced without an agent run.

The file holds only what an agent cannot cheaply infer and must always follow: a map of where things live,
how to run the tests, the definition of done, and the approval rules. Everything else stays out of context.

Descriptions in the map come from Python docstrings, or from a package's exported names. Other languages get
a directory map without descriptions.
"""
import argparse
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import uadr_lib as lib
import scan as scan_cmd

MAX_ENTRIES = 40
CHANGELOG = re.compile(r"^(CHANGES|CHANGELOG|HISTORY|NEWS|RELEASES?)(\.\w+)?$", re.IGNORECASE)


def first_line(text: str | None, limit: int = 90) -> str:
    if not text:
        return ""
    line = text.strip().splitlines()[0].strip().rstrip(".")
    return line if len(line) <= limit else line[: limit - 1].rstrip() + "..."


SKIP_DIRS = {"doc", "docs", "examples", "example", "benchmarks", "benchmark", "scripts", "tools", "bin", "tests",
             "test", "build", "dist", "node_modules", "vendor", "site-packages"}


def describe_py(path: Path) -> tuple[str, int]:
    """(one-line description, size in lines) of a module or a package's __init__."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (OSError, SyntaxError, ValueError):
        return "", 0
    doc = first_line(ast.get_docstring(tree))
    if doc and not doc.startswith(("=", "-", "*", "#")) and len(doc) > 12:
        return doc, source.count("\n") + 1
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
    funcs = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
             and not n.name.startswith("_")]
    exported = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level >= 1:
            exported += [a.asname or a.name for a in node.names if a.name != "*" and not a.name.startswith("_")]
    names = list(dict.fromkeys(classes or funcs or exported))[:4]
    return ("defines " + ", ".join(names) if names else ""), source.count("\n") + 1


def py_count(path: Path) -> int:
    return sum(1 for f in path.rglob("*.py") if not SKIP_DIRS & set(f.relative_to(path).parts[:-1]))


def source_root(root: Path) -> Path | None:
    """The directory holding the project's main Python source: most Python files outside docs, tests, examples."""
    options = []
    for top in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS):
        options.append(top)
        if not (top / "__init__.py").is_file():
            options += [p for p in sorted(top.iterdir()) if p.is_dir() and not p.name.startswith(".")
                        and p.name not in SKIP_DIRS]
    scored = [(py_count(p), p) for p in options]
    scored = [(n, p) for n, p in scored if n]
    if not scored:
        return None
    best = max(scored, key=lambda x: (x[0], -len(x[1].parts)))[1]
    while not (best / "__init__.py").is_file():  # a source folder such as src/: descend to the package
        kids = [p for p in best.iterdir() if p.is_dir() and py_count(p)]
        if len(kids) != 1:
            break
        best = kids[0]
    return best


def map_entries(root: Path, inventory: dict) -> list[str]:
    """Lines '`path` - description' for the main source areas, largest first."""
    base = source_root(root)
    if base is None:
        return [f"`{p}/`" for p in list(inventory["module_candidates"])[:MAX_ENTRIES]]
    entries: list[tuple[int, str]] = []
    for child in sorted(base.iterdir()):
        if child.name.startswith(".") or child.name in SKIP_DIRS or child.name == "__init__.py":
            continue
        if child.is_dir() and (child / "__init__.py").is_file():
            doc, _ = describe_py(child / "__init__.py")
            size = sum(describe_py(f)[1] for f in child.rglob("*.py") if not SKIP_DIRS & set(f.relative_to(child).parts))
        elif child.suffix == ".py":
            doc, size = describe_py(child)
        else:
            continue
        rel = child.relative_to(root).as_posix() + ("/" if child.is_dir() else "")
        entries.append((size, f"`{rel}`" + (f" - {doc}" if doc else "")))
    entries.sort(key=lambda e: -e[0])
    return [line for _, line in entries[:MAX_ENTRIES]]


def render(root: Path, name: str, commands: dict[str, str], inventory: dict, max_entries: int = MAX_ENTRIES) -> str:
    languages = ", ".join(list(inventory["languages"])[:3]) or "unknown language"
    layout = map_entries(root, inventory)[:max_entries] if max_entries > 0 else []
    tests = inventory["tests"]["roots"]
    test_hint = f" Tests: {', '.join(f'`{r}/`' for r in list(tests)[:3])}." if tests else ""
    changelog = next((f for f in sorted(p.name for p in root.iterdir() if p.is_file()) if CHANGELOG.match(f)), "")
    lines = [f"# AGENTS.md\n", f"{name} ({languages}).{test_hint}\n"]
    if layout:
        lines += ["## Where things live\n", "\n".join(f"- {entry}" for entry in layout) + "\n"]
    if commands:
        lines += ["## Commands\n", "\n".join(f"- {kind}: `{cmd}`" for kind, cmd in commands.items()) + "\n"]
    done = ["- A behaviour change needs an automated test that fails without it; a bug fix starts from a failing test.",
            "- Run the tests and report the real result. Say what you did not run, and why."]
    if changelog:
        done.append(f"- Add a `{changelog}` entry for user-visible changes.")
    done.append("- Update documentation the change affects.")
    lines += ["## Done means\n", "\n".join(done) + "\n"]
    lines += ["## Rules\n",
              "- Read the code and its callers before changing it. Mark guesses `ASSUMPTION:`.\n"
              "- Never read, print, or commit secrets, and never weaken a security check.\n"
              "- Ask a human before: production or deployment actions, destructive data or schema changes, "
              "infrastructure changes, new dependencies, auth or security changes, rewriting git history.\n"]
    return "\n".join(lines)


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py lean", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", help="repository to describe (default: this repository)")
    ap.add_argument("--name", help="project name (default: directory name)")
    ap.add_argument("--command", action="append", default=[], metavar="KIND=CMD",
                    help="verified command, e.g. test='python -m pytest'. Detected commands are used otherwise")
    ap.add_argument("--max-entries", type=int, default=MAX_ENTRIES, help="map size; 0 leaves the map out")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing AGENTS.md")
    ap.add_argument("--force", action="store_true", help="overwrite an existing AGENTS.md")
    args = ap.parse_args(argv)
    target = Path(args.target).resolve() if args.target else root
    inventory = scan_cmd.inventory(target)
    commands = {k: v[0].split("`")[1] for k, v in inventory["suggested_commands"].items() if v}
    for item in args.command:
        kind, _, cmd = item.partition("=")
        commands[kind] = cmd
    text = render(target, args.name or target.name, commands, inventory, args.max_entries)
    if args.stdout:
        print(text)
        return 0
    out = target / "AGENTS.md"
    if out.exists() and not args.force:
        print("AGENTS.md exists: not overwritten (use --force, or merge by hand)")
        return 2
    out.write_text(text, encoding="utf-8")
    claude = target / "CLAUDE.md"
    if not claude.exists():
        claude.write_text("@AGENTS.md\n", encoding="utf-8")
    print(f"wrote AGENTS.md (~{lib.est_tokens(text)} tokens, {len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
