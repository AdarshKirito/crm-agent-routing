"""Round 3's go/no-go checks C1-C8 (docs/checkable3_devlog.md), computed from scripts/rewrite_recheck.py output.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/gonogo.py --pro runs/checkable3_dev/pro.jsonl \
      --original runs/checkable3_dev/original_react.jsonl --out results/checkable3_gonogo.md

Definitions follow the development log: the population is the checkable run answers of the six types by
predicted type; a run's gate level is own, allowed or declared; a task passes the gate when no run of its
majority group fails and at least one passes; allowed readings are cross-fitted by round (round-2 tasks are
judged by readings learned from round-1 keys and the other way round). C9 is checked by hand and logged.
"""
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from convention_gate import CHECKABLE, akey, combos, complete, learn, level, load, task_gate  # noqa: E402

THRESHOLDS = {"C1": (">=", 0.90), "C2": (">=", 0.85), "C3": ("<=", 0.10), "C4": (">=", 0.40), "C5": ("<=", 0.08),
              "C6": (">=", 2), "C8": (">=", 0.85)}


def gate_checks(unanimous: dict, learned: dict, types=None) -> dict:
    """C4-C6 and the pass/fail/unchecked table on the unanimous tasks (of `types`, if given)."""
    table, withheld, own_pass_wrong, c6 = Counter(), Counter(), [], 0
    chosen = {k: v for k, v in unanimous.items() if types is None or v[0]["predicted"] in types}
    for key, runs in chosen.items():
        excluded = learned[int(key[0][1])]["excluded"]
        right = runs[0]["correct"] >= 1
        gates = {"own": task_gate([r.get("own", "unchecked") for r in runs]),
                 "allowed": task_gate([level(r, excluded) for r in runs]),
                 "declared": task_gate([level(r) for r in runs])}
        for name, g in gates.items():
            table[(name, right, g)] += 1
        if gates["allowed"] != "pass":
            withheld[right] += 1
        if not right and gates["own"] == "pass":
            own_pass_wrong.append(f"{key[1]}/{key[2]}{'' if gates['allowed'] == 'pass' else ' (withheld)'}")
            c6 += gates["allowed"] != "pass"
    wrong = sum(1 for v in chosen.values() if v[0]["correct"] < 1)
    right = len(chosen) - wrong
    return {"tasks": len(chosen), "wrong": wrong, "right": right, "table": table, "own_pass_wrong": own_pass_wrong,
            "C4": withheld[False] / wrong if wrong else 0.0, "C5": withheld[True] / right if right else 0.0, "C6": c6,
            "withheld_wrong": withheld[False], "withheld_right": withheld[True]}


def gate_lines(g: dict, title: str) -> list[str]:
    lines = [f"## {title}: {g['tasks']} unanimous tasks ({g['wrong']} wrong, {g['right']} right)", "",
             "| level | wrong: pass / fail / unchecked | right: pass / fail / unchecked |", "|---|---|---|"]
    for name in ("own", "allowed", "declared"):
        cells = [" / ".join(str(g["table"][(name, right, s)]) for s in ("pass", "fail", "unchecked")) for right in (False, True)]
        lines.append(f"| {name} | {cells[0]} | {cells[1]} |")
    return lines + ["", f"Withheld at the allowed level: {ratio(g['withheld_wrong'], g['wrong'])} wrong answers (C4), "
                    f"{ratio(g['withheld_right'], g['right'])} right answers (C5). Unanimous wrong tasks that pass the own "
                    f"level: {', '.join(sorted(g['own_pass_wrong'])) or 'none'} (C6 counts the withheld ones: {g['C6']}).", ""]


def ratio(a: int, b: int) -> str:
    return f"{a} of {b} ({100 * a / b:.1f}%)" if b else "0 of 0"


