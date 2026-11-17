"""Expose .agent/skills in the folders agent platforms scan (.claude/skills, .agents/skills).

Creates relative symlinks; use --copy where symlinks are unavailable (re-run after editing skills).
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import uadr_lib as lib


def sync(root: Path, copy: bool = False) -> list[str]:
    messages = []
    source = root / lib.SKILLS_REL
    for rel in lib.load_config(root).get("adapters", {}).get("skill_links", []):
        link = root / rel
        if link.is_symlink() or link.is_file():
            link.unlink()
        elif link.is_dir():
            shutil.rmtree(link)
        link.parent.mkdir(parents=True, exist_ok=True)
        if not copy:
            try:
                os.symlink(os.path.relpath(source, link.parent), link, target_is_directory=True)
                messages.append(f"linked {rel} -> {lib.SKILLS_REL}")
                continue
            except OSError:
                pass
        shutil.copytree(source, link)
        messages.append(f"copied {lib.SKILLS_REL} -> {rel}")
    return messages


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py sync-adapters", description=__doc__)
    ap.add_argument("--copy", action="store_true", help="copy instead of symlink")
    args = ap.parse_args(argv)
    for message in sync(root, args.copy):
        print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
