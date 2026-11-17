#!/usr/bin/env python3
"""Aggregate benchmark run records into a Markdown report and a compact JSON data file.

Usage: report.py --work <dir> --suite tasks/click.json --out results/click
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_benchmark import analyse_transcript, usage_summary

ORDER = ["bare", "minimal"]


def mean(values):
    values = list(values)
    return statistics.fmean(values) if values else 0.0


def pct(values):
    values = list(values)
    return f"{100 * sum(map(bool, values)) / len(values):.0f}%" if values else "-"


def fmt(n):
    return f"{n:,.0f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--suite", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    work = Path(args.work)
    suite = json.loads(Path(args.suite).read_text())
    records = []
    for path in sorted((work / "results").glob("*.json")):
        record = json.loads(path.read_text())
        if record.get("interrupted") or not record.get("finished", True):
            continue
        transcript = path.with_suffix(".transcript.jsonl")
        final = {}
        for line in transcript.read_text(encoding="utf-8").splitlines():
            if '"type":"result"' in line.replace(" ", ""):
                try:
                    final = json.loads(line)
                except json.JSONDecodeError:
                    pass
        if final:  # token totals from modelUsage, wall time as measured by the harness
            record.update(usage_summary({**final, "wall_seconds": record["wall_seconds"]}))
        record.update(analyse_transcript(transcript))  # refresh derived metrics, including turns
        records.append(record)
    onboarding = json.loads((work / "onboarding.json").read_text()) if (work / "onboarding.json").exists() else None
    present = {r["condition"] for r in records}
    conditions = [c for c in ORDER if c in present] + sorted(present - set(ORDER))
    frameworks = [c for c in conditions if c.startswith("uadr")]
    tasks = [t["id"] for t in suite["tasks"] if any(r["task"] == t["id"] for r in records)]
    by = lambda c, t=None: [r for r in records if r["condition"] == c and (t is None or r["task"] == t)]
    model = records[0]["model"] if records else "?"

    out = [f"# Benchmark results: {suite['repo'].split('/')[-1]}\n",
           f"Repository: {suite['repo']}. Agent: `claude -p` (Claude Code headless), model `{model}`. "
           f"{len(tasks)} tasks x {len(conditions)} conditions, {len(records)} runs. "
           "Success is decided by hidden tests taken from the real upstream fix. Token and cost figures are the "
           "exact values reported by the API, summed over every model call in a run.\n",
           "\n## Summary by condition\n",
           "| Metric | " + " | ".join(conditions) + " |", "| --- |" + " ---: |" * len(conditions)]

    def row(label, fn):
        out.append(f"| {label} | " + " | ".join(fn(by(c)) for c in conditions) + " |")

    row("Runs", lambda rs: str(len(rs)))
    row("Resolved (hidden tests pass, no regressions)", lambda rs: f"{sum(r['resolved'] for r in rs)}/{len(rs)}")
    row("Runs with regressions", lambda rs: str(sum(r["regressions"] > 0 for r in rs)))
    row("Mean cost per run (USD)", lambda rs: f"{mean(r['cost_usd'] for r in rs):.3f}")
    row("Mean total input tokens (all calls)", lambda rs: fmt(mean(r["total_input_tokens"] for r in rs)))
    row("  of which cache reads", lambda rs: fmt(mean(r["cache_read_tokens"] for r in rs)))
    row("  of which cache writes", lambda rs: fmt(mean(r["cache_write_tokens"] for r in rs)))
    row("Mean output tokens", lambda rs: fmt(mean(r["output_tokens"] for r in rs)))
    row("Context at first model call (tokens)", lambda rs: fmt(mean(r["first_context_tokens"] for r in rs)))
    row("Peak context (tokens)", lambda rs: fmt(mean(r["peak_context_tokens"] for r in rs)))
    row("Mean turns", lambda rs: f"{mean(r['turns'] for r in rs):.1f}")
    row("Mean tool calls", lambda rs: f"{mean(r['tool_calls'] for r in rs):.1f}")
    row("Mean model (API) time (s)", lambda rs: f"{mean(r['api_seconds'] for r in rs):.0f}")
    row("Mean wall time (s), includes environment stalls", lambda rs: f"{mean(r['wall_seconds'] for r in rs):.0f}")
    row("Ran tests itself", lambda rs: pct(r["ran_tests"] for r in rs))
    row("Added or changed tests", lambda rs: pct(r["added_tests"] for r in rs))
    row("Updated changelog", lambda rs: pct(r["updated_changelog"] for r in rs))
    row("Updated project docs", lambda rs: pct(r["updated_project_docs"] for r in rs))
    row("Source lines changed / reference fix", lambda rs: f"{mean(r['src_lines_changed'] / max(r['reference_src_lines'], 1) for r in rs):.2f}x")
    row("Touched files outside source, tests, docs, changelog", lambda rs: pct(bool(r["other_files"]) for r in rs))
    for fw in frameworks:
        u = by(fw)
        out += ["", f"Framework adherence in `{fw}`: read project state in {pct(r['read_state'] for r in u)} of runs, "
                    f"used the router in {pct(r['used_router'] for r in u)}, opened the workflow in "
                    f"{pct(r['read_workflow'] for r in u)}, opened a module doc in {pct(r['read_module_doc'] for r in u)}, "
                    f"ran `uadr.py check` in {pct(r['ran_uadr_check'] for r in u)}."]

    out += ["\n## Per task (mean over repetitions)\n",
            "| Task | Type | " + " | ".join(f"{c}: resolved" for c in conditions) + " | "
            + " | ".join(f"{c}: cost" for c in conditions) + " | "
            + " | ".join(f"{c}: input tok" for c in conditions) + " |",
            "| --- | --- |" + " ---: |" * (3 * len(conditions))]
    for t in tasks:
        kind = next(x["type"] for x in suite["tasks"] if x["id"] == t)
        out.append(f"| {t} | {kind} | "
                   + " | ".join(f"{sum(r['resolved'] for r in by(c, t))}/{len(by(c, t))}" for c in conditions) + " | "
                   + " | ".join(f"${mean(r['cost_usd'] for r in by(c, t)):.2f}" for c in conditions) + " | "
                   + " | ".join(fmt(mean(r["total_input_tokens"] for r in by(c, t))) for c in conditions) + " |")

    if frameworks:
        out.append("\n## Framework versus baselines (paired by task)\n")
        out += ["| Framework | Compared with | Cost | Total input tokens | Output tokens | Turns | Tasks where framework was cheaper |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
        for fw in frameworks:
            for base in [c for c in conditions if c != fw and not (c.startswith("uadr") and c > fw)]:
                def ratio(key):
                    pairs = [(mean(r[key] for r in by(fw, t)), mean(r[key] for r in by(base, t))) for t in tasks
                             if by(fw, t) and by(base, t)]
                    return mean(u / b for u, b in pairs if b), sum(u < b for u, b in pairs), len(pairs)
                cost, cheaper, n = ratio("cost_usd")
                out.append(f"| {fw} | {base} | {cost - 1:+.0%} | {ratio('total_input_tokens')[0] - 1:+.0%} | "
                           f"{ratio('output_tokens')[0] - 1:+.0%} | {ratio('turns')[0] - 1:+.0%} | {cheaper}/{n} |")
        out.append("\nValues are the mean of per-task ratios (framework / baseline - 1). Positive means the framework used more.")

    if onboarding:
        out += ["\n## One-time onboarding cost\n",
                f"The framework condition requires onboarding the repository once. Measured for this repository with the same model: "
                f"**${onboarding['cost_usd']:.2f}**, {fmt(onboarding['total_input_tokens'])} input tokens, "
                f"{fmt(onboarding['output_tokens'])} output tokens, {onboarding['turns']} turns, "
                f"{onboarding['wall_seconds'] / 60:.0f} minutes. Existing project files modified: "
                f"{len(onboarding['existing_files_modified'])}. `uadr.py check` exit code afterwards: {onboarding['check_exit']}."]
        for fw in frameworks:
            for base in [c for c in conditions if not c.startswith("uadr")]:
                saving = mean(r["cost_usd"] for r in by(base)) - mean(r["cost_usd"] for r in by(fw))
                if saving > 0:
                    out.append(f"\n`{fw}` against `{base}`: saves ${saving:.3f} per task on average, so onboarding "
                               f"pays for itself after about {onboarding['cost_usd'] / saving:.0f} tasks.")
                else:
                    out.append(f"\n`{fw}` against `{base}`: costs ${-saving:.3f} more per task on average, so "
                               f"onboarding is not recovered through token savings on tasks of this kind.")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out + ".md").write_text("\n".join(out) + "\n")
    compact = [{k: v for k, v in r.items() if k not in ("final_message",)} for r in records]
    if onboarding:
        onboarding = {k: v for k, v in onboarding.items() if k not in ("final_message", "check_tail", "audit")}
    Path(args.out + ".json").write_text(json.dumps({"suite": suite["repo"], "model": model, "onboarding": onboarding,
                                                    "runs": compact}, indent=2) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
