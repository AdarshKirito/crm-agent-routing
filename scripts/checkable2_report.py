"""Round 2 of checkable answers: the competence-map chain, by the pre-registered procedure (docs/checkable_answers.md).

  python scripts/checkable2_report.py --stage calibration   # certify; commit results/checkable2_rules.json first
  vendor/CRMArena/.venv/Scripts/python scripts/recheck_receipts.py --runs runs/checkable2_test/r1/routed \
      runs/checkable2_test/r2/routed runs/checkable2_test/f1/full --task-ids data/checkable2_test.json \
      --out runs/checkable2_test/recheck.json
  python scripts/checkable2_report.py --stage test          # apply the committed rules unchanged

Each system's competence map is learned on its own round-1 runs only (practice, calibration and test of
round 1). Stage 1 writes results/checkable2_calibration.md and results/checkable2_rules.json, with every
chosen rule spelled out (agreement, flags, withheld types) so stage 2 rebuilds it without refitting.
Stage 2 writes results/checkable2_answers.md and results/checkable2_decisions.json.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import checkable_report as CR  # noqa: E402  (round 1's report: the evidence re-check summary)
import release_eval as RE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ALPHA = DELTA = 0.10
FORMS = RE.UNCHECKABLE_FORMS
ROUND1 = {name: (ROOT / "runs" / f"checkable_{name}", ROOT / "data" / f"checkable_{name}.json")
          for name in ("practice", "calibration", "test")}
ROUND2 = {name: (ROOT / "runs" / f"checkable2_{name}", ROOT / "data" / f"checkable2_{name}.json")
          for name in ("calibration", "test")}
OUT = ROOT / "results"
RULES = OUT / "checkable2_rules.json"
ROUND1_RULE = "agree>=3, no budget/none_without_empty/errors, withhold bant/text answers"


def crm_runs(base: Path) -> list[Path]:
    return [base / "r1" / "routed", base / "r2" / "routed", base / "f1" / "full"]


def react_run(base: Path, round1_split: str | None = None) -> Path:
    if round1_split == "practice":
        return base / "react" / "react_privacy"
    if round1_split:  # round 1 ran the baseline's calibration and test as two halves
        return Path(f"{base / 'react_h1' / 'react_privacy'},{base / 'react_h2' / 'react_privacy'}")
    # round 2: one stream per org; the B2B tasks it had not reached ran as three more streams (react_p1..p3)
    return Path(",".join(str(d / "react_privacy") for d in [base / "react", *sorted(base.glob("react_p*"))]))


# system -> (runs per task, runs of a round-2 split, runs of a round-1 split, needs crmroute's router types)
SYSTEMS = {
    "crmroute": (3, crm_runs, lambda base, split: crm_runs(base), False),
    "crmroute_run1": (1, lambda base: crm_runs(base)[:1], lambda base, split: crm_runs(base)[:1], False),
    "baseline": (1, lambda base: [react_run(base)], lambda base, split: [react_run(base, split)], True),
}
LABELS = {"crmroute": "crmroute, three runs (two routed, one on 3.8 Flash)",
          "crmroute_run1": "crmroute, first routed run alone",
          "baseline": "ReAct with the privacy prompt, one run"}


def round1_tasks(system: str) -> list:
    _, _, runs_of, typed = SYSTEMS[system]
    tasks = []
    for split, (base, ids) in ROUND1.items():
        tasks += RE.load_tasks(runs_of(base, split), ids, base / "r1" / "routed" if typed else None)
    return tasks


def round2_tasks(system: str, split: str) -> list:
    _, runs_of, _, typed = SYSTEMS[system]
    base, ids = ROUND2[split]
    return RE.load_tasks(runs_of(base), ids, base / "r1" / "routed" if typed else None)


def spec_of(rule, k: int) -> dict:
    return {"rule": rule.__name__, "runs_per_task": k, "min_agree": rule.min_agree, "soft": list(rule.soft),
            "map_threshold": rule.map_threshold, "withheld_types": rule.map_types}


def rule_from(spec: dict | None):
    if not spec:
        return RE.withhold_all
    bad = frozenset(None if t == "None" else t for t in spec["withheld_types"])
    rule = RE.make_rule(spec["min_agree"], tuple(spec["soft"]), bad, FORMS)
    rule.__name__ = spec["rule"]
    return rule


def stage_calibration() -> None:
    rules, lines = {}, ["# Checkable answers, round 2: the certified release rules", "",
                        "```", "python scripts/checkable2_report.py --stage calibration", "```", "",
                        f"Learn-then-Test on the round-2 calibration runs (`data/checkable2_calibration.json`), alpha {ALPHA}, "
                        f"delta {DELTA}, over the pre-registered chain: each system's competence map is learned on its own "
                        "round-1 runs only. Each table stops at the first rule that is not certified; of the certified rules, "
                        "the one that answers the most calibration tasks is chosen. Committed before any round-2 test result "
                        "is read.", ""]
    for system, (k, *_rest) in SYSTEMS.items():
        dev = round1_tasks(system)
        chain = RE.round2_rules(k, dev, FORMS)
        cal = round2_tasks(system, "calibration")
        chosen, rows = RE.calibrate_widest(cal, chain, ALPHA, DELTA)
        rules[system] = {**(spec_of(chosen, k) if chosen else {"rule": None, "runs_per_task": k}),
                         "calibration_tasks": len(cal), "round1_tasks": len(dev)}
        lines += [f"## {LABELS[system]}", "", f"{len(cal)} calibration tasks, {k} run(s) each; competence maps "
                  f"from {len(dev)} round-1 tasks.", "", RE.TABLE[0] + " p-value | certified | types withheld by the map |",
                  RE.TABLE[1] + "---|---|---|"]
        for rule, row in zip(chain, rows):
            lines.append(RE.fmt(row) + f" {row['p']:.4f} | {'yes' if row['certified'] else 'no'} | "
                         f"{', '.join(rule.map_types) or 'none'} |")
        lines += ["", f"Chosen: **{chosen.__name__ if chosen else 'none (every answer is withheld)'}**", ""]
    RULES.write_text(json.dumps(rules, indent=1) + "\n", encoding="utf-8")
    out = OUT / "checkable2_calibration.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def paired_ci(a: list[float], b: list[float], iters: int = 5000) -> tuple[float, float, float]:
    n = len(a)
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(0)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    return sum(diffs) / n, boots[int(0.025 * iters)], boots[int(0.975 * iters) - 1]


def fmt_ci(ci: tuple[float, float, float]) -> str:
    return f"{100 * ci[0]:+.1f} [{100 * ci[1]:+.1f}, {100 * ci[2]:+.1f}]"


def stage_test(recheck: Path) -> None:
    specs = json.loads(RULES.read_text(encoding="utf-8"))
    lines = ["# Checkable answers, round 2: results on the held-out test split", "",
             "```", "python scripts/checkable2_report.py --stage test", "```", "",
             "The rules certified on the round-2 calibration runs (`results/checkable2_calibration.md`), applied unchanged "
             "to the round-2 test runs (`data/checkable2_test.json`, 431 single-turn business tasks, the benchmark's last "
             "unused ones). Risk is the share of wrong answers among the answers given, with its exact one-sided 95% upper "
             "bound (Clopper-Pearson); the standard score counts a withheld answer as a failure, as the benchmark does.", "",
             "## Released answers, round-2 test", "",
             "| system | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|---|"]
    made, rows, tasks_of = {}, {}, {}
    for system in SYSTEMS:
        tasks = round2_tasks(system, "test")
        rule = rule_from(specs[system] if specs[system]["rule"] else None)
        text, row = CR.summary_row(LABELS[system], tasks, rule)
        lines.append(text)
        made[system], rows[system], tasks_of[system] = RE.decisions(tasks, rule), row, tasks
    # round 1's certified rule, on the same three test runs
    old = RE.make_rule(3, ("budget", "none_without_empty", "errors"), frozenset(), FORMS)
    text, rows["round1_rule"] = CR.summary_row("crmroute, three runs, round 1's certified rule", tasks_of["crmroute"], old)
    lines.append(text)
    made["round1_rule"] = RE.decisions(tasks_of["crmroute"], old)

    crm, spec = rows["crmroute"], specs["crmroute"]
    keys = [tuple(d["task"]) for d in made["crmroute"]]
    by = {s: {tuple(d["task"]): d for d in made[s]} for s in made}
    cov = {other: paired_ci([float(by["crmroute"][k]["released"]) for k in keys], [float(by[other][k]["released"]) for k in keys])
           for other in ("round1_rule", "baseline", "crmroute_run1")}
    score = {other: paired_ci([by["crmroute"][k]["right"] for k in keys], [by[other][k]["right"] for k in keys])
             for other in ("round1_rule", "baseline", "crmroute_run1")}
    certified = bool(spec["rule"])
    lines += ["", "## Pre-registered primary outcomes (crmroute, three runs)", "",
              f"1. A rule of the chain certified on the round-2 calibration split: **{'yes, ' + spec['rule'] if certified else 'no'}**.",
              f"2. Wrong among released test answers at most 10%: **{'yes' if certified and crm['risk'] <= 0.10 else 'no'}** "
              f"({crm['wrong']} of {crm['released']}, {100 * crm['risk']:.1f}%).",
              f"3. Its exact one-sided 95% upper bound at most 10%: **{'yes' if certified and crm['risk_ub'] <= 0.10 else 'no'}** "
              f"({100 * crm['risk_ub']:.1f}%).",
              f"4. At least 50% of the {crm['tasks']} test tasks answered: **{'yes' if crm['coverage'] >= 0.50 else 'no'}** "
              f"({100 * crm['coverage']:.1f}%)."]
    lines += ["5. " + CR.recheck_lines(recheck, made["crmroute"])[0].split(". ", 1)[1]]
    beats = cov["round1_rule"][1] > 0 and cov["baseline"][1] > 0
    lines += [f"6. More test tasks answered than round 1's rule on the same runs and than the baseline under its own "
              f"round-2 rule, both paired intervals above zero: **{'yes' if beats else 'no'}** "
              f"(round 1's rule {fmt_ci(cov['round1_rule'])} points, baseline {fmt_ci(cov['baseline'])} points)."]
    lines += ["", f"## Paired differences on the same {len(keys)} test tasks (crmroute three runs, chosen rule, minus ...)", "",
              "| other | coverage, points [95% CI] | standard score, points [95% CI] |", "|---|---|---|"]
    for other, label in (("round1_rule", "round 1's certified rule, same runs"), ("baseline", "ReAct + privacy, its own round-2 rule"),
                         ("crmroute_run1", "crmroute's first run alone, its own round-2 rule")):
        lines.append(f"| {label} | {fmt_ci(cov[other])} | {fmt_ci(score[other])} |")
    lines += standard_scores()
    tasks = tasks_of["crmroute"]
    lines += ["", "## Repeats, latency and cost (crmroute, three runs)", "", *RE.repeat_table(tasks), ""]
    used = sum(d["runs_used"] for d in made["crmroute"]) / len(made["crmroute"])
    lines.append(f"With adaptive repeats (runs taken one at a time, routed runs first, until the decision is settled; the "
                 f"same decisions; a withheld task type stops after the router) the chosen rule needs {used:.2f} solver runs "
                 f"per task: ${sum(d['cost_adaptive'] for d in made['crmroute']) / len(keys):.4f} per task instead of "
                 f"${sum(d['cost_all_runs'] for d in made['crmroute']) / len(keys):.4f}.")
    lines += ["", "## crmroute's chosen rule by true task type (test)", "", *RE.per_type(tasks, rule_from(spec if certified else None))]
    out = OUT / "checkable2_answers.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "checkable2_decisions.json").write_text(json.dumps(made, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))


def standard_scores() -> list[str]:
    base, ids = ROUND2["test"]
    runs = {"crmroute routed run 1": base / "r1" / "routed", "crmroute routed run 2": base / "r2" / "routed",
            "crmroute 3.8 Flash run": base / "f1" / "full", "ReAct + privacy": react_run(base)}
    rows = {name: RE.load_run(path) for name, path in runs.items()}
    keys = sorted(k for k in RE.expected_keys(ids) if not k[1] and rows["ReAct + privacy"][k]["task_type"] not in RE.CONFIDENTIALITY)
    ok = {name: [RE.score(r[k], 0.5)[1] for k in keys] for name, r in rows.items()}
    lines = ["", "## Standard benchmark score of each run (every answer given), round-2 test", "",
             "| run | right | vs ReAct + privacy, points [95% CI] |", "|---|---|---|"]
    for name, values in ok.items():
        diff = "" if name == "ReAct + privacy" else fmt_ci(paired_ci(values, ok["ReAct + privacy"]))
        lines.append(f"| {name} | {int(sum(values))} of {len(values)} ({100 * sum(values) / len(values):.1f}%) | {diff} |")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["calibration", "test"], required=True)
    ap.add_argument("--recheck", type=Path, default=ROUND2["test"][0] / "recheck.json")
    args = ap.parse_args()
    if args.stage == "calibration":
        stage_calibration()
    else:
        stage_test(args.recheck)


if __name__ == "__main__":
    main()
