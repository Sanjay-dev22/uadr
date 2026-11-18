"""Install the framework into a repository.

Mode A (greenfield): a new or empty repository gets starter docs and a project README.
Mode B (existing): the framework is added beside the existing code; nothing existing is overwritten,
an inventory is generated, and a migration report is started for the onboarding workflow.
The mode is detected from whether the target contains source code; override with --mode.
"""
import argparse
import datetime
import filecmp
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import uadr_lib as lib
import index as index_cmd
import new as new_cmd
import scan as scan_cmd
import sync_adapters

TEMPLATE_MARKER = "<!-- uadr:template-file -->"
BLOCK = re.compile(r"(<!-- uadr:project:start -->\n).*?(<!-- uadr:project:end -->)", re.DOTALL)
STARTER_DOCS = ["project-overview", "architecture-overview", "setup-and-build", "coding-standards", "testing-strategy"]
# Replaced on --upgrade. Project-owned files (config, routing, memory, AGENTS.md) are never replaced.
FRAMEWORK_OWNED = (".agent/workflows/", ".agent/skills/", ".agent/policies/", ".agent/templates/", ".agent/guide/",
                   ".agent/README.md", ".agent/memory/README.md", ".automation/scripts/", ".automation/validation/",
                   ".automation/tests/", ".automation/uadr.py", ".automation/uadr_lib.py", "docs/templates/")
FRESH = {".agent/routing/modules.json": '{\n  "modules": []\n}\n'}


def memory_file(purpose: str, read_when: str, body: str) -> str:
    return f"---\npurpose: {purpose}\nread_when: {read_when}\n---\n{body}"


def copy_framework(src: Path, target: Path, upgrade: bool) -> dict:
    log = {"added": [], "kept": [], "conflicts": [], "upgraded": []}
    files = []
    for rel in lib.load_config(src)["framework_paths"]:
        path = src / rel
        if path.is_file():
            files.append(rel)
        elif path.is_dir():
            files += [p.relative_to(src).as_posix() for p in sorted(path.rglob("*")) if p.is_file()]
    for rel in files:
        if "__pycache__" in rel or rel.startswith(lib.ONBOARDING_REL + "/"):
            continue
        source, dest = src / rel, target / rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            if rel in FRESH:
                dest.write_text(FRESH[rel], encoding="utf-8")
            else:
                shutil.copy2(source, dest)
            log["added"].append(rel)
        elif filecmp.cmp(source, dest, shallow=False):
            log["kept"].append(rel)
        elif upgrade and rel.startswith(FRAMEWORK_OWNED):
            shutil.copy2(source, dest)
            log["upgraded"].append(rel)
        elif upgrade:
            log["kept"].append(rel)
        else:
            stash = target / lib.ONBOARDING_REL / "conflicts" / rel
            stash.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, stash)
            log["conflicts"].append(rel)
    return log


def set_project_block(target: Path, text: str) -> bool:
    path = target / "AGENTS.md"
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    if not BLOCK.search(content):
        return False
    path.write_text(BLOCK.sub(lambda m: m.group(1) + text.strip() + "\n" + m.group(2), content), encoding="utf-8")
    return True


def write_if_template(path: Path, content: str) -> bool:
    """Write when the file is absent or is still the framework template's own copy."""
    if path.exists() and TEMPLATE_MARKER not in path.read_text(encoding="utf-8", errors="replace"):
        return False
    path.write_text(content, encoding="utf-8")
    return True


