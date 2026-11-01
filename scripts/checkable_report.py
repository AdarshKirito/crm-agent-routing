"""The checkable-answers results, by the pre-registered procedure (docs/checkable_answers.md).

  python scripts/checkable_report.py --stage calibration   # certify the rules; commit before reading any test result
  vendor/CRMArena/.venv/Scripts/python scripts/recheck_receipts.py --runs runs/checkable_test/r1/routed \
      runs/checkable_test/r2/routed runs/checkable_test/f1/full --task-ids data/checkable_test.json \
      --out runs/checkable_test/recheck.json
  python scripts/checkable_report.py --stage test          # apply them unchanged to the test runs

Stage 1 writes results/checkable_calibration.md and results/checkable_rules.json: for each system the
Learn-then-Test table on its calibration runs and the rule it certifies (or none). Stage 2 reads the rules
file, applies each rule to the matching test runs and writes results/checkable_answers.md.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import release_eval as RE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ALPHA = DELTA = 0.10
FORMS = frozenset({"text", "bant"})
CAL, TEST = ROOT / "runs" / "checkable_calibration", ROOT / "runs" / "checkable_test"
SPLITS = {"calibration": ROOT / "data" / "checkable_calibration.json", "test": ROOT / "data" / "checkable_test.json"}
RULES = ROOT / "results" / "checkable_rules.json"


def crm_runs(base: Path) -> list[Path]:
    return [base / "r1" / "routed", base / "r2" / "routed", base / "f1" / "full"]


def react_run(base: Path) -> Path:
    return Path(f"{base / 'react_h1' / 'react_privacy'},{base / 'react_h2' / 'react_privacy'}")


# system name -> (runs of a split, types from, calibration orgs, evaluation orgs)
SYSTEMS = {
    "crmroute": (crm_runs, None, "b2b,b2c", "b2b,b2c"),
    "baseline": (lambda base: [react_run(base)], lambda base: base / "r1" / "routed", "b2b,b2c", "b2b,b2c"),
    "crmroute_run1": (lambda base: crm_runs(base)[:1], None, "b2b,b2c", "b2b,b2c"),
    "crmroute_b2b_to_b2c": (crm_runs, None, "b2b", "b2c"),
}
LABELS = {"crmroute": "crmroute, three runs (two routed, one on 3.8 Flash)",
          "baseline": "ReAct with the privacy prompt, one run",
          "crmroute_run1": "crmroute, first routed run alone",
          "crmroute_b2b_to_b2c": "crmroute, three runs, calibrated on B2B only and applied to B2C"}


def tasks_for(system: str, split: str, mode: str = "single") -> list:
    runs_of, types_of, cal_orgs, eval_orgs = SYSTEMS[system]
    base = CAL if split == "calibration" else TEST
    orgs = (cal_orgs if split == "calibration" else eval_orgs).split(",")
    tasks = RE.load_tasks(runs_of(base), SPLITS[split], types_of(base) if types_of else None, mode)
    return [t for t in tasks if t.key[0] in orgs]


def stage_calibration() -> None:
    rules, lines = {}, ["# Checkable answers: the certified release rules", "",
                        "```", "python scripts/checkable_report.py --stage calibration", "```", "",
                        f"Learn-then-Test on the calibration runs (`data/checkable_calibration.json`), alpha {ALPHA}, "
                        f"delta {DELTA}, the pre-registered family in its order; free-text and BANT answers are never "
                        "released. Each table stops at the first rule that is not certified; the chosen rule is the "
                        "last certified one before it. These choices are committed before any test result is read.", ""]
    for system in SYSTEMS:
        tasks = tasks_for(system, "calibration")
        k = len(tasks[0].runs)
        chosen, rows = RE.calibrate(tasks, RE.default_rules(k, FORMS), ALPHA, DELTA)
        rules[system] = {"rule": chosen.__name__ if chosen else None, "runs_per_task": k, "calibration_tasks": len(tasks)}
        lines += [f"## {LABELS[system]}", "", f"{len(tasks)} calibration tasks, {k} run(s) each.", "",
                  RE.TABLE[0] + " p-value | certified |", RE.TABLE[1] + "---|---|"]
        lines += [RE.fmt(r) + f" {r['p']:.4f} | {'yes' if r['certified'] else 'no'} |" for r in rows]
        lines += ["", f"Certified rule: **{chosen.__name__ if chosen else 'none (every answer is withheld)'}**", ""]
    RULES.write_text(json.dumps(rules, indent=1) + "\n", encoding="utf-8")
    out = ROOT / "results" / "checkable_calibration.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def rule_named(name: str | None, k: int):
    if name is None:
        return RE.withhold_all
    return next(r for r in RE.default_rules(k, FORMS) if r.__name__ == name)


def paired(a: list[float], b: list[float], iters: int = 5000) -> str:
    n = len(a)
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(0)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    return f"{100 * sum(diffs) / n:+.1f} [{100 * boots[int(0.025 * iters)]:+.1f}, {100 * boots[int(0.975 * iters) - 1]:+.1f}]"


def summary_row(label: str, tasks: list, rule) -> tuple[str, dict]:
    row = RE.evaluate(tasks, rule, 0.05)  # the exact 95% upper bound on the test risk
    return (f"| {label} | {rule.__name__} | {row['released']} of {row['tasks']} ({100 * row['coverage']:.1f}%) | "
            f"{row['wrong']} ({100 * row['risk']:.1f}%) | {100 * row['risk_ub']:.1f}% | {100 * row['score']:.1f}% |"), row


def stage_test(recheck: Path, refusal: Path) -> None:
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    lines = ["# Checkable answers: results on the held-out test split", "",
             "```", "python scripts/checkable_report.py --stage test", "```", "",
             "The rules certified on the calibration runs (`results/checkable_calibration.md`), applied unchanged to the "
             "test runs of `data/checkable_test.json` (304 single-turn business tasks, 76 multi-turn). Risk is the share "
             "of wrong answers among the answers given; its upper bound is exact (Clopper-Pearson, 95%). The standard "
             "score counts a withheld answer as a failure, as the benchmark does.", ""]
    head = ["| system | certified rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
            "|---|---|---|---|---|---|"]
    lines += ["## Released answers, single-turn test tasks", "", *head]
    made, results = {}, {}
    for system in SYSTEMS:
        tasks = tasks_for(system, "test")
        rule = rule_named(rules[system]["rule"], rules[system]["runs_per_task"])
        text, row = summary_row(LABELS[system], tasks, rule)
        lines.append(text)
        made[system], results[system] = RE.decisions(tasks, rule), row
    crm = results["crmroute"]
    lines += ["", "## Pre-registered primary outcomes (crmroute, three runs)", "",
              f"1. A rule certified on the calibration split: **{'yes, ' + rules['crmroute']['rule'] if rules['crmroute']['rule'] else 'no'}**.",
              f"2. Risk on the test split at most 10%: **{'yes' if rules['crmroute']['rule'] and crm['risk'] <= 0.10 else 'no'}** "
              f"({100 * crm['risk']:.1f}%, 95% upper bound {100 * crm['risk_ub']:.1f}%).",
              f"3. At least 40% of the 304 single-turn test tasks answered: **{'yes' if crm['coverage'] >= 0.40 else 'no'}** "
              f"({100 * crm['coverage']:.1f}%)."]
    lines += recheck_lines(recheck, made["crmroute"])
    keys = [tuple(d["task"]) for d in made["crmroute"]]
    by = {s: {tuple(d["task"]): d for d in made[s]} for s in ("crmroute", "baseline", "crmroute_run1")}
    lines += ["", f"## crmroute against the baseline, paired on the same {len(keys)} tasks", "",
              "| comparison | coverage, points [95% CI] | standard score, points [95% CI] |", "|---|---|---|"]
    for name, other in (("three runs vs ReAct + privacy", "baseline"), ("first run alone vs ReAct + privacy", "baseline"),
                        ("three runs vs first run alone", "crmroute_run1")):
        mine = "crmroute_run1" if name.startswith("first") else "crmroute"
        lines.append(f"| {name} | {paired([float(by[mine][k]['released']) for k in keys], [float(by[other][k]['released']) for k in keys])} | "
                     f"{paired([by[mine][k]['right'] for k in keys], [by[other][k]['right'] for k in keys])} |")
    lines += standard_score_lines()
    tasks = tasks_for("crmroute", "test")
    lines += ["", "## Repeats, latency and cost (crmroute, three runs)", "", *RE.repeat_table(tasks), ""]
    used = sum(d["runs_used"] for d in made["crmroute"]) / len(made["crmroute"])
    lines.append(f"With adaptive repeats (runs taken one at a time, routed runs first, until the decision is settled; "
                 f"the same decisions) the certified rule needs {used:.2f} runs per task: "
                 f"${sum(d['cost_adaptive'] for d in made['crmroute']) / len(made['crmroute']):.4f} per task instead of "
                 f"${sum(d['cost_all_runs'] for d in made['crmroute']) / len(made['crmroute']):.4f}.")
    rule = rule_named(rules["crmroute"]["rule"], 3)
    lines += ["", "## crmroute's certified rule by true task type (test)", "", *RE.per_type(tasks, rule)]
    lines += multi_turn_lines(rules)
    lines += refusal_lines(refusal)
    out = ROOT / "results" / "checkable_answers.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "results" / "checkable_decisions.json").write_text(json.dumps(made, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))


def recheck_lines(recheck: Path, decisions: list[dict]) -> list[str]:
    if not recheck.exists():
        return ["4. Evidence of released answers reproduced live: not measured yet (run recheck_receipts.py)."]
    entries = json.loads(recheck.read_text(encoding="utf-8"))["entries"]
    released = {(tuple(d["task"]), d["released_run"]) for d in decisions if d["released"]}
    mine = [e for e in entries if (tuple(e["task"]), e["run"]) in released and "entry" in e]
    match = sum(e["status"] == "match" for e in mine)
    sosl_ok = sum(e["status"] == "mismatch" and e["tool"] == "sosl_search" for e in mine)
    missing = [e for e in entries if e.get("status") == "answer_ids_missing_live" and (tuple(e["task"]), e["run"]) in released]
    share = (match + sosl_ok) / len(mine) if mine else 0.0
    return [f"4. Evidence behind released answers reproduced live (at least 99%): **{'yes' if share >= 0.99 else 'no'}**: "
            f"{match} of {len(mine)} entries reproduced exactly, {sosl_ok} SOSL searches ranked differently "
            f"(their answer Ids are checked separately); released Id answers with an Id missing live: {len(missing)}."]


def standard_score_lines() -> list[str]:
    rows = {"crmroute routed run 1": RE.load_run(TEST / "r1" / "routed"), "crmroute routed run 2": RE.load_run(TEST / "r2" / "routed"),
            "crmroute 3.8 Flash run": RE.load_run(TEST / "f1" / "full"), "ReAct + privacy": RE.load_run(react_run(TEST))}
    keys = sorted(k for k in RE.expected_keys(SPLITS["test"]) if not k[1] and rows["ReAct + privacy"][k]["task_type"] not in RE.CONFIDENTIALITY)
    ok = {name: [RE.score(r[k], 0.5)[1] for k in keys] for name, r in rows.items()}
    lines = ["", "## Standard benchmark score of each run (every answer given), single-turn test tasks", "",
             "| run | right | vs ReAct + privacy, points [95% CI] |", "|---|---|---|"]
    for name, values in ok.items():
        diff = "" if name == "ReAct + privacy" else paired(values, ok["ReAct + privacy"])
        lines.append(f"| {name} | {int(sum(values))} of {len(values)} ({100 * sum(values) / len(values):.1f}%) | {diff} |")
    return lines


def multi_turn_lines(rules: dict) -> list[str]:
    lines = ["", "## Multi-turn test tasks (descriptive, not certified: conversations are another distribution)", "",
             "| system | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|---|"]
    for system, runs in (("crmroute_run1", [TEST / "r1" / "routed"]), ("baseline", [react_run(TEST)])):
        types = TEST / "r1" / "routed" if system == "baseline" else None
        tasks = RE.load_tasks(runs, SPLITS["test"], types, "multi")
        text, _ = summary_row(LABELS[system], tasks, rule_named(rules[system]["rule"], 1))
        lines.append(text)
    return lines


def refusal_lines(refusal: Path) -> list[str]:
    if not refusal.exists():
        return ["", "Refusal re-check: not run."]
    rows = RE.load_run(refusal)
    refused = [RE.score(r, 0.5)[1] for r in rows.values() if r["task_type"] in RE.CONFIDENTIALITY]
    return ["", "## Refusal re-check (regressions only)", "",
            f"The old test split's {len(refused)} confidential requests, re-run once with this image: "
            f"{int(sum(refused))} refused ({100 * sum(refused) / len(refused):.1f}%); the held-out test run of "
            "2026-10-02 refused 39 of 42 (92.9%) with the routed system."]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["calibration", "test"], required=True)
    ap.add_argument("--recheck", type=Path, default=TEST / "recheck.json")
    ap.add_argument("--refusal", type=Path, default=ROOT / "runs" / "checkable_refusal" / "routed")
    args = ap.parse_args()
    if args.stage == "calibration":
        stage_calibration()
    else:
        stage_test(args.recheck, args.refusal)


if __name__ == "__main__":
    main()
