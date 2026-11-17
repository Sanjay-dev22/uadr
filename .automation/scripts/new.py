"""Create a project document from a template: module doc, ADR, or any template."""
import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import uadr_lib as lib
import index as index_cmd


def instantiate(root: Path, template: str, variables: dict, out: str | None = None, force: bool = False) -> str:
    tpl = root / lib.TEMPLATES_REL / f"{template}.template.md"
    if not tpl.is_file():
        names = sorted(p.name.removesuffix(".template.md") for p in (root / lib.TEMPLATES_REL).glob("*.template.md"))
        raise SystemExit(f"unknown template '{template}'. Available: {', '.join(names)}")
    variables = {"PROJECT_NAME": lib.load_config(root)["project"]["name"],
                 "DATE": datetime.date.today().isoformat(), **variables}
    text = tpl.read_text(encoding="utf-8")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    meta, body = lib.parse_frontmatter(text)
    target = out or meta.pop("target")
    meta.pop("target", None)
    dest = root / target
    if dest.exists() and not force:
        raise SystemExit(f"{target} already exists (read and update it instead, or pass --force)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(lib.render_frontmatter(meta) + body, encoding="utf-8")
    return target


def next_adr_number(root: Path) -> str:
    numbers = [int(m.group(1)) for p in (root / "docs/decisions").glob("*.md")
               if (m := re.match(r"(\d{4})-", p.name))]
    return f"{max(numbers, default=0) + 1:04d}"


def register_module(root: Path, name: str, paths: list[str], doc: str) -> None:
    path = root / lib.MODULES_REL
    data = lib.read_json(path)
    modules = [m for m in data.get("modules", []) if m["name"] != name]
    modules.append({"name": name, "paths": paths, "doc": doc})
    data["modules"] = sorted(modules, key=lambda m: m["name"])
    lib.write_json(path, data)


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py new", description=__doc__)
    sub = ap.add_subparsers(dest="kind", required=True)
    p_mod = sub.add_parser("module", help="create a module doc and register its paths")
    p_mod.add_argument("name")
    p_mod.add_argument("--paths", nargs="+", required=True, help="globs or directories owned by the module")
    p_adr = sub.add_parser("adr", help="create the next numbered decision record")
    p_adr.add_argument("title")
    p_doc = sub.add_parser("doc", help="create a doc from any template in docs/templates")
    p_doc.add_argument("template")
    for p in (p_mod, p_adr, p_doc):
        p.add_argument("--out", help="override the target path")
        p.add_argument("--force", action="store_true", help="overwrite an existing file")
    args = ap.parse_args(argv)

    if args.kind == "module":
        name = lib.slugify(args.name)
        target = instantiate(root, "module", {"NAME": name, "PATHS": ", ".join(args.paths)}, args.out, args.force)
        register_module(root, name, args.paths, target)
        print(f"registered module '{name}' in {lib.MODULES_REL}")
    elif args.kind == "adr":
        number = next_adr_number(root)
        target = instantiate(root, "adr", {"NUMBER": number, "TITLE": args.title, "SLUG": lib.slugify(args.title)},
                             args.out, args.force)
    else:
        target = instantiate(root, args.template, {}, args.out, args.force)
    print(f"created {target} (status: draft) - fill it from verified sources")
    index_cmd.main([], root)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