def configure(target: Path, name: str, mode: str, legacy: list[str]) -> None:
    cfg = lib.load_config(target)
    cfg["project"] = {"name": name, "mode": mode}
    cfg["docs"]["legacy_paths"] = legacy
    cfg["commands"] = {key: "" for key in cfg["commands"]}
    lib.write_json(target / lib.CONFIG_REL, cfg)
    today = datetime.date.today().isoformat()
    (target / ".agent/memory/handover.md").write_text(memory_file(
        "Notes for the next agent session on work left in progress.",
        "Start of a session when state.md lists an active task, or when resuming someone else's work.",
        "# Handover\n\nNo work in progress.\n"), encoding="utf-8")
    (target / ".agent/memory/known-issues.md").write_text(memory_file(
        "Known technical limitations and outstanding technical debt.",
        "A symptom may be a known limitation, or you are planning work in an area with recorded debt.",
        "# Known issues\n\n## Limitations\n\n- None recorded.\n\n## Technical debt\n\n- None recorded.\n"),
        encoding="utf-8")
    workflow = "init-greenfield" if mode == "greenfield" else "onboard-existing-repo"
    (target / ".agent/memory/state.md").write_text(memory_file(
        "Current project state, active tasks, and recent significant changes.", "Start of every task.",
        f"# Project state\n\n## Now\n\n- Mode: {mode}. UADR framework installed {today}.\n"
        f"- Project commands are not configured yet (`{lib.CONFIG_REL}`).\n"
        f"- Project docs are drafts or absent; trust code over drafts.\n\n## Active tasks\n\n"
        f"- Complete `.agent/workflows/{workflow}.md`.\n\n## Recent significant changes\n\n"
        f"- {today}: UADR framework installed.\n"), encoding="utf-8")


def finalize_greenfield(target: Path, name: str, description: str) -> list[str]:
    notes = []
    for template in STARTER_DOCS:
        try:
            notes.append("created " + new_cmd.instantiate(target, template, {}))
        except SystemExit as exc:
            notes.append(f"kept existing doc ({exc})")
    set_project_block(target, f"""{name}: {description}
Status: new project being initialised. Starter docs are drafts; continue `.agent/workflows/init-greenfield.md`.
Architecture: `docs/architecture/overview.md`. Module registry: `.agent/routing/modules.json`.""")
    readme = f"""# {name}

{description}

## Working in this repository

This repository is developed agent-first with the UADR framework.

- AI agents start at [AGENTS.md](AGENTS.md).
- Humans start at [docs/index.md](docs/index.md) for project documentation and
  [.agent/guide/adoption.md](.agent/guide/adoption.md) for how the framework operates.

```bash
python3 .automation/uadr.py run all   # lint, static analysis, build, test (as configured)
python3 .automation/uadr.py check     # documentation and framework quality gates
```
"""
    if write_if_template(target / "README.md", readme):
        notes.append("wrote project README.md")
    changelog = ("# Changelog\n\nNotable user-visible changes. Format: [Keep a Changelog]"
                 "(https://keepachangelog.com/en/1.1.0/).\n\n## Unreleased\n\n### Added\n\n- Project initialised.\n")
    if write_if_template(target / "CHANGELOG.md", changelog):
        notes.append("wrote CHANGELOG.md")
    gitignore = target / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(".env\n.env.*\n!.env.example\n__pycache__/\n*.pyc\n", encoding="utf-8")
        notes.append("wrote .gitignore")
    return notes