def passes(name: str, value) -> bool:
    op, bar = THRESHOLDS[name]
    return value >= bar if op == ">=" else value <= bar


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pro", type=Path, required=True)
    ap.add_argument("--original", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    rows = load(args.pro)
    population = [r for r in rows if r["kind"] in CHECKABLE]
    tasks = defaultdict(list)
    for r in rows:
        tasks[(r["split"], r["org"], r["task"])].append(r)
    results = {}
    lines = ["# Round 3 go/no-go checks on CRMArena-Pro records", "",
             "Computed by `scripts/dev/gonogo.py` from `scripts/rewrite_recheck.py` output, with the definitions and",
             "thresholds committed in `docs/checkable3_devlog.md` before any of them was computed. These are in-sample",
             "development figures: the engine was written while reading these records.", ""]

    # C1, C2
    by_type = defaultdict(list)
    for r in population:
        by_type[r["predicted"]].append(r)
    c1 = sum(complete(r) for r in population)
    c2 = sum(r.get("own") == "pass" for r in population)
    results["C1"], results["C2"] = c1 / len(population), c2 / len(population)
    lines += ["## Run answers of the six types, by predicted type", "",
              "| type | run answers | C1 check completes | C2 own level passes | own passes over one group |",
              "|---|---|---|---|---|"]
    for typ, group in sorted(by_type.items()):
        lines.append(f"| {typ} | {len(group)} | {ratio(sum(complete(r) for r in group), len(group))} | "
                     f"{ratio(sum(r.get('own') == 'pass' for r in group), len(group))} | "
                     f"{sum(r.get('own') == 'pass' and r.get('groups') == 1 for r in group)} |")
    single = sum(r.get("own") == "pass" and r.get("groups") == 1 for r in population)
    lines.append(f"| all | {len(population)} | {ratio(c1, len(population))} | {ratio(c2, len(population))} | {single} |")
    why = Counter(r.get("why") or next((x["status"] for x in r.get("readings", []) if x["status"] != "ok"), "own unchecked")
                  for r in population if not complete(r))
    lines += ["", "Why a check did not complete: " + (", ".join(f"{k}: {v}" for k, v in why.most_common()) or "-") + ".", ""]

    # C3: the same run of the next task of the same predicted type; pairs with the same answer left out
    order = defaultdict(list)
    for key in sorted(tasks, key=lambda k: (k[1], int(k[2]), k[0])):
        order[tasks[key][0]["predicted"]].append(key)
    pairs = hits = 0
    for keys in order.values():
        for i, key in enumerate(keys):
            other = tasks[keys[(i + 1) % len(keys)]]
            for run in tasks[key]:
                twin = next((o for o in other if o["run"] == run["run"]), None)
                if run["kind"] not in CHECKABLE or twin is None or akey(twin["answer"]) == akey(run["answer"]):
                    continue
                pairs += 1
                hits += any(akey(run["answer"]) in {akey(a) for a in (d.get("answers") or {}).values()}
                            for d in twin.get("derived", []))
    results["C3"] = hits / pairs if pairs else 0.0
    lines += [f"C3 chance control: the own level passes for {ratio(hits, pairs)} answers on the other task's receipt.", ""]

    # allowed readings, cross-fitted by round
    learned = {n: learn([r for r in population if r["split"].startswith(f"r{3 - n}_")]) for n in (1, 2)}
    fmt = lambda s: ", ".join(f"{a}={b}" for a, b in sorted(s)) or "none"  # noqa: E731
    lines += ["## Readings the other round's keys exclude or pin", "",
              "| tasks judged | readings learned from | excluded | pinned (reported only) |", "|---|---|---|---|"]
    lines += [f"| round {n} | round {3 - n} | {fmt(info['excluded'])} | {fmt(info['pinned'])} |" for n, info in learned.items()]
    lines.append("")

    unanimous = {k: v for k, v in tasks.items() if v[0]["unanimous"]}
    g = gate_checks(unanimous, learned)
    results.update(C4=g["C4"], C5=g["C5"], C6=g["C6"])
    lines += gate_lines(g, "The gate")

    # C7
    disagree = [v for v in tasks.values() if len({akey(r["answer"]) for r in v}) > 1]
    in_readings = sum(any(akey(v[0]["key"]) == a for r in v for x in r.get("readings", []) for _, a in combos(x))
                      for v in disagree)
    in_runs = sum(any(akey(v[0]["key"]) == akey(r["answer"]) for r in v) for v in disagree)
    lines += [f"C7 rescue (reported only), {len(disagree)} tasks whose runs disagree: the key is among the declared "
              f"readings' answers in {ratio(in_readings, len(disagree))}, among the runs' answers in "
              f"{ratio(in_runs, len(disagree))}.", ""]

    if args.original:
        orig = [r for r in load(args.original) if r["kind"] in CHECKABLE]
        results["C8"] = sum(complete(r) for r in orig) / len(orig) if orig else 0.0
        lines += [f"C8 portability: checks complete for {ratio(sum(complete(r) for r in orig), len(orig))} of ReAct's "
                  "checkable answers on the original org.", ""]

    lines += ["## Against the committed thresholds", "", "| check | value | GO if | result |", "|---|---|---|---|"]
    for name, (op, bar) in THRESHOLDS.items():
        if name in results:
            value = results[name]
            shown, bar_shown = (f"{value}", f"{bar}") if name == "C6" else (f"{100 * value:.1f}%", f"{100 * bar:.0f}%")
            lines.append(f"| {name} | {shown} | {'at least' if op == '>=' else 'at most'} {bar_shown} | "
                         f"{'pass' if passes(name, value) else 'FAIL'} |")
    if not (passes("C1", results["C1"]) and passes("C2", results["C2"])):
        ok_types = {t for t, group in by_type.items()
                    if passes("C1", sum(complete(r) for r in group) / len(group))
                    and passes("C2", sum(r.get("own") == "pass" for r in group) / len(group))}
        restricted = gate_checks(unanimous, learned, ok_types)
        lines += ["", f"C1 or C2 failed overall, so the development log restricts the gate to the types that pass both: "
                  f"{', '.join(sorted(ok_types)) or 'none'}.", ""]
        lines += gate_lines(restricted, "The gate on those types")
        lines += ["| check | value | GO if | result |", "|---|---|---|---|"]
        for name in ("C4", "C5", "C6"):
            op, bar = THRESHOLDS[name]
            value = restricted[name]
            shown, bar_shown = (f"{value}", f"{bar}") if name == "C6" else (f"{100 * value:.1f}%", f"{100 * bar:.0f}%")
            lines.append(f"| {name} (restricted) | {shown} | {'at least' if op == '>=' else 'at most'} {bar_shown} | "
                         f"{'pass' if passes(name, value) else 'FAIL'} |")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
