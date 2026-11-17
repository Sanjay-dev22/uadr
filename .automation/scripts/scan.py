"""Inventory a repository: languages, manifests, entry points, module candidates, tests, pipelines, docs.

Everything reported is a CANDIDATE found by file patterns. The onboarding agent must verify each
item against the code before documenting it.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import uadr_lib as lib

LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".java": "Java", ".kt": "Kotlin", ".cs": "C#", ".go": "Go", ".rs": "Rust",
    ".rb": "Ruby", ".php": "PHP", ".swift": "Swift", ".c": "C", ".h": "C/C++", ".cpp": "C++", ".cc": "C++",
    ".scala": "Scala", ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir", ".vue": "Vue", ".sh": "Shell",
    ".sql": "SQL", ".fs": "F#", ".vb": "Visual Basic", ".lua": "Lua", ".r": "R", ".m": "Objective-C",
}
MANIFESTS = {
    "package.json": "Node.js", "pyproject.toml": "Python", "requirements.txt": "Python", "setup.py": "Python",
    "Pipfile": "Python", "pom.xml": "Maven (JVM)", "build.gradle": "Gradle (JVM)", "build.gradle.kts": "Gradle (JVM)",
    "go.mod": "Go", "Cargo.toml": "Rust", "Gemfile": "Ruby", "composer.json": "PHP", "pubspec.yaml": "Dart",
    "mix.exs": "Elixir", "Package.swift": "Swift", "CMakeLists.txt": "CMake", "Makefile": "Make",
}
MANIFEST_SUFFIXES = {".csproj": ".NET", ".fsproj": ".NET", ".sln": ".NET"}
FRAMEWORK_HINTS = [
    "react", "next", "vue", "angular", "svelte", "express", "nestjs", "fastify", "django", "flask", "fastapi",
    "spring-boot", "quarkus", "rails", "laravel", "symfony", "gin-gonic", "actix", "Microsoft.AspNetCore",
    "pytest", "jest", "vitest", "mocha", "junit", "xunit", "nunit", "playwright", "cypress", "rspec",
    "sqlalchemy", "prisma", "typeorm", "hibernate", "EntityFramework", "mongoose", "sequelize", "psycopg",
    "mysql", "postgres", "sqlite", "redis", "kafka", "rabbitmq", "graphql", "grpc", "celery", "boto3", "aws-sdk",
]
ENTRY_NAMES = {
    "main.py", "__main__.py", "app.py", "manage.py", "wsgi.py", "asgi.py", "server.js", "server.ts", "index.js",
    "index.ts", "main.js", "main.ts", "app.js", "app.ts", "main.go", "main.rs", "Program.cs", "Main.java",
    "main.kt", "Main.kt", "main.c", "main.cpp", "Procfile", "Startup.cs",
}
CONTAINERS = ["src", "app", "apps", "packages", "services", "modules", "lib", "libs", "cmd", "internal", "pkg",
              "components", "projects"]
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs", "e2e"}
TEST_FILE = re.compile(r"(^test_.*\.py$|_test\.(py|go)$|\.(test|spec)\.[jt]sx?$|Tests?\.(java|cs|kt)$|_spec\.rb$)")
CI_FILES = ["azure-pipelines.yml", "azure-pipelines.yaml", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml",
            "bitbucket-pipelines.yml", ".travis.yml"]
INSTRUCTION_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursorrules",
                     ".windsurfrules"]
FRAMEWORK_PREFIXES = (".agent/", ".automation/", ".agents/", ".claude/skills", "docs/templates/")
COMMAND_HINTS = {
    "go.mod": {"build": "go build ./...", "test": "go test ./...", "static": "go vet ./..."},
    "Cargo.toml": {"build": "cargo build", "test": "cargo test", "lint": "cargo clippy"},
    "pom.xml": {"build": "mvn -q -DskipTests package", "test": "mvn -q test"},
    "build.gradle": {"build": "./gradlew assemble", "test": "./gradlew test"},
    "build.gradle.kts": {"build": "./gradlew assemble", "test": "./gradlew test"},
    "Gemfile": {"test": "bundle exec rake test"},
    "composer.json": {"test": "composer test"},
}


def read(root: Path, rel: str, limit: int = 200_000) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def inventory(root: Path) -> dict:
    files = [f for f in lib.list_files(root) if not f.startswith(FRAMEWORK_PREFIXES)]
    if (root / lib.CONFIG_REL).is_file():  # already adopted: framework-managed files are not project findings
        managed = lib.load_config(root).get("framework_paths", [])
        files = [f for f in files if not any(lib.glob_match(g, f) for g in managed)]
    code = [f for f in files if Path(f).suffix.lower() in LANGUAGES]
    languages = Counter(LANGUAGES[Path(f).suffix.lower()] for f in code)

    manifests = [f for f in files if Path(f).name in MANIFESTS or Path(f).suffix in MANIFEST_SUFFIXES]
    frameworks: dict[str, list[str]] = {}
    commands: dict[str, list[str]] = {}

    def suggest(kind: str, command: str, source: str) -> None:
        commands.setdefault(kind, [])
        entry = f"`{command}` (from {source})"
        if entry not in commands[kind]:
            commands[kind].append(entry)

    for rel in manifests:
        text, name = read(root, rel), Path(rel).name
        for hint in FRAMEWORK_HINTS:
            if re.search(r"(?<![\w-])" + re.escape(hint) + r"(?![\w])", text, re.IGNORECASE):
                frameworks.setdefault(hint, []).append(rel)
        prefix = "" if "/" not in rel else f"(cd {Path(rel).parent.as_posix()} && "
        suffix = "" if not prefix else ")"
        for kind, command in COMMAND_HINTS.get(name, {}).items():
            suggest(kind, f"{prefix}{command}{suffix}", rel)
        if name in ("pyproject.toml", "requirements.txt", "setup.py"):
            runner = "pytest" if re.search(r"\bpytest\b", text) else "unittest discover"
            suggest("test", f"{prefix}python -m {runner}{suffix}", rel)
        if Path(rel).suffix in MANIFEST_SUFFIXES:
            suggest("build", "dotnet build", rel)
            suggest("test", "dotnet test", rel)
        if name == "package.json":
            try:
                scripts = json.loads(text).get("scripts", {})
            except (json.JSONDecodeError, AttributeError):
                scripts = {}
            for kind, script in (("build", "build"), ("test", "test"), ("lint", "lint"), ("static", "typecheck")):
                if script in scripts:
                    suggest(kind, f"{prefix}npm run {script}{suffix}", rel)
        if name == "Makefile":
            targets = set(re.findall(r"^([A-Za-z][\w-]*):", text, re.MULTILINE))
            for kind in ("build", "test", "lint"):
                if kind in targets:
                    suggest(kind, f"{prefix}make {kind}{suffix}", rel)

    entries = [f for f in files if Path(f).name in ENTRY_NAMES or re.search(r"Application\.(java|kt)$", f)]
    entries = sorted(entries, key=lambda f: (f.count("/"), f))[:30]

    candidates: dict[str, dict] = {}

    def add_candidate(path: str, reason: str) -> None:
        inside = [f for f in code if f.startswith(path + "/")]
        if inside and path not in candidates:
            candidates[path] = {
                "code_files": len(inside), "reason": reason,
                "has_tests": any(TEST_FILE.search(Path(f).name) or TEST_DIRS & set(f.split("/")) for f in inside),
            }

    for rel in manifests:
        if "/" in rel:
            add_candidate(Path(rel).parent.as_posix(), f"own manifest {Path(rel).name}")
    for container in CONTAINERS:
        children = sorted({f.split("/")[1] for f in code if f.startswith(container + "/") and f.count("/") >= 2})
        for child in children:
            if child not in TEST_DIRS:
                add_candidate(f"{container}/{child}", f"directory under {container}/")
    for path in list(candidates):  # a single wrapping package: its sub-packages are the likelier modules
        children = sorted({f[len(path) + 1:].split("/")[0] for f in code
                           if f.startswith(path + "/") and f[len(path) + 1:].count("/") >= 1})
        children = [c for c in children if c not in TEST_DIRS]
        if len(children) >= 2:
            for child in children:
                add_candidate(f"{path}/{child}", f"sub-package of {path}/")
    if not candidates:
        for top in sorted({f.split("/")[0] for f in code if "/" in f}):
            if top not in TEST_DIRS:
                add_candidate(top, "top-level directory with code")

    test_files = [f for f in files if TEST_FILE.search(Path(f).name) or TEST_DIRS & set(f.split("/")[:-1])]
    test_roots = Counter("/".join(f.split("/")[: next((i for i, p in enumerate(f.split("/")) if p in TEST_DIRS), 0) + 1])
                         for f in test_files if TEST_DIRS & set(f.split("/")[:-1]))

    pick = lambda pattern: [f for f in files if re.search(pattern, f, re.IGNORECASE)]
    ci = [f for f in files if f.startswith(".github/workflows/") and f != ".github/workflows/uadr-checks.yml"]
    ci += [f for f in CI_FILES if f in files]
    ci_commands = []
    for rel in ci:
        for match in re.findall(r"^\s*(?:-\s*)?(?:run|script|sh):\s*(?![|>])(.+)$", read(root, rel), re.MULTILINE):
            command = match.strip().strip("'\"")
            if command and command not in ci_commands:
                ci_commands.append(command)
    docs = [f for f in files if f.lower().endswith((".md", ".rst", ".adoc")) and not f.startswith(".github/")]
    todo = 0
    for f in code[:3000]:
        todo += len(re.findall(r"\b(TODO|FIXME|HACK|XXX)\b", read(root, f, 100_000)))

    inv = {
        "root": root.name, "total_files": len(files), "code_files": len(code),
        "languages": dict(languages.most_common()),
        "manifests": {f: MANIFESTS.get(Path(f).name) or MANIFEST_SUFFIXES.get(Path(f).suffix) for f in manifests},
        "framework_hints": frameworks, "entry_point_candidates": entries, "module_candidates": candidates,
        "tests": {"files": len(test_files), "roots": dict(test_roots.most_common(15))},
        "ci": ci, "ci_commands": ci_commands[:20],
        "infrastructure": pick(r"(^|/)(Dockerfile[^/]*|docker-compose[^/]*\.ya?ml|[^/]+\.tf|Chart\.yaml|serverless\.ya?ml|"
                               r"kustomization\.ya?ml)$")[:30],
        "data": pick(r"(^|/)(migrations?|alembic|db/migrate)/|schema\.(prisma|rb|sql)$|\.sql$|liquibase")[:30],
        "api_contracts": pick(r"(openapi|swagger)[^/]*\.(ya?ml|json)$|\.proto$|\.graphqls?$")[:30],
        "docs": docs[:60], "docs_total": len(docs),
        "instruction_files": [f for f in INSTRUCTION_FILES if f in files] + pick(r"^\.cursor/rules/"),
        "env_files": pick(r"(^|/)\.env(\.[\w-]+)?$"),
        "suggested_commands": commands, "debt_markers": todo,
    }
    gaps = []
    if not test_files:
        gaps.append("No automated tests detected.")
    if not ci:
        gaps.append("No CI pipeline detected.")
    if not any(Path(f).name.lower().startswith("readme") for f in files):
        gaps.append("No README.")
    if not [d for d in docs if d.startswith("docs/")]:
        gaps.append("No docs/ directory content.")
    if [e for e in inv["env_files"] if not e.endswith((".example", ".sample", ".template"))]:
        gaps.append("Environment files are present in the tree: confirm they are untracked and contain no secrets "
                    "(do not open them).")
    if not manifests:
        gaps.append("No dependency manifest detected: build and dependency tooling is UNKNOWN.")
    inv["gaps"] = gaps
    return inv


def render(inv: dict) -> str:
    def bullets(items, empty="None detected."):
        return "\n".join(f"- `{i}`" for i in items) if items else empty

    lang = "\n".join(f"| {name} | {count} |" for name, count in inv["languages"].items()) or "| none | 0 |"
    mods = "\n".join(f"| `{path}` | {m['code_files']} | {'yes' if m['has_tests'] else 'no'} | {m['reason']} |"
                     for path, m in inv["module_candidates"].items()) or "| none | | | |"
    frameworks = "\n".join(f"- {name} (mentioned in {', '.join(f'`{s}`' for s in sorted(set(src))[:3])})"
                           for name, src in sorted(inv["framework_hints"].items())) or "None detected."
    commands = "\n".join(f"- {kind}: {'; '.join(cands)}" for kind, cands in inv["suggested_commands"].items()) \
        or "None derived. Find the commands in build files or CI."
    manifests = "\n".join(f"- `{f}` ({kind})" for f, kind in inv["manifests"].items()) or "None detected."
    tests = "\n".join(f"- `{root}/` ({count} files)" for root, count in inv["tests"]["roots"].items())
    return f"""# Repository inventory: {inv['root']}

