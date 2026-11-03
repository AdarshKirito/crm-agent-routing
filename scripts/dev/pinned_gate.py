"""Exploratory, computed after round 3's go/no-go decision (docs/checkable3_devlog.md, NO-GO): the gate asked
only the readings the other round's keys pin.

The go/no-go used the allowed level: every reading the other round's keys do not exclude. Here a slot with a
pinned reading is asked only its pinned readings (scripts/dev/gonogo.py learn: runs of three or more tasks
support it, none contradicts it); other slots keep all theirs. Two variants: the own level is required, as in
the development log; or it decides only questions without readings, and elsewhere the executed readings
decide. Nothing here changes the decision. It says whether such a gate is worth pre-registering as an arm and
testing on the original org.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/pinned_gate.py --pro runs/checkable3_dev/pro.jsonl --out results/checkable3_pinned.md
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import gonogo as G


def pinned_level(run: dict, pins: dict, own_required: bool) -> str:
    """pass | fail | unchecked of one run over the pinned readings (`pins`: slot -> pinned readings)."""
    readings = run.get("readings", [])
    if run.get("own") == "fail" and (own_required or not readings):
        return "fail"
    answer = G.akey(run["answer"])
    unknown = bool(run.get("why")) or ((own_required or not readings) and run.get("own") != "pass")
    asked = 0
    for reading in readings:
        if any(slot in pins and value not in pins[slot] for slot, value in reading["choices"]):
            continue
        if reading.get("status") != "ok":
            unknown = True
            continue
        for choices, a in G.combos(reading):
            slot, value = choices[-1]
            if slot in pins and value not in pins[slot]:
                continue
            asked += 1
            if a != answer:
                return "fail"
    return "unchecked" if unknown or (readings and not asked) else "pass"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pro", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    rows = G.load(args.pro)
    population = [r for r in rows if r["kind"] in G.CHECKABLE]
    tasks = defaultdict(list)
    for r in rows:
        tasks[(r["split"], r["org"], r["task"])].append(r)
    pins = {}
    for n in (1, 2):
        learned = G.learn([r for r in population if r["split"].startswith(f"r{3 - n}_")])
        by_slot = defaultdict(set)
        for slot, value in learned["pinned"]:
            by_slot[slot].add(value)
        pins[n] = dict(by_slot)
    unanimous = {k: v for k, v in tasks.items() if v[0]["unanimous"]}
    lines = ["# Round 3, exploratory: the gate over pinned readings only", "",
             "Computed by `scripts/dev/pinned_gate.py` after the go/no-go decision (NO-GO, `results/checkable3_gonogo.md`),",
             "on the same in-sample CRMArena-Pro records. Pins are cross-fitted by round, as in the go/no-go. This is a",
             "post-hoc analysis: it can motivate an arm to pre-register and test on new data, not a result.", "",
             "| tasks judged | pinned readings (from the other round's keys) |", "|---|---|"]
    for n, p in pins.items():
        lines.append(f"| round {n} | " + "; ".join(f"{s}: {', '.join(sorted(v))}" for s, v in sorted(p.items())) + " |")
    lines += ["", "| variant | type | unanimous wrong held back | unanimous right held back |", "|---|---|---|---|"]
    for own_required, label in ((True, "own level required"), (False, "readings decide where they exist")):
        held = Counter()
        for key, runs in unanimous.items():
            right = runs[0]["correct"] >= 1
            gate = G.task_gate([pinned_level(r, pins[int(key[0][1])], own_required) for r in runs])
            for typ in (runs[0]["predicted"], "all"):
                held[(typ, right, "n")] += 1
                held[(typ, right, "held")] += gate != "pass"
        for typ in sorted({k[0] for k in held if k[0] != "all"}) + ["all"]:
            lines.append(f"| {label} | {typ} | {G.ratio(held[(typ, False, 'held')], held[(typ, False, 'n')])} | "
                         f"{G.ratio(held[(typ, True, 'held')], held[(typ, True, 'n')])} |")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
