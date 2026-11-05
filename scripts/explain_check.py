"""Show why the convention gate released or held back an answer: its reading table.

For each run of a task in scripts/rewrite_recheck.py output, prints the answer, the deciding query and the
own level, then every declared reading of the question's period: its choices (season, year, rolling or
calendar window, date field), the rewritten query that was re-run live, and the answer it gives under each
tie reading. The readings the pinned gate asks under an org's conventions are marked; the gate's decision
follows at each level.

  python scripts/explain_check.py --records runs/checkable3_dev/pro_v2.jsonl --task b2b/1110
  python scripts/explain_check.py --records runs/checkable3_dev/d1.jsonl --task original/655 \
      --conventions data/conventions_original.yaml
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import convention_gate as CG  # noqa: E402


def show(answer) -> str:
    kind, values = answer[0], answer[1]
    return "None" if kind == "none" else ", ".join(values)


def table(run: dict, pins: dict | None) -> list[str]:
    lines = [f"run {run['run']}: answer {show(run['answer'])}"
             + (f" (key {show(run['key'])}, {'right' if run['correct'] >= 1 else 'wrong'})" if "key" in run else "")]
    if run.get("why") and not run.get("readings"):
        return lines + [f"  not checked: {run['why']}"]
    lines.append(f"  own level: {run.get('own')} (deciding query: receipt entry {run.get('deciding')})")
    for reading in run.get("readings", []):
        label = "; ".join(f"{s} = {v}" for s, v in reading["choices"]) or "the period the question names"
        asked = pins is not None and all(s not in pins or v in pins[s] for s, v in reading["choices"])
        if reading.get("status") != "ok":
            got = reading.get("status")
        else:
            answers = reading["answers"]
            got = show(answers["*"]) if "*" in answers else (
                f"a tie: {show(answers['first'])} (first) or None")
        lines.append(f"  {'[asked] ' if asked else ''}{label} -> {got}")
        if reading.get("query"):
            lines.append(f"      {reading['query']}")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", type=Path, required=True, help="scripts/rewrite_recheck.py output")
    ap.add_argument("--task", required=True, help="org/task id, e.g. b2b/1110")
    ap.add_argument("--conventions", type=Path, help="an org's frozen conventions (scripts/learn_conventions.py)")
    args = ap.parse_args()
    org, tid = args.task.split("/")
    runs = [r for r in CG.load(args.records) if r["org"] == org and str(r["task"]) == tid]
    if not runs:
        raise SystemExit(f"{args.task} is not in {args.records}")
    pins = None
    if args.conventions:
        import learn_conventions as LC
        pins = LC.pins_of(args.conventions)
    print(f"{args.task} ({runs[0]['predicted']}), period: {runs[0]['period']['text'] or 'none'}")
    if pins is not None:
        print("[asked]: a reading the pinned gate asks (a slot's pinned readings, or all of a slot without one)")
    for run in runs:
        print("\n".join(table(run, pins)))
    levels = {"own": [r.get("own", "unchecked") for r in runs], "declared": [CG.level(r) for r in runs]}
    if pins is not None:
        levels["pinned"] = [CG.pinned_level(r, pins, own_required=False) for r in runs]
    print("gate: " + "; ".join(f"{name} {CG.task_gate(v)} (runs: {', '.join(v)})" for name, v in levels.items()))


if __name__ == "__main__":
    main()
