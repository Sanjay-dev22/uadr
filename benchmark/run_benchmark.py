#!/usr/bin/env python3
"""Run the UADR benchmark: the same tasks, the same agent, with and without the framework.

For every task x condition x repetition the harness:
  1. exports the task's parent commit into a fresh workspace with no git history,
  2. applies the condition (bare / minimal AGENTS.md / UADR overlay),
  3. runs a headless agent (`claude -p`) with the problem statement only,
  4. evaluates the result with the hidden tests from the real fix commit,
  5. records exact token usage, cost, turns, tool calls, and change-quality signals.

Conditions:
  bare     the repository as it was, no agent instructions
  minimal  a short hand-written AGENTS.md (layout, test command, conventions)
  uadr     the framework, adopted and onboarded once by an agent at an older commit

Usage:
  run_benchmark.py onboard --suite tasks/click.json --repo <clone> --work <dir>
  run_benchmark.py run     --suite tasks/click.json --repo <clone> --work <dir>
                           [--conditions bare,minimal,uadr] [--reps 2] [--jobs 3] [--only task-id,...]
"""
import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parent
TASK_PROMPT = "Resolve the following in the repository in the current directory.\n\n{statement}\n"
ONBOARD_PROMPT = ("The UADR framework has just been installed in this existing repository. Follow "
                  "`.agent/workflows/onboard-existing-repo.md` from the first step to completion. Register and "
                  "document every real module, configure and run the project commands, and finish the migration "
                  "report. Do not modify any existing project file.")


def sh(cmd, cwd=None, check=True, env=None, timeout=None, input=None):
    return subprocess.run(cmd, cwd=cwd, check=check, env=env, timeout=timeout, input=input,
                          capture_output=True, text=isinstance(input, str) or input is None)


def git(repo, *args, check=True):
    return sh(["git", "-C", str(repo), *args], check=check).stdout


def export(repo: Path, commit: str, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", commit], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive, check=True)


def commit_all(workspace: Path, message: str, tag: str = "") -> None:
    """Fresh single-commit repository. A tag is added for projects that derive their version from git."""
    sh(["git", "init", "-q", "-b", "main"], cwd=workspace)
    sh(["git", "add", "-A"], cwd=workspace)
    sh(["git", "-c", "user.name=bench", "-c", "user.email=bench@example.com", "commit", "-qm", message], cwd=workspace)
    if tag:
        sh(["git", "tag", tag], cwd=workspace)


PATH_PREPEND = ""  # set from --path-prepend: a toolchain directory given to every condition and the evaluator


def tool_env() -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if PATH_PREPEND:
        env["PATH"] = f"{PATH_PREPEND}:{env['PATH']}"
    return env


def agent_env() -> dict:
    return tool_env()  # identical for every condition


def is_test_path(suite: dict, path: str) -> bool:
    return bool(re.search(suite.get("test_pattern", "^" + re.escape(suite.get("tests", "tests")) + "/"), path))


def is_src_path(suite: dict, path: str) -> bool:
    return path.startswith(suite["src"] + "/") and not is_test_path(suite, path)


def run_agent(prompt: str, cwd: Path, model: str, transcript: Path, timeout: int) -> dict:
    """Run a headless agent; store the full event stream; return the final result event."""
    started = time.time()
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", model,
           "--permission-mode", "bypassPermissions"]
    try:
        proc = subprocess.run(cmd, cwd=cwd, env=agent_env(), capture_output=True, text=True, timeout=timeout)
        output = proc.stdout
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        output += json.dumps({"type": "result", "subtype": "harness_timeout", "is_error": True}) + "\n"
    transcript.write_text(output, encoding="utf-8")
    result = {"subtype": "no_result", "is_error": True}
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result = event
    result["wall_seconds"] = round(time.time() - started, 1)
    return result


