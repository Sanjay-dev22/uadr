#!/usr/bin/env python3
"""Mine benchmark tasks from a repository's history, SWE-bench style.

A commit qualifies when it changes source and tests, and the tests it adds or changes
FAIL on the parent's source but PASS on the commit's source. Those tests become the hidden
acceptance tests; the agent is given the parent checkout and a problem statement only.

Usage: mine_tasks.py <repo> --src src/click --tests tests --python <venv python> [--limit 40]
"""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check).stdout


def export(repo: Path, commit: str, dest: Path) -> None:
    dest.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", commit], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive, check=True)


def run_tests(workdir: Path, python: str, pythonpath: str, files: list[str]) -> dict[str, str]:
    """Return {test id: outcome} for the given test files."""
    proc = subprocess.run(
        [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", "--no-header", *files],
        cwd=workdir, capture_output=True, text=True, timeout=900,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": pythonpath, "PYTHONDONTWRITEBYTECODE": "1", "HOME": "/tmp"})
    outcomes = {}
    for line in proc.stdout.splitlines():
        m = re.match(r"(PASSED|FAILED|ERROR)\s+(\S+)", line)
        if m:
            outcomes[m.group(2)] = m.group(1)
    if not outcomes and proc.returncode not in (0, 1):
        outcomes["__collection__"] = "ERROR"
    return outcomes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--src", required=True)
    ap.add_argument("--tests", required=True)
    ap.add_argument("--python", required=True)
    ap.add_argument("--pythonpath", default="src")
    ap.add_argument("--max-src-lines", type=int, default=60)
    ap.add_argument("--limit", type=int, default=40, help="candidates to validate")
    ap.add_argument("--out", default="candidates.json")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    candidates = []
    for sha in git(repo, "log", "--no-merges", "--format=%H", "-n", "1500").split():
        if not git(repo, "rev-parse", "--verify", "-q", sha + "^", check=False).strip():
            continue
        src = tests = 0
        test_files, src_files = [], []
        for row in git(repo, "show", "--numstat", "--format=", sha).splitlines():
            parts = row.split("\t")
            if len(parts) != 3 or parts[0] == "-":
                continue
            lines, path = int(parts[0]) + int(parts[1]), parts[2]
            if path.startswith(args.src + "/"):
                src += lines
                src_files.append(path)
            elif path.startswith(args.tests + "/") and path.endswith(".py"):
                tests += lines
                test_files.append(path)
        if 0 < src <= args.max_src_lines and tests > 0 and len(src_files) <= 3:
            candidates.append({"commit": sha, "src_lines": src, "src_files": src_files, "test_files": test_files})
        if len(candidates) >= args.limit:
            break
    print(f"{len(candidates)} candidate commits; validating...")

    valid = []
    for cand in candidates:
        sha = cand["commit"]
        with tempfile.TemporaryDirectory() as tmp:
            parent, fixed = Path(tmp) / "parent", Path(tmp) / "fixed"
            export(repo, sha + "^", parent)
            export(repo, sha, fixed)
            files = [f for f in cand["test_files"] if (fixed / f).is_file()]
            if not files:
                continue
            for f in files:  # hidden tests overlaid on the unfixed source
                (parent / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(fixed / f, parent / f)
            try:
                before = run_tests(parent, args.python, args.pythonpath, files)
                after = run_tests(fixed, args.python, args.pythonpath, files)
            except subprocess.TimeoutExpired:
                continue
        f2p = sorted(t for t, o in after.items() if o == "PASSED" and before.get(t) != "PASSED")
        p2p = sorted(t for t, o in after.items() if o == "PASSED" and before.get(t) == "PASSED")
        subject = git(repo, "log", "-1", "--format=%s", sha).strip()
        print(f"  {sha[:9]} src={cand['src_lines']:>3} f2p={len(f2p):>3} p2p={len(p2p):>4}  {subject[:70]}")
        if f2p and "__collection__" not in after:
            valid.append({**cand, "parent": git(repo, "rev-parse", sha + "^").strip(), "subject": subject,
                          "date": git(repo, "log", "-1", "--format=%cs", sha).strip(),
                          "fail_to_pass": f2p, "pass_to_pass_count": len(p2p)})
    Path(args.out).write_text(json.dumps(valid, indent=2) + "\n")
    print(f"{len(valid)} validated tasks written to {args.out}")


if __name__ == "__main__":
    main()
