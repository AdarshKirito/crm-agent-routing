"""Round 3's second development check G2 (docs/checkable3_devlog.md): the pinned-reading gate on the original
org, computed from scripts/rewrite_recheck.py output for the development run D1.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/g2.py --d1 runs/checkable3_dev/d1.jsonl --out results/checkable3_g2.md

As committed before D1 ran: the population is D1's checkable run answers in the six types, by predicted type;
pins are cross-fitted between tasks with odd and even ids (each half judged by pins learned from the other
half's keys, by the rule used on the Pro records); the gate asks only the pinned readings, the executed
readings deciding wherever the question has a period and the own level elsewhere. D1 has one run per task,
so a task's gate is its run's level. The own-level-required, allowed and declared levels are reported beside.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import gonogo as G
from convention_gate import pinned_level  # noqa: E402  (gonogo puts scripts/ on the path)

BARS = {"G2a": (">=", 0.85), "G2b": (">=", 0.40), "G2c": ("<=", 0.08)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d1", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    population = [r for r in G.load(args.d1) if r["kind"] in G.CHECKABLE]
    fold = lambda r: int(r["task"]) % 2  # noqa: E731
    learned = {f: G.learn([r for r in population if fold(r) != f]) for f in (0, 1)}
    pins = {}
    for f, info in learned.items():
        by_slot = defaultdict(set)
        for slot, value in info["pinned"]:
            by_slot[slot].add(value)
        pins[f] = dict(by_slot)
    levels = {
        "pinned, readings decide (G2)": lambda r: pinned_level(r, pins[fold(r)], own_required=False),
        "pinned, own level required": lambda r: pinned_level(r, pins[fold(r)], own_required=True),
        "allowed (the go/no-go level)": lambda r: G.level(r, learned[fold(r)]["excluded"]),
        "declared": lambda r: G.level(r),
    }
    lines = ["# Round 3, G2: the pinned-reading gate on the original org's development run", "",
             "Computed by `scripts/dev/g2.py` from `scripts/rewrite_recheck.py --records d1`, with the check and its bars",
             "committed in `docs/checkable3_devlog.md` before D1 ran. D1 is one routed run of round 2's image on the",
             "original org's 510 used tasks; these are development figures on used tasks, not a test.", "",
             "| judged half | pinned readings (from the other half's keys) | excluded |", "|---|---|---|"]
    for f in (0, 1):
        lines.append(f"| {'even' if f == 0 else 'odd'} ids | "
                     + "; ".join(f"{s}: {', '.join(sorted(v))}" for s, v in sorted(pins[f].items())) + " | "
                     + (", ".join(f"{s}={v}" for s, v in sorted(learned[f]["excluded"])) or "none") + " |")
    lines += ["", "| level | type | run answers | check completes | wrong held back | right held back |",
              "|---|---|---|---|---|---|"]
    results = {}
    for name, level_of in levels.items():
        counts = Counter()
        for r in population:
            lv = level_of(r)
            right = r["correct"] >= 1
            for typ in (r["predicted"], "all"):
                counts[(typ, "n")] += 1
                counts[(typ, "done")] += lv != "unchecked"
                counts[(typ, right)] += 1
                counts[(typ, right, "held")] += lv != "pass"
        for typ in sorted({k[0] for k in counts if k[0] != "all"}) + ["all"]:
            lines.append(f"| {name} | {typ} | {counts[(typ, 'n')]} | {G.ratio(counts[(typ, 'done')], counts[(typ, 'n')])} | "
                         f"{G.ratio(counts[(typ, False, 'held')], counts[(typ, False)])} | "
                         f"{G.ratio(counts[(typ, True, 'held')], counts[(typ, True)])} |")
        if name.endswith("(G2)"):
            results = {"G2a": counts[("all", "done")] / counts[("all", "n")],
                       "G2b": counts[("all", False, "held")] / counts[("all", False)] if counts[("all", False)] else 0.0,
                       "G2c": counts[("all", True, "held")] / counts[("all", True)] if counts[("all", True)] else 0.0}
    lines += ["", "| check | value | GO if | result |", "|---|---|---|---|"]
    for name, (op, bar) in BARS.items():
        ok = results[name] >= bar if op == ">=" else results[name] <= bar
        lines.append(f"| {name} | {100 * results[name]:.1f}% | {'at least' if op == '>=' else 'at most'} {100 * bar:.0f}% | "
                     f"{'pass' if ok else 'FAIL'} |")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