def analyse_transcript(transcript: Path) -> dict:
    """Derive behaviour metrics from the event stream."""
    tools, reads, commands, message_ids = {}, [], [], set()
    peak_context, first_context, final_text, seen = 0, 0, "", set()
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        message = event.get("message", {})
        message_ids.add(message.get("id"))
        usage = message.get("usage", {})
        context = (usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
                   + usage.get("cache_creation_input_tokens", 0))
        first_context = first_context or context  # system prompt + tools + always-loaded instructions + task
        peak_context = max(peak_context, context)
        for block in message.get("content", []):
            if block.get("type") == "text":
                final_text = block.get("text", "")
            elif block.get("type") == "tool_use" and block.get("id") not in seen:
                seen.add(block.get("id"))
                name = block.get("name", "?")
                tools[name] = tools.get(name, 0) + 1
                data = block.get("input", {})
                if name == "Read":
                    reads.append(data.get("file_path", ""))
                elif name == "Bash":
                    commands.append(data.get("command", ""))
    joined = "\n".join(commands)
    # Agents read files with the Read tool or with shell commands (cat, sed, grep); count both.
    framework_docs = set(re.findall(
        r"(\.agent/(?:workflows|skills|policies|memory|routing)/[\w./-]+|docs/(?:modules|architecture)/[\w-]+\.md)",
        joined + "\n" + "\n".join(reads)))
    return {
        "turns": len(message_ids), "tool_calls": sum(tools.values()), "tools": tools,
        "files_read": len(set(reads)),
        "framework_reads": len(framework_docs),
        "read_workflow": any("/workflows/" in d for d in framework_docs),
        "read_module_doc": any(d.startswith("docs/modules/") for d in framework_docs),
        "read_state": any(d.endswith("memory/state.md") for d in framework_docs),
        "bash_commands": len(commands),
        "ran_tests": bool(re.search(r"pytest|uadr\.py run (test|all)", joined)),
        "used_router": "uadr.py route" in joined,
        "ran_uadr_check": "uadr.py check" in joined,
        "first_context_tokens": first_context, "peak_context_tokens": peak_context,
        "final_message": final_text[-3000:],
        "claims_tests_pass": bool(re.search(r"(?i)(tests?|suite|checks?)\b[^.\n]{0,80}\bpass", final_text)),
    }


def run_pytest(workdir: Path, suite: dict, targets: list[str]) -> dict[str, str]:
    """Run the project's own test command and return {test id: outcome}."""
    proc = subprocess.run([*suite["test_cmd"], "-q", "-p", "no:cacheprovider", "-rA", "--no-header", *targets],
                          cwd=workdir, capture_output=True, text=True, timeout=3600, env=tool_env())
    outcomes = {}
    for line in proc.stdout.splitlines():
        m = re.match(r"(PASSED|FAILED|ERROR)\s+(\S+)", line)
        if m:
            outcomes[m.group(2)] = m.group(1)
    return outcomes


def reference(repo: Path, suite: dict, task: dict, cache: Path) -> dict:
    """Hidden-test ground truth for a task: fail-to-pass tests and the suite's state at the real fix."""
    path = cache / f"{task['id']}.json"
    if path.exists():
        return json.loads(path.read_text())
    commit = git(repo, "rev-parse", task["commit"]).strip()
    test_files = [f for f in git(repo, "show", "--name-only", "--format=", commit).split()
                  if is_test_path(suite, f) and f.endswith(".py")]
    # Projects whose whole suite is too slow to run per evaluation are scored on the changed test files only.
    scope = test_files if suite.get("eval_scope") == "changed_test_files" else [suite["tests"]]
    fixed, parent = cache / "tmp-fixed", cache / "tmp-parent"
    export(repo, commit, fixed)
    export(repo, commit + "^", parent)
    for f in test_files:
        shutil.copy2(fixed / f, parent / f)
    if suite.get("git_tag"):
        commit_all(fixed, "fixed", suite["git_tag"])
        commit_all(parent, "parent", suite["git_tag"])
    after = run_pytest(fixed, suite, scope)
    before = run_pytest(parent, suite, test_files)
    f2p = sorted(t for t in before if after.get(t) == "PASSED" and before[t] != "PASSED")
    f2p += sorted(t for t, o in after.items() if o == "PASSED" and t not in before
                  and t.split("::")[0] in test_files)
    ref_diff = git(repo, "show", "--numstat", "--format=", commit).splitlines()
    src_lines = sum(int(r.split("\t")[0]) + int(r.split("\t")[1]) for r in ref_diff
                    if is_src_path(suite, r.split("\t")[2]) and r.split("\t")[0] != "-")
    data = {"commit": commit, "parent": git(repo, "rev-parse", commit + "^").strip(), "test_files": test_files,
            "eval_targets": scope, "fail_to_pass": sorted(set(f2p)), "passing_at_fix": sorted(t for t, o in after.items() if o == "PASSED"),
            "reference_src_lines": src_lines}
    shutil.rmtree(fixed)
    shutil.rmtree(parent)
    if data["fail_to_pass"]:  # never cache an invalid reference
        path.write_text(json.dumps(data, indent=2))
    return data