def finalize_existing(target: Path, name: str, log: dict, inv: dict) -> list[str]:
    notes = []
    onboarding = target / lib.ONBOARDING_REL
    onboarding.mkdir(parents=True, exist_ok=True)
    (onboarding / "inventory.md").write_text(scan_cmd.render(inv), encoding="utf-8")
    notes.append(f"wrote {lib.ONBOARDING_REL}/inventory.md")
    legacy = lib.load_config(target)["docs"]["legacy_paths"]
    if legacy:
        notes.append(f"registered {len(legacy)} pre-existing docs as legacy (docs.legacy_paths in {lib.CONFIG_REL})")
    install_log = [f"- Added {len(log['added'])} framework files; {len(log['kept'])} already present and left as is.",
                   "- No existing file was overwritten or moved.",
                   f"- {len(legacy)} pre-existing Markdown files registered as legacy in `docs.legacy_paths`: "
                   "checks skip them until reviewed. Remove an entry once the doc has frontmatter and is verified."]
    for rel in log["conflicts"]:
        install_log.append(f"- CONFLICT: existing `{rel}` kept. Framework version saved to "
                           f"`{lib.ONBOARDING_REL}/conflicts/{rel}` for merging.")
    report = onboarding / "migration-report.md"
    if not report.exists():
        text = (target / ".agent/templates/migration-report.template.md").read_text(encoding="utf-8")
        text = (text.replace("{{PROJECT_NAME}}", name).replace("{{DATE}}", datetime.date.today().isoformat())
                .replace("{{INSTALL_LOG}}", "\n".join(install_log)))
        report.write_text(text, encoding="utf-8")
        notes.append(f"wrote {lib.ONBOARDING_REL}/migration-report.md")
    ok = set_project_block(target, f"""{name}: existing codebase being onboarded to the UADR framework.
Onboarding is in progress: follow `.agent/workflows/onboard-existing-repo.md`, starting from `.agent/onboarding/inventory.md`.
Until it completes, trust code over draft docs. Module registry: `.agent/routing/modules.json`.""")
    if not ok:
        notes.append("existing AGENTS.md kept: merge it with the framework version during onboarding")
    return notes


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py adopt", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, help="repository to adopt the framework ('.' for this one)")
    ap.add_argument("--name", help="project name (default: target directory name)")
    ap.add_argument("--description", default="<!-- One-line project description. -->")
    ap.add_argument("--mode", choices=["auto", "greenfield", "existing"], default="auto")
    ap.add_argument("--upgrade", action="store_true",
                    help="replace framework-owned files with this version; project-owned files are kept")
    ap.add_argument("--copy-skills", action="store_true", help="copy skills into adapter folders instead of symlinking")
    args = ap.parse_args(argv)

    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    in_place = target == root.resolve()
    log = {"added": [], "kept": [], "conflicts": [], "upgraded": []}
    # Markdown that predates the framework is registered as legacy: checks skip it until an agent adopts it.
    scope = lib.load_config(root)["docs"]["lint_paths"]
    legacy = [] if in_place or args.upgrade or (target / lib.CONFIG_REL).exists() else [
        p for p in lib.markdown_files(target) if any(lib.glob_match(g, p) for g in scope)]
    inv = scan_cmd.inventory(target)  # taken before installing, so it describes only what was already there
    if not in_place:
        log = copy_framework(root, target, args.upgrade)
    if args.upgrade:
        mine, theirs = target / "AGENTS.md", (root / "AGENTS.md").read_text(encoding="utf-8")
        kept = BLOCK.search(mine.read_text(encoding="utf-8")) if mine.is_file() else None
        if kept:  # framework rules are replaced; the project's own description block is preserved
            mine.write_text(BLOCK.sub(lambda m: kept.group(0), theirs), encoding="utf-8")
        cfg, version = lib.load_config(target), lib.load_config(root)["framework_version"]
        cfg["framework_version"] = version
        lib.write_json(target / lib.CONFIG_REL, cfg)
        print(f"Upgraded {len(log['upgraded'])} framework files to {version}; added {len(log['added'])}; "
              f"project-owned files untouched. Run: python3 .automation/uadr.py check")
        return 0
    if in_place and lib.load_config(target)["project"]["mode"] != "template":
        print("This repository is already initialised. Use --upgrade from a newer framework checkout to update it.")
        return 2

    mode = args.mode
    if mode == "auto":
        mode = "existing" if inv["code_files"] else "greenfield"
    name = args.name or target.name
    configure(target, name, mode, legacy)
    if mode == "greenfield":
        notes = finalize_greenfield(target, name, args.description)
        workflow = "init-greenfield"
    else:
        notes = finalize_existing(target, name, log, inv)
        workflow = "onboard-existing-repo"
    notes += sync_adapters.sync(target, args.copy_skills)
    index_cmd.main([], target)

    print(f"\nUADR adopted in {target} (mode: {mode})")
    print(f"  framework files added: {len(log['added'])}, already present: {len(log['kept'])}, "
          f"conflicts: {len(log['conflicts'])}")
    for note in notes:
        print(f"  {note}")
    for rel in log["conflicts"]:
        print(f"  CONFLICT {rel}: existing file kept, framework version in {lib.ONBOARDING_REL}/conflicts/{rel}")
    print(f"\nNext: open the repository with your coding agent and ask it to follow .agent/workflows/{workflow}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
