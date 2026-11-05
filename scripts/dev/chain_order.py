"""Development data for ordering round 3's rule chain: each candidate rule's coverage and risk on the used
CRMArena-Pro records (rounds 1 and 2, three runs per task), with the gate from scripts/rewrite_recheck.py.

Fixed-sequence Learn-then-Test needs its rules in order of expected risk before calibration; this measures
that order on development data only. Pins come from the other round's keys (cross-fitted), as in the
go/no-go checks. Free-text and BANT answers are withheld, as in rounds 1 and 2; no competence map is applied.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/chain_order.py --pro runs/checkable3_dev/pro_v2.jsonl --out results/checkable3_chain_order.md
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import convention_gate as CG  # noqa: E402
import pro_records as P  # noqa: E402
import release3 as R3  # noqa: E402

CANDIDATES = [(3, "pinned"), (3, "own"), (3, "none"), (2, "pinned"), (2, "own"), (1, "pinned"), (1, "own")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pro", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    rows = [r for r in CG.load(args.pro) if r["kind"] in CG.CHECKABLE]
    pins = {n: CG.pins_by_slot(CG.learn([r for r in rows if r["split"].startswith(f"r{3 - n}_")])["pinned"]) for n in (1, 2)}
    gates = {n: R3.Gate([r for r in rows if r["split"].startswith(f"r{n}_")], pins[n]) for n in (1, 2)}
    tasks = P.load()
    lines = ["# Round 3: ordering the rule chain on development data", "",
             "Computed by `scripts/dev/chain_order.py` on the used CRMArena-Pro records (rounds 1 and 2, 1,753 tasks, three",
             "runs each), with gate results from `scripts/rewrite_recheck.py` and pins cross-fitted by round. Development",
             "data only: it orders the chain before calibration, it is not a result.", "",
             "| rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | runs per task |",
             "|---|---|---|---|---|"]
    for runs_used, kind in CANDIDATES:
        released = wrong = runs = 0
        for t in tasks:
            gate = gates[t.round] if kind != "none" else None
            rule = R3.make_rule(runs_used, kind, gate)
            if rule(t.task):
                released += 1
                wrong += R3.released_run(t.task, rule).correct < 1
            runs += R3.runs_needed(t.task, rule)
        name = R3.make_rule(runs_used, kind, gates[1] if kind != "none" else None).__name__
        ub = R3.RE.upper_bound(int(wrong), released, 0.05)
        lines.append(f"| {name} | {released} of {len(tasks)} ({100 * released / len(tasks):.1f}%) | {int(wrong)} "
                     f"({100 * wrong / released if released else 0:.1f}%) | {100 * ub:.1f}% | {runs / len(tasks):.2f} |")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
