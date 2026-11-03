"""Round 3's development run D1 (one routed run on the original org's 510 used tasks): what the freeze needs.

Per predicted type: tasks, right answers and the share of released answers that are wrong under the one-run
rule (run 1 clean, free text withheld), from which round 3's competence maps are read (types wrong more than
15% and more than 20% are withheld); the list price per task against the plan's $0.0311 (the stop rule drops
ReAct from the calibration half if it is more than 25% above); and the receipt-flag table that fixes the
chain's flag level. Development data on used tasks only.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/d1_summary.py --out results/checkable3_d1.md
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import release_eval as RE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(f"{ROOT / 'runs' / 'checkable3_dev' / 'd1_h1' / 'routed'},{ROOT / 'runs' / 'checkable3_dev' / 'd1_h2' / 'routed'}")
PLANNED_PRICE = 0.0311


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=RUN)
    ap.add_argument("--task-ids", type=Path, default=ROOT / "data" / "checkable3_dev.json")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    tasks = RE.load_tasks([args.run], args.task_ids)
    rule = RE.make_rule(1, (), frozenset(), RE.UNCHECKABLE_FORMS)
    maps = {t: RE.competence_map(tasks, rule, t) for t in (0.15, 0.20)}
    lines = ["# Round 3, development run D1 on the original org's used tasks", "",
             "One routed run of round 2's unchanged image (658df1a6bc7f) on the 510 used single-turn tasks",
             "(`data/checkable3_dev.json`), computed by `scripts/dev/d1_summary.py`. Development data, not a result.", "",
             "| predicted type | tasks | right | released by run 1 clean | wrong among them |", "|---|---|---|---|---|"]
    by = Counter(), Counter(), Counter(), Counter()
    for t in tasks:
        released = rule(t)
        for i, n in enumerate((1, t.runs[0].correct, released, released and t.runs[0].correct < 1)):
            by[i][t.predicted] += n
    for typ in sorted(by[0], key=str):
        rel, wrong = by[2][typ], by[3][typ]
        lines.append(f"| {typ} | {by[0][typ]} | {int(by[1][typ])} | {rel} | {wrong} ({100 * wrong / rel if rel else 0:.1f}%) |")
    total_right = sum(t.runs[0].correct for t in tasks)
    lines += ["", f"Right overall: {int(total_right)} of {len(tasks)} ({100 * total_right / len(tasks):.1f}%).", ""]
    for threshold, withheld in maps.items():
        lines.append(f"Competence map, types wrong more than {round(100 * threshold)}%: {', '.join(sorted(map(str, withheld))) or 'none'}.")
    costs = [t.runs[0].cost or 0 for t in tasks]
    price = sum(costs) / len(costs)
    lines += ["", f"List price: ${sum(costs):.2f} in all, ${price:.4f} per task against the plan's ${PLANNED_PRICE} "
              f"({100 * (price / PLANNED_PRICE - 1):+.1f}%; the stop rule acts above +25%).", "",
              "## Receipt flags (run 1)", "", *RE.flag_table(tasks), ""]
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
