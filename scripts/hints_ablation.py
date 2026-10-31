"""Hints ablation on the held-out test set: system 3 with and without the per-task-type hints.

System 3 (crmroute, every task on Gemini 3.8 Flash) ran again on the 194 test tasks with the test run's
pins and CRMROUTE_TASK_HINTS=0, in the image the test numbers come from with only that flag added
(deploy/hints_ablation.Dockerfile). It ran after the test run; nothing was tuned or changed because of it.

Reads the run records in runs/ (git-ignored) and writes a markdown report: the standard summary from
analyze_results.py, the paired comparisons with both ReAct baselines (measured, and with every capped
baseline task counted as a success, as in robustness_checks.py), a per-task-type breakdown and the spend.

Usage:  python scripts/hints_ablation.py --out results/ablation_hints.md
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_results import expected_keys, load_system, validate_complete  # noqa: E402
from robustness_checks import GROUPS, capped, group_of, logged_cost, paired, pct, success  # noqa: E402


def record_cost(run_dir: Path) -> float:
    """The task records' spend, failed attempts included (as robustness_checks.spend_section counts it)."""
    cost = 0.0
    for f in sorted(run_dir.rglob("results_*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            for attempt in [r, *(r.get("previous_attempts") or [])]:
                cost += float((attempt.get("agent_info") or {}).get("total_cost") or 0.0)
                cost += sum(float(c.get("cost") or 0.0) for c in attempt.get("llm_calls") or []
                            if c.get("role") in ("judge", "user"))
    return cost


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--task-ids", type=Path, default=Path("data/test.json"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    test_dir, ablation_dir = args.runs / "test", args.runs / "ablation_hints"
    paths = {"react": test_dir / "react", "react_privacy": test_dir / "react_privacy",
             "full": test_dir / "full", "full_nohints": ablation_dir / "full_nohints"}
    wanted = expected_keys(args.task_ids)
    runs = {name: load_system(path) for name, path in paths.items()}
    validate_complete(runs, wanted)
    runs = {name: {k: rows[k] for k in wanted} for name, rows in runs.items()}
    keys = sorted(wanted)

    summary_cmd = ["scripts/analyze_results.py", "--system", f"full={paths['full'].as_posix()}",
                   "--system", f"full_nohints={paths['full_nohints'].as_posix()}", "--baseline", "full",
                   "--task-ids", args.task_ids.as_posix(), "--big-model", "3.8-flash"]
    script = Path(__file__).parent / "analyze_results.py"  # runs from any directory; the command shown stays relative
    summary = subprocess.run([sys.executable, str(script), *summary_cmd[1:]], check=True, capture_output=True,
                             text=True, encoding="utf-8").stdout.strip()

    lines = ["# Hints ablation on the held-out test set", "",
             "System 3 (crmroute, every task on Gemini 3.8 Flash) with the per-task-type hints left out of the solver "
             "prompt (`CRMROUTE_TASK_HINTS=0`): the 25 `TaskSpec.hints` lines over the 19 business task types in "
             "`agent/app/task_specs.py`. The router's task goal, the answer form, the details to ask for, the general "
             "rules and the checker stay, so this measures the per-type hints only, not all of the dev tuning.", "",
             "It ran on the 194 test tasks after the test run, with the test run's pins (models, thinking level, eval "
             "mode, judge and simulated user, task ids, turn limits; `runs/ablation_hints/manifest_*.json`), in "
             "`crmroute:nohints`: the test image (`0374d9c6e7b7`, commit `7beda40`) with only `agent/app/config.py` "
             "and `agent/app/prompts.py` replaced (`deploy/hints_ablation.Dockerfile`). The harness patch has two "
             "changes since the test run, neither of which affects CRMArena-Pro scoring: it copies the agent's last "
             "answer check into the run record, and it wraps single-string answers, which only the original CRMArena "
             "org has. Nothing was tuned or changed because of this run.", "",
             "```", "python scripts/hints_ablation.py --out results/ablation_hints.md",
             "python " + " ".join(summary_cmd), "```", "",
             "## Summary (`analyze_results.py`)", "", summary, "",
             "The p95 latency column is not comparable between the two runs, which ran four weeks apart under "
             "different host load.", "",
             "## Against the ReAct baselines", "",
             "Paired on the same task ids, 95% bootstrap intervals (5,000 resamples, seed 0, as in "
             "`results/robustness_checks.md`). \"Best case\" counts every baseline task that hit the 250K-token "
             "request cap as a baseline success; no crmroute task hit it.", "",
             "| comparison | group | n | baseline, measured | baseline, best case | crmroute | difference, measured "
             "[95% CI] | difference, best case [95% CI] |", "|---|---|---|---|---|---|---|---|"]
    for base in ("react", "react_privacy"):
        for name in ("full", "full_nohints"):
            for g in GROUPS[:2]:
                ks = [k for k in keys if group_of(k, runs[base][k]) == g]
                measured = [success(runs[base][k]) for k in ks]
                best = [1.0 if capped(runs[base][k]) else s for k, s in zip(ks, measured)]
                ours = [success(runs[name][k]) for k in ks]
                lines.append(f"| {name} vs {base} | {g} | {len(ks)} | {pct(measured)} | {pct(best)} | {pct(ours)} | "
                             f"{paired(ours, measured)} | {paired(ours, best)} |")
    capped_ours = sum(capped(r) for name in ("full", "full_nohints") for r in runs[name].values())
    lines += ["", f"crmroute tasks ended by the cap (both runs): {capped_ours}.", "",
              "## By task type (business, single-turn)", "",
              "Tasks solved with and without the hints. About 6 tasks per type, so a single type's change is "
              "descriptive, not a finding.", "",
              "| task type | n | with hints | without hints | change |", "|---|---|---|---|---|"]
    single = [k for k in keys if group_of(k, runs["full"][k]) == "business, single-turn"]
    by_type: dict[str, list[tuple]] = {}
    for k in single:
        by_type.setdefault(runs["full"][k]["task_type"], []).append(k)
    table = []
    for task_type, ks in by_type.items():
        with_hints = sum(success(runs["full"][k]) for k in ks)
        without = sum(success(runs["full_nohints"][k]) for k in ks)
        table.append((without - with_hints, task_type, len(ks), with_hints, without))
    for change, task_type, n, with_hints, without in sorted(table):
        lines.append(f"| {task_type} | {n} | {with_hints:g} | {without:g} | {change:+g} |")
    multi = [k for k in keys if group_of(k, runs["full"][k]) == "business, multi-turn"]
    flips = lambda ks: (sum(success(runs["full"][k]) > success(runs["full_nohints"][k]) for k in ks),  # noqa: E731
                        sum(success(runs["full"][k]) < success(runs["full_nohints"][k]) for k in ks))
    lost, gained = flips(single)
    lost_m, gained_m = flips(multi)
    lines += ["", f"Single-turn tasks solved only with the hints: {lost}; only without them: {gained}. "
              f"Multi-turn: {lost_m} and {gained_m}.", "",
              "## Spend", "",
              "List price, the larger of the task records and the per-call logs (as in `results/robustness_checks.md`; "
              "the local judge and simulated user are $0):", "",
              "| run directory | task records | per-call logs |", "|---|---|---|",
              f"| `{ablation_dir.as_posix()}` | ${record_cost(ablation_dir):.2f} | ${logged_cost(ablation_dir):.2f} |"]
    text = "\n".join(lines)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