def lint_scope_markdown(workspace: Path) -> list[str]:
    cfg = json.loads((workspace / ".automation/configuration/uadr.json").read_text())
    sys.path.insert(0, str(FRAMEWORK / ".automation"))
    import uadr_lib as lib
    return [p for p in lib.markdown_files(workspace) if any(lib.glob_match(g, p) for g in cfg["docs"]["lint_paths"])]


def strip_agent_files(workspace: Path, suite: dict) -> None:
    """Remove the project's own agent instruction files so every condition starts from the same code."""
    for rel in suite.get("strip_files", []):
        path = workspace / rel
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def apply_condition(workspace: Path, condition: str, suite: dict, overlay: Path) -> None:
    strip_agent_files(workspace, suite)
    if condition == "minimal":
        (workspace / "AGENTS.md").write_text(suite["minimal_agents_md"], encoding="utf-8")
        (workspace / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    elif condition.startswith("uadr"):
        before = set(p.relative_to(workspace).as_posix() for p in workspace.rglob("*.md"))
        shutil.copytree(overlay, workspace, dirs_exist_ok=True, symlinks=True)
        # The overlay was onboarded at an older commit. Docs the project added since then are registered as
        # legacy, exactly as adoption at this commit would have done, and the generated index is refreshed.
        cfg_path = workspace / ".automation/configuration/uadr.json"
        cfg = json.loads(cfg_path.read_text())
        overlay_files = {p.relative_to(overlay).as_posix() for p in overlay.rglob("*.md")}
        legacy = set(cfg["docs"].get("legacy_paths", []))
        legacy |= {p for p in lint_scope_markdown(workspace) if p in before and p not in overlay_files}
        cfg["docs"]["legacy_paths"] = sorted(p for p in legacy if (workspace / p).exists())
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
        sh([sys.executable, ".automation/uadr.py", "index"], cwd=workspace)


def change_metrics(workspace: Path, suite: dict) -> dict:
    sh(["git", "add", "-A", "-N"], cwd=workspace, check=False)
    rows = [r.split("\t") for r in git(workspace, "diff", "--numstat", "HEAD").splitlines() if r.count("\t") == 2]
    files = [r[2] for r in rows]
    lines = lambda pred: sum(int(r[0]) + int(r[1]) for r in rows if r[0] != "-" and pred(r[2]))
    is_src = lambda p: is_src_path(suite, p)
    is_test = lambda p: is_test_path(suite, p)
    is_fw = lambda p: p.startswith((".agent/", ".automation/", "docs/modules/", "docs/index.md", "AGENTS.md"))
    return {
        "files_changed": len(files), "src_files_changed": sum(map(is_src, files)),
        "src_lines_changed": lines(is_src), "test_lines_changed": lines(is_test),
        "added_tests": any(map(is_test, files)),
        "updated_changelog": any(Path(p).name.upper().startswith("CHANGES") for p in files),
        "updated_project_docs": any(p.startswith("docs/") and not is_fw(p) for p in files),
        "updated_framework_docs": any(is_fw(p) for p in files),
        "other_files": [p for p in files if not (is_src(p) or is_test(p) or is_fw(p) or p.startswith("docs/")
                                                 or Path(p).name.upper().startswith("CHANGES"))],
    }


def evaluate(workspace: Path, repo: Path, suite: dict, ref: dict, scratch: Path) -> dict:
    """Overlay the hidden tests from the real fix and run the whole suite."""
    if scratch.exists():
        shutil.rmtree(scratch)
    shutil.copytree(workspace, scratch, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))
    for f in ref["test_files"]:
        content = subprocess.run(["git", "-C", str(repo), "show", f"{ref['commit']}:{f}"],
                                 capture_output=True, check=True).stdout
        (scratch / f).parent.mkdir(parents=True, exist_ok=True)
        (scratch / f).write_bytes(content)
    if suite.get("git_tag"):
        commit_all(scratch, "evaluation", suite["git_tag"])
    outcomes = run_pytest(scratch, suite, ref.get("eval_targets", [suite["tests"]]))
    shutil.rmtree(scratch)
    f2p_failed = [t for t in ref["fail_to_pass"] if outcomes.get(t) != "PASSED"]
    regressions = [t for t in ref["passing_at_fix"] if t not in ref["fail_to_pass"] and outcomes.get(t) != "PASSED"]
    return {"resolved": not f2p_failed and not regressions,
            "fail_to_pass_total": len(ref["fail_to_pass"]), "fail_to_pass_failed": len(f2p_failed),
            "regressions": len(regressions), "regression_examples": regressions[:5]}


