"""How far the headline numbers depend on choices made in this project.

Reads the run records in runs/ (git-ignored, not in the repository) and writes a markdown report:

1. The ReAct context cap. The patched harness does not send a request above 250K input tokens
   and scores the task as the system's failure. This counts those tasks per group and recomputes
   the paired differences with every one of them counted as a baseline success (its best case).
2. Customer-facing business requests refused (false refusals) by the guard or by the solver,
   single- and multi-turn, on the test run and on both fresh runs.
3. Router-example overlap. The router's example file was exported from every non-test task
   before data/fresh.json existed, and the router's nearest task type is passed to the policy
   classifier as a hint. This counts fresh tasks that are themselves labelled examples and
   reports the refusal rate on confidential requests inside and outside the example file.
4. List-price spend, split into the runs made before the test run, the test run, and the runs
   made after it. Per run directory it takes the larger of two sums: the task records (failed
   attempts included) and the per-call logs, which also hold calls of tasks that never finished
   but have no prices in the earliest runs.

Usage:  python scripts/robustness_checks.py --out results/robustness_checks.md
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_results import CONFIDENTIALITY, REFUSAL_REPLY, expected_keys, final_reply, load_system, score  # noqa: E402

CUSTOMER_BUSINESS = {"knowledge_qa", "named_entity_disambiguation"}  # EXTERNAL_FACING_TASKS minus refusals
GROUPS = ("business, single-turn", "business, multi-turn", "confidentiality")
AFTER_TEST = {"fresh_before", "fresh_after", "original_smoke", "original_smoke2", "original_dev",
              "original_dev_oom_attempt", "original_test", "ablation_hints"}


def group_of(key: tuple, row: dict) -> str:
    if row["task_type"] in CONFIDENTIALITY:
        return "confidentiality"
    return "business, multi-turn" if key[1] else "business, single-turn"


def success(row: dict) -> float:
    return score(row, 0.5)[1]  # reward 1 on a confidential request = refused


def capped(row: dict) -> bool:
    return row.get("failure") == "request_too_large"


def guard_refused(row: dict) -> bool:
    return ((row.get("agent_info") or {}).get("guard") or {}).get("decision") == "refuse"


def pct(values: list[float]) -> str:
    return f"{100 * sum(values) / len(values):.1f}%"


def paired(new: list[float], old: list[float], iters: int = 5000) -> str:
    """new - old in points, 95% paired bootstrap interval (seed 0, as in fresh_analysis.py)."""
    diffs = [a - b for a, b in zip(new, old)]
    n = len(diffs)
    rng = random.Random(0)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    lo, hi = boots[int(0.025 * iters)], boots[int(0.975 * iters) - 1]
    return f"{100 * sum(diffs) / n:+.1f} [{100 * lo:+.1f}, {100 * hi:+.1f}]"


def load_split(path: Path, wanted: set) -> dict:
    rows = load_system(path)
    missing = wanted - rows.keys()
    if missing:
        raise SystemExit(f"{path}: {len(missing)} tasks of the split are missing")
    return {k: rows[k] for k in wanted}


def cap_section(test_dir: Path, task_ids: Path) -> list[str]:
    wanted = expected_keys(task_ids)
    runs = {name: load_split(test_dir / name, wanted) for name in ("react", "react_privacy", "full", "routed")}
    keys = sorted(wanted)
    lines = ["## 1. The 250K-token request cap (test run)", "",
             f"`{test_dir.as_posix()}`, `{task_ids.as_posix()}`. Tasks scored as failures because one request "
             "went over the cap:", "",
             "| system | business, single-turn | business, multi-turn | confidentiality | total |",
             "|---|---|---|---|---|"]
    for name, rows in runs.items():
        counts = [sum(capped(rows[k]) for k in keys if group_of(k, rows[k]) == g) for g in GROUPS]
        lines.append(f"| {name} | " + " | ".join(map(str, counts)) + f" | {sum(counts)} |")
    lines += ["", "Business success with every capped baseline task counted as a success instead (the best case "
              "for the baseline), paired on the same task ids:", "",
              "| comparison | group | n | baseline, measured | baseline, best case | crmroute | difference, best case [95% CI] |",
              "|---|---|---|---|---|---|---|"]
    for base in ("react", "react_privacy"):
        for name in ("full", "routed"):
            for g in GROUPS[:2]:
                ks = [k for k in keys if group_of(k, runs[base][k]) == g]
                measured = [success(runs[base][k]) for k in ks]
                best = [1.0 if capped(runs[base][k]) else s for k, s in zip(ks, measured)]
                ours = [success(runs[name][k]) for k in ks]
                lines.append(f"| {name} vs {base} | {g} | {len(ks)} | {pct(measured)} | {pct(best)} | {pct(ours)} | "
                             f"{paired(ours, best)} |")
    return lines


def solver_refused(row: dict) -> bool:
    """The guard allowed the request, but the agent's final reply declines to answer it."""
    return not guard_refused(row) and bool(REFUSAL_REPLY.search(final_reply(row)))