Generated by `python3 .automation/uadr.py scan`. Every item is a candidate found by file patterns, not a verified
fact. Verify against the code before documenting. Regenerate instead of editing.

Files: {inv['total_files']} total, {inv['code_files']} source. Debt markers (TODO/FIXME/HACK): {inv['debt_markers']}.

## Languages

| Language | Files |
| --- | --- |
{lang}

## Dependency manifests

{manifests}

## Framework and library hints

{frameworks}

## Entry point candidates

{bullets(inv['entry_point_candidates'])}

## Module candidates

Register real modules with `python3 .automation/uadr.py new module <name> --paths <path>/**`.

| Path | Source files | Tests inside | Why suggested |
| --- | --- | --- | --- |
{mods}

## Tests

Test files detected: {inv['tests']['files']}.

{tests}

## Candidate project commands

Verify each by running it, then set `commands` in `.automation/configuration/uadr.json`.

{commands}

## CI pipelines

{bullets(inv['ci'])}

Commands the pipelines run (the most reliable source for project commands):

{bullets(inv['ci_commands'], 'None extracted.')}

## Infrastructure and deployment files

{bullets(inv['infrastructure'])}

## Data stores and migrations

{bullets(inv['data'])}

## API contracts

{bullets(inv['api_contracts'])}

## Existing documentation ({inv['docs_total']} files)

{bullets(inv['docs'])}

## Existing agent instruction files

{bullets(inv['instruction_files'])}

## Gaps and risks detected

{chr(10).join('- ' + g for g in inv['gaps']) or 'None detected by pattern scan.'}
"""


def main(argv: list[str], root: Path = lib.ROOT) -> int:
    ap = argparse.ArgumentParser(prog="uadr.py scan", description=__doc__)
    ap.add_argument("--target", help="repository to scan (default: this repository)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing the inventory file")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    target = Path(args.target).resolve() if args.target else root
    inv = inventory(target)
    if args.json:
        print(json.dumps(inv, indent=2))
    elif args.stdout:
        print(render(inv))
    else:
        out = target / lib.ONBOARDING_REL / "inventory.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(inv), encoding="utf-8")
        print(f"wrote {out.relative_to(target).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