def usage_summary(result: dict) -> dict:
    """Token totals come from modelUsage (cumulative, matches the reported cost). The top-level `usage` field
    can describe only part of a run, so it is used only when modelUsage is absent."""
    models = result.get("modelUsage") or {}
    if models:
        fresh = sum(m.get("inputTokens", 0) for m in models.values())
        write = sum(m.get("cacheCreationInputTokens", 0) for m in models.values())
        read = sum(m.get("cacheReadInputTokens", 0) for m in models.values())
        output = sum(m.get("outputTokens", 0) for m in models.values())
    else:
        usage = result.get("usage", {})
        fresh, write, read = (usage.get("input_tokens", 0), usage.get("cache_creation_input_tokens", 0),
                              usage.get("cache_read_input_tokens", 0))
        output = usage.get("output_tokens", 0)
    return {"input_tokens_uncached": fresh, "cache_write_tokens": write, "cache_read_tokens": read,
            "output_tokens": output, "total_input_tokens": fresh + write + read,
            "cost_usd": result.get("total_cost_usd", 0), "turns": result.get("num_turns", 0),
            "api_seconds": round(result.get("duration_api_ms", 0) / 1000, 1),
            "wall_seconds": result.get("wall_seconds", 0),
            "finished": result.get("subtype") == "success" and not result.get("is_error")}


def run_one(job: dict) -> dict:
    out = Path(job["out"])
    if out.exists():
        return json.loads(out.read_text())
    suite, task, ref = job["suite"], job["task"], job["ref"]
    repo, work = Path(job["repo"]), Path(job["work"])
    run_id = f"{task['id']}__{job['condition']}__r{job['rep']}"
    workspace = work / "workspaces" / run_id
    export(repo, ref["parent"], workspace)
    apply_condition(workspace, job["condition"], suite, work / f"{job['condition']}-overlay")
    commit_all(workspace, "benchmark baseline", suite.get("git_tag", ""))
    transcript = out.with_suffix(".transcript.jsonl")
    result = run_agent(TASK_PROMPT.format(statement=task["statement"]), workspace, job["model"],
                       transcript, job["timeout"])
    if not usage_summary(result)["finished"]:  # usage limit, timeout, crash: not a measurement of the agent
        print(f"  {run_id:<52} INTERRUPTED ({result.get('subtype')}); not recorded, rerun to retry", flush=True)
        return {"run": run_id, "interrupted": True}
    record = {"run": run_id, "task": task["id"], "type": task["type"], "condition": job["condition"],
              "rep": job["rep"], "model": job["model"], **usage_summary(result), **analyse_transcript(transcript),
              **change_metrics(workspace, suite),
              **evaluate(workspace, repo, suite, ref, work / "eval" / run_id),
              "reference_src_lines": ref["reference_src_lines"]}
    out.write_text(json.dumps(record, indent=2))
    print(f"  {run_id:<52} resolved={record['resolved']!s:<5} ${record['cost_usd']:.2f} "
          f"{record['total_input_tokens']:>9} in  {record['turns']:>3} turns", flush=True)
    return record