def false_refusal_section(runs: list[tuple[str, Path, Path]]) -> list[str]:
    lines = ["", "## 2. Customer-facing business requests refused", "",
             "The benchmark runs knowledge_qa and named_entity_disambiguation tasks as customer sessions, so the "
             "policy check screens them alongside the confidential requests; refusing one is a false refusal. The guard "
             "can refuse a request, or the solver can after the guard allowed it: its final reply then declines to answer "
             "(\"I cannot share this information because it is confidential.\"), found with a fixed regex "
             "(`REFUSAL_REPLY` in `scripts/analyze_results.py`).", "",
             "| run | single-turn, guard | single-turn, solver | multi-turn, guard | multi-turn, solver | guard-refused tasks | solver refusals by type |",
             "|---|---|---|---|---|---|---|"]
    for label, path, task_ids in runs:
        wanted = expected_keys(task_ids)
        rows = load_split(path, wanted)
        cust = sorted(k for k in wanted if rows[k]["task_type"] in CUSTOMER_BUSINESS)
        single, multi = [k for k in cust if not k[1]], [k for k in cust if k[1]]
        refused = [k for k in cust if guard_refused(rows[k])]
        names = ", ".join(f"{org}/{tid} ({'multi' if inter else 'single'}-turn, {rows[(org, inter, tid)]['task_type']})"
                          for org, inter, tid in refused) or "none"
        types = Counter(rows[k]["task_type"] for k in cust if solver_refused(rows[k]))
        by_type = ", ".join(f"{t} {n}" for t, n in sorted(types.items())) or "none"
        count = lambda ks, refused_by: f"{sum(refused_by(rows[k]) for k in ks)} of {len(ks)}"  # noqa: E731
        lines.append(f"| {label} | {count(single, guard_refused)} | {count(single, solver_refused)} | "
                     f"{count(multi, guard_refused)} | {count(multi, solver_refused)} | {names} | {by_type} |")
    return lines


def overlap_section(before: Path, after: Path, task_ids: Path, examples: Path, test_ids: Path) -> list[str]:
    in_examples = {(e["org"], str(e["idx"])) for e in map(json.loads, examples.read_text(encoding="utf-8").splitlines())}
    seen = lambda key: (key[0], key[2]) in in_examples  # noqa: E731 - task ids are shared across modes
    wanted = expected_keys(task_ids)
    old, new = load_split(before, wanted), load_split(after, wanted)
    keys = sorted(wanted)
    lines = ["", "## 3. Fresh tasks that are labelled router examples", "",
             f"`{examples.as_posix()}` ({len(in_examples)} examples) holds 0 of the "
             f"{len(expected_keys(test_ids))} test tasks and these fresh tasks:", "",
             "| group | fresh tasks | also router examples |", "|---|---|---|"]
    for g in GROUPS:
        ks = [k for k in keys if group_of(k, new[k]) == g]
        lines.append(f"| {g} | {len(ks)} | {sum(seen(k) for k in ks)} |")
    if any(seen(k) for k in expected_keys(test_ids)):
        raise SystemExit("router examples overlap the test split")
    conf = [k for k in keys if new[k]["task_type"] in CONFIDENTIALITY]
    lines += ["", f"Confidential requests refused, `{before.as_posix()}` vs `{after.as_posix()}`:", "",
              "| requests | n | before | after | difference [95% CI] |", "|---|---|---|---|---|"]
    subsets = [("all", conf), ("in the example file", [k for k in conf if seen(k)]),
               ("not in the example file", [k for k in conf if not seen(k)])]
    subsets += [(f"not in the example file, {t}", [k for k in conf if not seen(k) and new[k]["task_type"] == t])
                for t in sorted(CONFIDENTIALITY)]
    for label, ks in subsets:
        b, a = [success(old[k]) for k in ks], [success(new[k]) for k in ks]
        lines.append(f"| {label} | {len(ks)} | {pct(b)} | {pct(a)} | {paired(a, b)} |")
    return lines


