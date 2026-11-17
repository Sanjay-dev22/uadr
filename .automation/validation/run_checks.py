"""Run the framework quality gates. Exit code 1 if any check reports an error."""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for extra in (HERE, HERE.parent, HERE.parent / "scripts"):
    sys.path.insert(0, str(extra))
import uadr_lib as lib
import check_config
import check_context
import check_docs
import check_instructions
import check_links
import check_markdown
import check_secrets
import check_structure

CHECKS = [check_structure, check_config, check_docs, check_links, check_markdown, check_instructions,
          check_secrets, check_context]


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    names = [c.NAME for c in CHECKS]
    ap = argparse.ArgumentParser(prog="uadr.py check", description=__doc__)
    ap.add_argument("--only", help=f"comma-separated subset of: {', '.join(names)}")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--quiet", action="store_true", help="print failures only")
    args = ap.parse_args(argv)
    selected = args.only.split(",") if args.only else names
    unknown = [n for n in selected if n not in names]
    if unknown:
        print(f"unknown check(s): {', '.join(unknown)}. Available: {', '.join(names)}")
        return 2
    cfg = lib.load_config(root)
    total_errors = total_warnings = 0
    for check in CHECKS:
        if check.NAME not in selected:
            continue
        try:
            errors, warnings = check.run(root, cfg)
        except Exception as exc:  # a crashing check must fail the gate, not hide
            errors, warnings = [f"check crashed: {type(exc).__name__}: {exc}"], []
        if args.strict:
            errors, warnings = errors + warnings, []
        total_errors += len(errors)
        total_warnings += len(warnings)
        status = "FAIL" if errors else "ok" if not warnings else "warn"
        if not args.quiet or errors:
            print(f"[{status:>4}] {check.NAME}")
        for message in errors:
            print(f"       ERROR  {message}")
        if not args.quiet:
            for message in warnings:
                print(f"       warn   {message}")
    print(f"\nuadr check: {'FAILED' if total_errors else 'PASSED'} "
          f"({total_errors} error(s), {total_warnings} warning(s), {len(selected)} check(s) run)")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