def cmd_onboard(args, suite) -> None:
    repo, work = Path(args.repo).resolve(), Path(args.work).resolve()
    workspace = work / "onboarding"
    export(repo, suite["onboard_commit"], workspace)
    strip_agent_files(workspace, suite)
    commit_all(workspace, "project at onboarding commit", suite.get("git_tag", ""))
    adopt = sh([sys.executable, str(FRAMEWORK / ".automation/uadr.py"), "adopt", "--target", str(workspace)])
    print(adopt.stdout[-600:])
    result = run_agent(ONBOARD_PROMPT, workspace, args.model, work / "onboarding.transcript.jsonl",
                       args.timeout)
    if not usage_summary(result)["finished"]:
        raise SystemExit(f"onboarding did not finish ({result.get('subtype')}); nothing saved. Rerun.")
    status = git(workspace, "status", "--porcelain", "-uall").splitlines()
    modified = [s[3:] for s in status if not s.startswith("??")]
    overlay = work / "uadr-overlay"
    if overlay.exists():
        shutil.rmtree(overlay)
    for rel in [s[3:] for s in status if s.startswith("??")]:
        if "__pycache__" in rel or ".pytest_cache" in rel:
            continue
        src, dest = workspace / rel, overlay / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_symlink():
            os.symlink(os.readlink(src), dest)
        else:
            shutil.copy2(src, dest)
    check = sh([sys.executable, ".automation/uadr.py", "check"], cwd=workspace, check=False)
    audit = sh([sys.executable, ".automation/uadr.py", "audit", "--json"], cwd=workspace, check=False)
    record = {"model": args.model, **usage_summary(result), **analyse_transcript(work / "onboarding.transcript.jsonl"),
              "existing_files_modified": modified, "overlay_files": sum(1 for p in overlay.rglob("*") if p.is_file()),
              "check_exit": check.returncode, "check_tail": check.stdout[-1500:],
              "audit": json.loads(audit.stdout) if audit.returncode == 0 else None}
    (work / "onboarding.json").write_text(json.dumps(record, indent=2))
    print(json.dumps({k: record[k] for k in ("cost_usd", "total_input_tokens", "output_tokens", "turns",
                                             "wall_seconds", "existing_files_modified", "check_exit")}, indent=2))
    print(check.stdout[-800:])


def cmd_run(args, suite) -> None:
    repo, work = Path(args.repo).resolve(), Path(args.work).resolve()
    results, cache = work / "results", work / "reference"
    results.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    tasks = [t for t in suite["tasks"] if not args.only or t["id"] in args.only.split(",")]
    jobs = []
    for task in tasks:
        ref = reference(repo, suite, task, cache)
        print(f"{task['id']}: {len(ref['fail_to_pass'])} hidden fail-to-pass tests, "
              f"{len(ref['passing_at_fix'])} suite tests, reference fix {ref['reference_src_lines']} source lines")
        if not ref["fail_to_pass"]:
            raise SystemExit(f"{task['id']}: no fail-to-pass tests; task is not valid")
        for rep in range(1, args.reps + 1):
            for condition in args.conditions.split(","):
                jobs.append({"suite": suite, "task": task, "ref": ref, "condition": condition, "rep": rep,
                             "repo": str(repo), "work": str(work), "model": args.model,
                             "timeout": args.timeout,
                             "out": str(results / f"{task['id']}__{condition}__r{rep}.json")})
    print(f"{len(jobs)} runs, {args.jobs} in parallel")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(run_one, jobs))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["onboard", "run"])
    ap.add_argument("--suite", required=True)
    ap.add_argument("--repo", required=True, help="local clone with history")
    ap.add_argument("--work", required=True, help="scratch directory for workspaces and results")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--conditions", default="bare,minimal,uadr")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only", help="comma-separated task ids")
    ap.add_argument("--timeout", type=int, default=2400, help="seconds per agent run")
    ap.add_argument("--path-prepend", default="", help="directory put first on PATH for agents and the evaluator")
    args = ap.parse_args()
    global PATH_PREPEND
    PATH_PREPEND = args.path_prepend
    suite = json.loads(Path(args.suite).read_text())
    (cmd_onboard if args.command == "onboard" else cmd_run)(args, suite)


if __name__ == "__main__":
    main()
