"""Round 3's frozen chain inputs from the development run D1 (docs/checkable3_devlog.md, the entry written while
D1 ran): the flag level, the competence maps and the chain, in results/checkable3_frozen.json.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/freeze_inputs.py --d1 runs/checkable3_dev/d1.jsonl \
      --g2 pass --out results/checkable3_frozen.json

Flag level: the strictest of round 2's soft-flag levels that withholds at most 10% of the run-1 answers the
level without soft flags releases. Maps: predicted types whose released run-1 answers in D1 are wrong more
than 15% / 20% (through the pinned gate on gated types, with G2's cross-fitted pins, when G2 passed). The chain
is written as rule specs, in order, for scripts/checkable3_report.py to build unchanged.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import convention_gate as CG  # noqa: E402
import release3 as R3  # noqa: E402

RE = R3.RE
ROOT = Path(__file__).resolve().parents[2]
# A single run's error over three agreeing runs' on the used Pro records (20.5% / 11.0%), which scales round
# 2's three-run map thresholds to single-run data (docs/checkable3_devlog.md, the entry after reading D1).
RATIO = 1.86
# The types whose right answers D1's pinned gate held back at most 8% of the time: the gate's secondary analysis.
GATE_TYPES = ("best_region_identification", "case_routing", "transfer_count")
D1_RUN = Path(f"{ROOT / 'runs' / 'checkable3_dev' / 'd1_h1' / 'routed'},{ROOT / 'runs' / 'checkable3_dev' / 'd1_h2' / 'routed'}")


def spec(runs_used: int, gate: str, soft, withheld) -> dict:
    rule = R3.make_rule(runs_used, gate, R3.Gate([], {}) if gate != "none" else None, tuple(soft), frozenset(withheld))
    return {"rule": rule.__name__, "runs_used": runs_used, "gate": gate, "soft": list(soft), "withheld_types": sorted(withheld)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d1", type=Path, required=True, help="rewrite_recheck.py --records d1 output")
    ap.add_argument("--g2", choices=["pass", "fail"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--run", type=Path, default=D1_RUN)
    ap.add_argument("--task-ids", type=Path, default=ROOT / "data" / "checkable3_dev.json")
    args = ap.parse_args()
    tasks = RE.load_tasks([args.run], args.task_ids)
    rows = [r for r in CG.load(args.d1) if r["kind"] in CG.CHECKABLE]
    fold = lambda tid: int(tid) % 2  # noqa: E731
    pins = {f: CG.pins_by_slot(CG.learn([r for r in rows if fold(r["task"]) != f])["pinned"]) for f in (0, 1)}
    by_key = {(r["org"], str(r["task"])): r for r in rows}

    def gated_pass(t) -> bool:
        row = by_key.get((t.key[0], str(t.key[2])))
        return row is not None and CG.pinned_level(row, pins[fold(t.key[2])], own_required=False) == "pass"

    released = {soft: sum(RE.make_rule(1, soft, frozenset(), RE.UNCHECKABLE_FORMS)(t) for t in tasks) for soft in RE.SOFT_LEVELS}
    soft = next(s for s in RE.SOFT_LEVELS if released[s] >= 0.9 * released[()])

    def maps_at(level) -> tuple[dict, dict]:
        rule = RE.make_rule(1, level, frozenset(), RE.UNCHECKABLE_FORMS)
        n, wrong = Counter(), Counter()
        for t in tasks:
            if rule(t) and (args.g2 == "fail" or t.predicted not in R3.GATED or gated_pass(t)):
                n[t.predicted] += 1
                wrong[t.predicted] += t.runs[0].correct < 1
        rates = {str(k): [wrong[k], n[k]] for k in n}
        return rates, {th: sorted(str(k) for k in n if wrong[k] / n[k] > float(th)) for th in ("0.15", "0.20")}

    if args.g2 == "pass":
        rates, maps = maps_at(soft)
        chain = [spec(runs_used, "pinned", soft, maps[th]) for runs_used in (3, 2, 1) for th in ("0.15", "0.20")]
        chain += [spec(3, "none", soft, maps[th]) for th in ("0.15", "0.20")]
        out_maps, out_rates = maps, rates
    else:  # round 2's chain for this org (maps per flag level, as round 2 learned them), then the scaled maps, then none
        chain, out_maps, out_rates = [], {}, {}
        for label, threshold in (("0.15", 0.15), ("0.20", 0.20), (f"{0.15 * RATIO:.3f}", 0.15 * RATIO),
                                 (f"{0.20 * RATIO:.3f}", 0.20 * RATIO), ("no map", None)):
            for level in RE.SOFT_LEVELS:
                rates, _ = maps_at(level)
                withheld = sorted(k for k, (w, n) in rates.items() if threshold is not None and w / n > threshold)
                chain.append(spec(3, "none", level, withheld))
                out_maps[f"{'/'.join(level) or 'no soft flags'} {label}"] = withheld
                out_rates['/'.join(level) or 'no soft flags'] = rates
    frozen = {"g2": args.g2, "soft": list(soft), "released_run1_by_flag_level": {"/".join(k) or "none": v for k, v in released.items()},
              "maps": out_maps, "map_rates_wrong_released": out_rates, "pins": "data/conventions_original.yaml",
              "single_to_three_run_error": RATIO, "gate_types": list(GATE_TYPES), "chain": chain}
    args.out.write_text(json.dumps(frozen, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in frozen.items() if k != "chain"}, indent=1))
    for i, s in enumerate(chain, 1):
        print(f"{i}. {s['rule']}")


if __name__ == "__main__":
    main()