def logged_cost(run_dir: Path) -> float:
    """Spend in the per-call logs: agent_calls_*.jsonl (the agent) and bench_calls_*.jsonl (the harness)."""
    total = 0.0
    for f in [*run_dir.rglob("agent_calls_*.jsonl"), *run_dir.rglob("bench_calls_*.jsonl")]:
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                call = json.loads(line)
            except ValueError:
                continue
            total += float(call.get("cost_usd") or call.get("cost") or 0.0)
    return total


def spend_section(runs_dir: Path, test_dir: Path) -> list[str]:
    phases: dict[str, list[tuple[str, int, float]]] = {"before the test": [], "test run": [], "after the test": []}
    for d in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        files = sorted(d.rglob("results_*.json"))
        if not files:
            continue
        tasks, cost = 0, 0.0
        for f in files:
            for r in json.loads(f.read_text(encoding="utf-8")):
                tasks += 1
                for attempt in [r, *(r.get("previous_attempts") or [])]:
                    cost += float((attempt.get("agent_info") or {}).get("total_cost") or 0.0)
                    cost += sum(float(c.get("cost") or 0.0) for c in attempt.get("llm_calls") or []
                                if c.get("role") in ("judge", "user"))
        phase = "test run" if d == test_dir else ("after the test" if d.name in AFTER_TEST else "before the test")
        phases[phase].append((d.name, tasks, max(cost, logged_cost(d))))
    lines = ["", "## 4. List-price spend", "",
             "Model calls at list price (agent, policy classifier, Prompt Guard, and any judge or simulated-user "
             "API calls; local Ollama is $0). Per run directory, the larger of the task records (failed attempts "
             "included) and the per-call logs: the logs also hold calls of tasks that never finished, such as a run "
             "stopped mid-task, but the earliest runs logged no prices. Runs on free tiers (the 2026-09-29 pilot and "
             "the PR-eval baseline runs) are counted at list price although they were not billed. Prompt Guard calls "
             "rejected with 429 have no usage record.", "",
             "| phase | run directories | task records | list-price spend |", "|---|---|---|---|"]
    total = 0.0
    for phase, rows in phases.items():
        spend = sum(c for _, _, c in rows)
        total += spend
        dirs = ", ".join(f"{name} (${c:.2f})" for name, _, c in rows)
        lines.append(f"| {phase} | {dirs} | {sum(t for _, t, _ in rows)} | ${spend:.2f} |")
    lines.append(f"| all | | | ${total:.2f} |")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--test-ids", type=Path, default=Path("data/test.json"))
    ap.add_argument("--fresh-ids", type=Path, default=Path("data/fresh.json"))
    ap.add_argument("--router-examples", type=Path, default=Path("agent/app/data/router_examples.jsonl"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    test_dir = args.runs / "test"
    before, after = args.runs / "fresh_before" / "routed", args.runs / "fresh_after" / "routed"
    lines = ["# Robustness checks on the headline numbers", "",
             "```", "python scripts/robustness_checks.py --out results/robustness_checks.md", "```", ""]
    lines += cap_section(test_dir, args.test_ids)
    lines += false_refusal_section([("test, crmroute 3.8 Flash only", test_dir / "full", args.test_ids),
                                    ("test, crmroute routed", test_dir / "routed", args.test_ids),
                                    ("fresh, measured agent", before, args.fresh_ids),
                                    ("fresh, fixed agent", after, args.fresh_ids)])
    lines += overlap_section(before, after, args.fresh_ids, args.router_examples, args.test_ids)
    lines += spend_section(args.runs, test_dir)
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
