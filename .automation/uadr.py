#!/usr/bin/env python3
"""UADR command line: single entry point for all framework automation.

Usage: python3 .automation/uadr.py <command> [args]   (add -h to any command)
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for sub in ("", "scripts", "validation"):
    sys.path.insert(0, str(HERE / sub))

COMMANDS = {
    "route": ("scripts/route.py", "Find the workflow and minimum docs for a task"),
    "run": ("scripts/run.py", "Run a configured project command (test, build, lint, static, all)"),
    "check": ("validation/run_checks.py", "Run framework quality gates"),
    "audit": ("scripts/context_audit.py", "Estimate token cost of agent context"),
    "new": ("scripts/new.py", "Create a doc from a template (module, adr, doc)"),
    "index": ("scripts/index.py", "Regenerate docs/index.md from doc frontmatter"),
    "lean": ("scripts/lean.py", "Generate a lean AGENTS.md from the code (no agent run)"),
    "scan": ("scripts/scan.py", "Inventory an existing repository"),
    "adopt": ("scripts/adopt.py", "Install the framework (greenfield or existing repo)"),
    "sync-adapters": ("scripts/sync_adapters.py", "Link skills into agent-native folders"),
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help") or sys.argv[1] not in COMMANDS:
        print(__doc__)
        for name, (_, desc) in COMMANDS.items():
            print(f"  {name:<14} {desc}")
        return 0 if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help") else 2
    rel, _ = COMMANDS[sys.argv[1]]
    spec = importlib.util.spec_from_file_location("uadr_cmd", HERE / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return int(module.main(sys.argv[2:]) or 0)
    except BrokenPipeError:  # output piped into head, less, etc.
        return 0


if __name__ == "__main__":
    sys.exit(main())
