"""Run project commands configured in .automation/configuration/uadr.json.

Gives every agent one technology-agnostic way to build, lint, and test,
and reports unconfigured commands as NOT RUN so they are never mistaken for a pass.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import uadr_lib as lib

ALL_ORDER = ["lint", "static", "build", "test"]
NOT_CONFIGURED = 3


def run_one(name: str, command: str, root: Path) -> str:
    if not command:
        print(f"[{name}] NOT CONFIGURED - set commands.{name} in {lib.CONFIG_REL}")
        return "not run (not configured)"
    print(f"[{name}] $ {command}", flush=True)
    code = subprocess.run(command, shell=True, cwd=root).returncode
    return "passed" if code == 0 else f"FAILED (exit {code})"


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    commands = lib.load_config(root).get("commands", {})
    ap = argparse.ArgumentParser(prog="uadr.py run", description=__doc__)
    ap.add_argument("name", help=f"one of: {', '.join(commands)}, all")
    ap.add_argument("--strict", action="store_true", help="with 'all': fail if test is not configured")
    args = ap.parse_args(argv)

    if args.name != "all":
        if args.name not in commands:
            print(f"unknown command '{args.name}'. Known: {', '.join(commands)}, all")
            return 2
        result = run_one(args.name, commands[args.name], root)
        print(f"RESULT {args.name}: {result}")
        return 0 if result == "passed" else NOT_CONFIGURED if result.startswith("not run") else 1

    results = {name: run_one(name, commands.get(name, ""), root) for name in ALL_ORDER}
    print("\nRESULTS (report exactly these):")
    for name, result in results.items():
        print(f"  {name:<7} {result}")
    if any(r.startswith("FAILED") for r in results.values()):
        return 1
    if args.strict and results["test"].startswith("not run"):
        print("strict mode: test command is not configured")
        return NOT_CONFIGURED
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
