"""Round 3 of checkable answers, by the pre-registered procedure (docs/checkable3_plan.md): the original org.

  vendor/CRMArena/.venv/Scripts/python scripts/rewrite_recheck.py --records checkable3_calibration \
      --out runs/checkable3_calibration/rewrites.jsonl
  vendor/CRMArena/.venv/Scripts/python scripts/rewrite_recheck.py --records checkable3_calibration_react \
      --out runs/checkable3_calibration/rewrites_react.jsonl
  python scripts/checkable3_report.py --stage calibration   # certify; commit results/checkable3_rules.json first
  (the test half's runs and re-checks, the same way, and recheck_receipts.py on its evidence)
  python scripts/checkable3_report.py --stage test          # apply the committed rules unchanged

The frozen inputs are results/checkable3_frozen.json (the chain's competence maps and flag level, from the
development run D1) and data/conventions_original.yaml (the pinned readings, from D1's used tasks). Stage 1
writes results/checkable3_calibration.md and results/checkable3_rules.json; stage 2 writes
results/checkable3_answers.md and results/checkable3_decisions.json.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import checkable2_report as C2  # noqa: E402
import checkable_report as CR  # noqa: E402
import convention_gate as CG  # noqa: E402
import learn_conventions as LC  # noqa: E402
import release3 as R3  # noqa: E402

RE = R3.RE
ROOT = Path(__file__).resolve().parents[1]
ALPHA = DELTA = 0.10
FROZEN = ROOT / "results" / "checkable3_frozen.json"
CONVENTIONS = ROOT / "data" / "conventions_original.yaml"
RULES = ROOT / "results" / "checkable3_rules.json"
SPLITS = {name: (ROOT / "runs" / f"checkable3_{name}", ROOT / "data" / f"checkable3_{name}.json")
          for name in ("calibration", "test")}


def react_run(base: Path) -> Path:
    return Path(",".join(str(d / "react") for d in [base / "react", *sorted(base.glob("react_p*"))]))


def tasks_of(system: str, split: str) -> list:
    base, ids = SPLITS[split]
    if system == "crmroute":
        return RE.load_tasks(C2.crm_runs(base), ids)
    return RE.load_tasks([react_run(base)], ids, base / "r1" / "routed")


def gate_of(system: str, split: str) -> R3.Gate:
    base, _ = SPLITS[split]
    rows = CG.load(base / ("rewrites.jsonl" if system == "crmroute" else "rewrites_react.jsonl"))
    return R3.Gate(rows, LC.pins_of(CONVENTIONS))


def chain(gate: R3.Gate, frozen: dict, runs: int) -> list:
    """The rules in their pre-registered order, built unchanged from results/checkable3_frozen.json. A one-run
    system keeps only the specs that differ for it (one run on gated types, or no gate)."""
    specs = [s for s in frozen["chain"] if runs == 3 or s["runs_used"] == 1 or s["gate"] == "none"]
    return [rule_from(s, gate) for s in specs]


def spec_of(rule) -> dict:
    return {"rule": rule.__name__, "runs_used": rule.runs_used, "gate": rule.gate_kind, "soft": list(rule.soft),
            "withheld_types": sorted(rule.withheld_types)}


WITHHOLD_ALL = R3.make_rule(3, "none", None, (), frozenset(RE.specs.SPECS) | {None})
WITHHOLD_ALL.__name__ = "none (no rule certified: every answer is withheld)"


def rule_from(spec: dict, gate: R3.Gate):
    if not spec.get("rule"):
        return WITHHOLD_ALL
    rule = R3.make_rule(spec["runs_used"], spec["gate"], gate if spec["gate"] != "none" else None,
                        tuple(spec["soft"]), frozenset(spec["withheld_types"]))
    assert rule.__name__ == spec["rule"], (rule.__name__, spec["rule"])
    return rule


def stage_calibration() -> None:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    rules, lines = {}, ["# Checkable answers, round 3: the certified release rules", "",
                        "```", "python scripts/checkable3_report.py --stage calibration", "```", "",
                        f"Learn-then-Test on the round-3 calibration half (`data/checkable3_calibration.json`), alpha {ALPHA}, "
                        f"delta {DELTA}, over the pre-registered chain (`docs/checkable3_plan.md`). Each table stops at the first "
                        "rule that is not certified; of the certified rules, the one that answers the most calibration tasks is "
                        "chosen. Committed before the test half launches.", ""]
    for system, runs in (("crmroute", 3), ("baseline", 1)):
        tasks = tasks_of("crmroute" if system == "crmroute" else "react", "calibration")
        gate = gate_of("crmroute" if system == "crmroute" else "react", "calibration")
        family = chain(gate, frozen, runs)
        chosen, rows = R3.calibrate_widest(tasks, family, ALPHA, DELTA)
        rules[system] = {**(spec_of(chosen) if chosen else {"rule": None}), "runs_per_task": runs,
                         "calibration_tasks": len(tasks)}
        lines += [f"## {system}", "", RE.TABLE[0] + " p-value | certified |", RE.TABLE[1] + "---|---|"]
        lines += [RE.fmt(r) + f" {r['p']:.4f} | {'yes' if r['certified'] else 'no'} |" for r in rows]
        lines += ["", f"Chosen: **{chosen.__name__ if chosen else 'none (every answer is withheld)'}**", ""]
    RULES.write_text(json.dumps(rules, indent=1) + "\n", encoding="utf-8")
    (ROOT / "results" / "checkable3_calibration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def fisher_one_sided(a: int, b: int, c: int, d: int) -> float:
    """P(X >= a) for the hypergeometric table [[a, b], [c, d]] (rows: held back, passed; columns: wrong, right)."""
    n1, n2, k = a + b, c + d, a + c
    total = math.comb(n1 + n2, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / total


def stage_test(recheck: Path) -> None:
    specs = json.loads(RULES.read_text(encoding="utf-8"))
    tasks = tasks_of("crmroute", "test")
    gate = gate_of("crmroute", "test")
    rule = rule_from(specs["crmroute"], gate)
    row = R3.evaluate(tasks, rule, 0.05)
    made = decisions(tasks, rule)
    lines = ["# Checkable answers, round 3: results on the held-out test half", "",
             "```", "python scripts/checkable3_report.py --stage test", "```", "",
             f"The rule certified on the calibration half (`results/checkable3_calibration.md`), applied unchanged to the "
             f"{len(tasks)} test tasks. Risk is the share of wrong answers among the answers given, with its exact one-sided "
             "95% upper bound.", "",
             "| rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|", RE.fmt(row), ""]
    certified = bool(specs["crmroute"]["rule"])
    lines += ["## Pre-registered primary outcomes (crmroute, three runs)", "",
              f"1. A rule of the chain certified on the calibration half: **{'yes, ' + specs['crmroute']['rule'] if certified else 'no'}**.",
              f"2. Wrong among released test answers at most 10%, and its exact one-sided 95% upper bound at most 10%: "
              f"**{'yes' if certified and row['risk'] <= 0.10 and row['risk_ub'] <= 0.10 else 'no'}** "
              f"({row['wrong']} of {row['released']}, {100 * row['risk']:.1f}%; bound {100 * row['risk_ub']:.1f}%).",
              f"4. {CR.recheck_lines(recheck, made)[0].split('. ', 1)[1]}",
              f"5. At least 50% of the {len(tasks)} test tasks answered: **{'yes' if row['coverage'] >= 0.50 else 'no'}** "
              f"({100 * row['coverage']:.1f}%).",
              "", "(P3, the gate's mechanism outcome, became a secondary analysis when G2 failed: below.)"]
    lines += gate_lines(tasks, gate, rule, json.loads(FROZEN.read_text(encoding="utf-8")))
    lines += ["", "## crmroute's chosen rule by true task type (test)", "", *RE.per_type(tasks, rule)]
    out = ROOT / "results" / "checkable3_answers.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "results" / "checkable3_decisions.json").write_text(json.dumps(made, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))


def unanimous(t) -> bool:
    claims = [r.verdict.claim for r in t.runs]
    return all(c.kind in CG.CHECKABLE for c in claims) and all(RE.rc.same_answer(claims[0], c) for c in claims[1:])


def gate_lines(tasks: list, gate: R3.Gate, rule, frozen: dict) -> list[str]:
    """The pre-registered secondary analysis of the pinned gate (docs/checkable3_plan.md), on its three types
    and on all six: the one-sided Fisher test on unanimous answers; the chosen rule with the gate added; and
    the gate with fewer runs."""
    lines = ["", "## The pinned gate, secondary analysis (test half)", "",
             "| types | unanimous held back: wrong of all | passed: wrong of all | one-sided Fisher p |", "|---|---|---|---|"]
    for label, types in (("its three types", tuple(frozen["gate_types"])), ("all six", R3.GATED)):
        table = [[0, 0], [0, 0]]
        for t in tasks:
            if t.predicted in types and unanimous(t):
                held = CG.task_gate([gate.level(t, i, "pinned") for i in range(3)]) != "pass"
                table[0 if held else 1][0 if t.runs[0].correct < 1 else 1] += 1
        (a, b), (c, d) = table
        p = fisher_one_sided(a, b, c, d) if a + b and c + d else 1.0
        lines.append(f"| {label} | {a} of {a + b} | {c} of {c + d} | {p:.4f} |")
    if rule is WITHHOLD_ALL:
        return lines + ["", "No rule was certified, so the gate is not added to one."]
    lines += ["", "| rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score | runs per task |",
              "|---|---|---|---|---|---|"]
    types = tuple(frozen["gate_types"])
    for runs_used in (3, 2, 1):
        gated = R3.make_rule(runs_used, "pinned", gate, rule.soft, rule.withheld_types, gated_types=types)
        lines.append(RE.fmt(R3.evaluate(tasks, gated, 0.05)) + f" {sum(R3.runs_needed(t, gated) for t in tasks) / len(tasks):.2f} |")
    return lines


def decisions(tasks: list, rule) -> list[dict]:
    """One row per task: released or not, right or not, the released run, the runs a deployment would make."""
    out = []
    for t in tasks:
        released = bool(rule(t))
        run = R3.released_run(t, rule) if released else None
        out.append({"task": list(t.key), "type": t.task_type, "predicted": t.predicted, "released": released,
                    "released_run": 1 if released else None, "right": float(run.correct) if run else 0.0,
                    "answer": list(run.verdict.claim.values) if run else None,
                    "runs_used": R3.runs_needed(t, rule),
                    "cost_all_runs": sum(r.cost or 0 for r in t.runs)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["calibration", "test"], required=True)
    ap.add_argument("--recheck", type=Path, default=SPLITS["test"][0] / "recheck.json")
    args = ap.parse_args()
    if args.stage == "calibration":
        stage_calibration()
    else:
        stage_test(args.recheck)


if __name__ == "__main__":
    main()
