"""Does a routing table fitted on one org's dev runs save cost on another org? (offline)

runs/dev3/full and runs/dev3/agent_small hold both solvers on the same dev tasks in both Pro orgs.
For each direction a table is fitted with fit_routing.py's own pairing and rule on the source org's
business dev tasks, then applied to the target org's tasks using the task type the router predicted
at run time: a task routed small takes the small run's result and cost, otherwise the big run's.
Compared with the big model alone on the same tasks (paired bootstrap, 5,000 resamples). Only the
source -> target rows are out of sample; a table fitted on the target org itself is in sample.

Usage:  python scripts/routing_transfer.py --out results/routing_transfer.json
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_results import CONFIDENTIALITY, load_system, score  # noqa: E402
from fit_routing import paired_rates  # noqa: E402


def cost_of(row: dict) -> float:
    usage = (row.get("agent_info") or {}).get("usage") or {}
    return float(usage.get("total_cost_usd") or (row.get("agent_info") or {}).get("total_cost") or 0.0)


def fit(big: dict, small: dict, keys: list, margin: float, min_n: int) -> dict:
    by_big, by_small = paired_rates({k: big[k] for k in keys}, {k: small[k] for k in keys}, 0.5)
    tiers = {}
    for t in by_big:  # the rule in fit_routing.main
        b, s = 100 * sum(by_big[t]) / len(by_big[t]), 100 * sum(by_small[t]) / len(by_small[t])
        tiers[t] = "small" if min(len(by_big[t]), len(by_small[t])) >= min_n and s >= b - margin else "big"
    return tiers


def evaluate(big: dict, small: dict, keys: list, tiers: dict) -> dict:
    rows = []
    for k in keys:
        predicted = ((big[k].get("agent_info") or {}).get("route") or {}).get("task_type")
        chosen = small[k] if tiers.get(predicted) == "small" else big[k]
        rows.append((score(big[k], 0.5)[1], score(chosen, 0.5)[1], cost_of(big[k]), cost_of(chosen),
                     tiers.get(predicted) == "small"))
    n = len(rows)
    diffs = [r[1] - r[0] for r in rows]
    rng = random.Random(0)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(5000))
    big_cost, routed_cost = sum(r[2] for r in rows), sum(r[3] for r in rows)
    return {"n": n, "sent_to_small": sum(r[4] for r in rows),
            "big_success": round(100 * sum(r[0] for r in rows) / n, 1), "routed_success": round(100 * sum(r[1] for r in rows) / n, 1),
            "diff_points": round(100 * sum(diffs) / n, 1), "diff_ci95": [round(100 * boots[124], 1), round(100 * boots[4874], 1)],
            "big_cost": round(big_cost, 4), "routed_cost": round(routed_cost, 4),
            "cost_change_pct": round(100 * (routed_cost - big_cost) / big_cost, 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--big", default="runs/dev3/full")
    ap.add_argument("--small", default="runs/dev3/agent_small")
    ap.add_argument("--margin", type=float, default=2.0)
    ap.add_argument("--out", default="results/routing_transfer.json")
    args = ap.parse_args()
    big, small = load_system(ROOT / args.big), load_system(ROOT / args.small)
    keys = sorted((k for k in big if k in small and big[k]["task_type"] not in CONFIDENTIALITY), key=str)
    by_org = {o: [k for k in keys if k[0] == o] for o in ("b2b", "b2c")}
    per_type = {o: sorted(sum(1 for k in by_org[o] if big[k]["task_type"] == t) for t in {big[k]["task_type"] for k in by_org[o]})
                for o in by_org}
    report = {"source": {"big": args.big, "small": args.small}, "margin_points": args.margin,
              "business_dev_tasks_per_org": {o: len(v) for o, v in by_org.items()},
              "median_tasks_per_type_per_org": {o: v[len(v) // 2] for o, v in per_type.items()}, "results": []}
    print(f"business dev tasks per org {report['business_dev_tasks_per_org']}, median per type {report['median_tasks_per_type_per_org']}")
    for min_n in (8, 4):
        for source, target in (("b2b", "b2c"), ("b2c", "b2b")):
            for fitted_on, fit_keys in (("source org (out of sample)", by_org[source]),
                                        ("target org (in sample)", by_org[target]), ("both orgs (in sample)", keys)):
                tiers = fit(big, small, fit_keys, args.margin, min_n)
                r = {"min_n": min_n, "target": target, "fitted_on": fitted_on,
                     "types_small": sorted(t for t, v in tiers.items() if v == "small"), **evaluate(big, small, by_org[target], tiers)}
                report["results"].append(r)
                print(f"min_n={min_n} {target} | fitted on {fitted_on:<27} | small types {len(r['types_small']):>2} | "
                      f"success {r['big_success']} -> {r['routed_success']} ({r['diff_points']:+} {r['diff_ci95']}) | cost {r['cost_change_pct']:+}%")
    Path(args.out).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
