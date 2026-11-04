"""Round 3's secondary outcomes S1-S10 (docs/checkable3_plan.md), computed once from the committed runs and rules.

Run after `checkable3_report.py --stage test`. It reads the same records, re-check rows and committed rules, and
nothing here feeds back into a rule: every figure is reported, none is certified.

  vendor/CRMArena/.venv/Scripts/python scripts/checkable3_secondary.py

Writes results/checkable3_secondary.md, the reading tables of the answers the gate held back
(results/checkable3_reading_tables.md) and the key-reproduction flags (results/checkable3_key_flags.json).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import checkable2_report as C2  # noqa: E402
import checkable3_report as K3  # noqa: E402
import convention_gate as CG  # noqa: E402
import explain_check as EX  # noqa: E402
import learn_conventions as LC  # noqa: E402

R3, RE, ROOT = K3.R3, K3.RE, K3.ROOT
DELTA = 0.05
ROUND2_RULES = ROOT / "results" / "checkable2_rules.json"


def ratio(a: int, b: int) -> str:
    return f"{a} of {b} ({100 * a / b:.1f}%)" if b else f"{a} of 0"


def by_key(tasks: list) -> dict:
    return {t.key: t for t in tasks}


def paired(keys: list, a: dict, b: dict, rule_a, rule_b) -> tuple[str, str]:
    """Paired coverage and standard-score differences (points, bootstrap 95% CI) of rule_a on a minus rule_b on b."""
    rel_a = [float(rule_a(a[k])) for k in keys]
    rel_b = [float(rule_b(b[k])) for k in keys]
    right_a = [float(rule_a(a[k]) and R3.released_run(a[k], rule_a).correct >= 1) for k in keys]
    right_b = [float(rule_b(b[k]) and R3.released_run(b[k], rule_b).correct >= 1) for k in keys]
    return C2.fmt_ci(C2.paired_ci(rel_a, rel_b)), C2.fmt_ci(C2.paired_ci(right_a, right_b))


def held_table(tasks: list, decide) -> tuple[int, int, int, int]:
    """(held-back wrong, held-back right, passed wrong, passed right) over unanimous tasks of the six types."""
    held_w = held_r = pass_w = pass_r = 0
    for t in tasks:
        if t.predicted not in R3.GATED or not K3.unanimous(t):
            continue
        wrong = t.runs[0].correct < 1
        if decide(t) != "pass":
            held_w, held_r = held_w + wrong, held_r + (not wrong)
        else:
            pass_w, pass_r = pass_w + wrong, pass_r + (not wrong)
    return held_w, held_r, pass_w, pass_r


def gate_row(label: str, table: tuple[int, int, int, int]) -> str:
    hw, hr, pw, pr = table
    p = K3.fisher_one_sided(hw, hr, pw, pr) if hw + hr and pw + pr else 1.0
    return (f"| {label} | {ratio(hw, hw + pw)} | {ratio(hr, hr + pr)} | {hw} of {hw + hr} | {pw} of {pw + pr} | "
            f"{p:.4f} |")


GATE_HEAD = ["| gate level | wrong answers held back (catch) | right answers held back (cost) | held back: wrong of all | "
             "passed: wrong of all | one-sided Fisher p |", "|---|---|---|---|---|---|"]


def s1_s10_chain(tasks: list, gate: R3.Gate, frozen: dict, chosen) -> list[str]:
    """S1 and S10's risk-coverage curve: every rule of the frozen chain on the test half, then round 2's six against
    the chosen rule, paired on the same tasks."""
    rules = K3.chain(gate, frozen, 3)
    lines = ["## S1 and S10: the whole chain on the test half (the risk-coverage curve)", "",
             "Every rule of the pre-registered chain (`results/checkable3_frozen.json`), strictest first, applied to the "
             "test half's three runs. Learn-then-Test stopped at rule 10 on the calibration half, so rules 10 to 15 were "
             "never certified; they are shown to draw the curve.", "",
             "| # | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|---|"]
    for i, rule in enumerate(rules, 1):
        mark = " (chosen)" if rule.__name__ == chosen.__name__ else ""
        lines.append(f"| {i}{mark} " + RE.fmt(R3.evaluate(tasks, rule, DELTA)))
    t = by_key(tasks)
    keys = sorted(t)
    lines += ["", "Round 2's six rules (the chain's first six; rules 4 to 6 repeat 1 to 3 because maps 15 and 20 "
              "withhold the same types) against the chosen rule, on the same test tasks:", "",
              "| round 2's rule | chosen minus it: coverage, points [95% CI] | standard score, points [95% CI] |",
              "|---|---|---|"]
    for rule in rules[:3]:
        cov, score = paired(keys, t, t, chosen, rule)
        lines.append(f"| {rule.__name__} | {cov} | {score} |")
    return lines


def s2_s3_gates(tasks: list, gate: R3.Gate, rows: dict, chosen, frozen: dict) -> list[str]:
    """S2 (own level against pinned) and S3 (declared, allowed and pinned readings) on unanimous test answers."""
    conv = yaml.safe_load(K3.CONVENTIONS.read_text(encoding="utf-8"))
    excluded = {(slot, v) for slot, readings in conv["slots"].items() for v, r in readings.items() if r["status"] == "excluded"}
    status = Counter(r["status"] for readings in conv["slots"].values() for r in readings.values())

    def declared(t, exclude=None):
        levels = []
        for i in range(3):
            row = rows.get((t.key[0], str(t.key[2]), i + 1))
            levels.append("unchecked" if row is None or row["kind"] not in CG.CHECKABLE else CG.level(row, exclude))
        return CG.task_gate(levels)

    level = {
        "own": lambda t: CG.task_gate([gate.level(t, i, "own") for i in range(3)]),
        "pinned (the frozen conventions)": lambda t: CG.task_gate([gate.level(t, i, "pinned") for i in range(3)]),
        "allowed (every reading D1's keys do not exclude)": lambda t: declared(t, excluded),
        "declared (every catalog reading)": lambda t: declared(t),
    }
    three = tuple(frozen["gate_types"])
    lines = ["", "## S2 and S3: gate levels on the test half's unanimous answers", "",
             f"The catalog declares {sum(status.values())} readings over {len(conv['slots'])} slots; D1's keys pin "
             f"{status['pinned']}, leave {status['allowed']} allowed and exclude {status.get('excluded', 0)}. With "
             "nothing excluded, the allowed level equals the declared level on this org.", "",
             "All six row-computed types (by predicted type):", "", *GATE_HEAD]
    lines += [gate_row(name, held_table(tasks, f)) for name, f in level.items()]
    sub = [t for t in tasks if t.predicted in three]
    lines += ["", f"The secondary hypothesis's three types ({', '.join(three)}):", "", *GATE_HEAD]
    lines += [gate_row(name, held_table(sub, f)) for name, f in level.items()]
    lines += ["", "The chosen rule with each gate level added on the three types (reported, not certified):", "",
              "| gate | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
              "|---|---|---|---|---|", RE.fmt(R3.evaluate(tasks, chosen, DELTA)).replace(chosen.__name__, "none (the chosen rule)")]
    for kind in ("own", "pinned"):
        gated = R3.make_rule(3, kind, gate, chosen.soft, chosen.withheld_types, gated_types=three)
        lines.append(RE.fmt(R3.evaluate(tasks, gated, DELTA)).replace(gated.__name__, kind))
    return lines


def s5_chance(rows: list[dict]) -> list[str]:
    """S5, the chance control (the go/no-go check C3 on the test half): does a run's answer pass the own level on
    the same run of the next task of its predicted type? Pairs with the same answer are left out."""
    tasks = defaultdict(list)
    for r in rows:
        tasks[r["task"]].append(r)
    order = defaultdict(list)
    for key in sorted(tasks, key=int):
        order[tasks[key][0]["predicted"]].append(key)
    pairs = hits = 0
    for keys in order.values():
        for i, key in enumerate(keys):
            other = tasks[keys[(i + 1) % len(keys)]]
            for run in tasks[key]:
                twin = next((o for o in other if o["run"] == run["run"]), None)
                if run["kind"] not in CG.CHECKABLE or twin is None or CG.akey(twin["answer"]) == CG.akey(run["answer"]):
                    continue
                pairs += 1
                hits += any(CG.akey(run["answer"]) in {CG.akey(a) for a in (d.get("answers") or {}).values()}
                            for d in twin.get("derived", []))
    return ["", "## S5: the chance control", "",
            f"A run's answer, put on the same run of the next task of its predicted type, passes the own level in "
            f"{ratio(hits, pairs)} pairs (test half; the go/no-go bar on the Pro records was at most 10%)."]


def s6_react(crm: list, react: list, chosen, react_rule) -> list[str]:
    """S6: ReAct through the same chain, its certified rule on the test half, paired with crmroute's."""
    c, r = by_key(crm), by_key(react)
    keys = sorted(c.keys() & r.keys())
    cov, score = paired(keys, c, r, chosen, react_rule)
    lines = ["", "## S6: ReAct through the same chain", "",
             "ReAct's rule, certified on the calibration half (`results/checkable3_calibration.md`), on the test half:", "",
             "| system | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|---|",
             "| crmroute, three runs " + RE.fmt(R3.evaluate(crm, chosen, DELTA)),
             "| ReAct, one run " + RE.fmt(R3.evaluate(react, react_rule, DELTA)), "",
             f"crmroute minus ReAct on the same {len(keys)} tasks: coverage {cov} points, standard score {score} points.",
             "", "Standard benchmark score of each run (every answer given, scored as the benchmark does):", "",
             "| run | right | minus ReAct, points [95% CI] |", "|---|---|---|"]
    runs = {"crmroute routed run 1": 0, "crmroute routed run 2": 1, "crmroute 3.8 Flash run": 2}
    base = [r[k].runs[0].correct for k in keys]
    for name, i in runs.items():
        vals = [c[k].runs[i].correct for k in keys]
        lines.append(f"| {name} | {ratio(int(sum(vals)), len(vals))} | {C2.fmt_ci(C2.paired_ci(vals, base))} |")
    lines.append(f"| ReAct | {ratio(int(sum(base)), len(base))} | |")
    lines += ["", "ReAct's rule by true task type (test):", "", *RE.per_type(react, react_rule)]
    return lines


def s7_transfer(halves: dict) -> list[str]:
    """S7: round 2's chosen rule, certified on CRMArena-Pro, applied unchanged to the original org; and round 1's."""
    spec = json.loads(ROUND2_RULES.read_text(encoding="utf-8"))["crmroute"]
    r2 = R3.make_rule(3, "none", None, tuple(spec["soft"]), frozenset(spec["withheld_types"]))
    r1 = R3.make_rule(3, "none", None, ("budget", "none_without_empty", "errors"))
    present = sorted(set(spec["withheld_types"]) & {t.task_type for t in halves["test"]})
    lines = ["", "## S7: round 2's certified rule, frozen and applied unchanged", "",
             f"Round 2's rule (`results/checkable2_rules.json`: {spec['rule']}) withholds five CRMArena-Pro types; of "
             f"them only {', '.join(present) or 'none'} exists on the original org. Both halves are fresh tasks for a "
             "rule fixed before round 3, so both are shown. Its certificate (risk at most 10%) is the question.", "",
             "| tasks | rule | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|---|"]
    for label, tasks in (("test half", halves["test"]), ("calibration half", halves["calibration"]),
                         ("both halves", halves["test"] + halves["calibration"])):
        for name, rule in (("round 2's rule", r2), ("round 1's rule", r1)):
            row = R3.evaluate(tasks, rule, DELTA)
            row["rule"] = name
            lines.append(f"| {label} " + RE.fmt(row))
    return lines


def candidates(run: dict) -> set:
    """Every answer a run's check produced: its own derivation and each reading under each tie reading."""
    out = {CG.akey(a) for d in run.get("derived", []) for a in (d.get("answers") or {}).values()}
    return out | {a for reading in run.get("readings", []) for _, a in CG.combos(reading)}


def s8_s9_keys(rows: list[dict]) -> tuple[list[str], list[dict]]:
    """S8: does some reading's answer hold the key, where the runs disagree? S9: tasks whose key no reading and no
    derivation of any run reproduces (key-reproduction flags, for the audit)."""
    tasks = defaultdict(list)
    for r in rows:
        tasks[r["task"]].append(r)
    disagree = [v for v in tasks.values() if len({CG.akey(r["answer"]) for r in v}) > 1]
    in_readings = sum(any(CG.akey(v[0]["key"]) in candidates(r) for r in v) for v in disagree)
    in_runs = sum(any(CG.akey(v[0]["key"]) == CG.akey(r["answer"]) for r in v) for v in disagree)
    checked = {k: v for k, v in tasks.items() if any(candidates(r) for r in v)}
    flags = [{"task": k, "predicted": v[0]["predicted"], "key": v[0]["key"],
              "answers": sorted({tuple(CG.akey(r["answer"])[1]) for r in v}), "unanimous": v[0]["unanimous"],
              "right": v[0]["correct"] >= 1, "a_run_gives_key": any(r["correct"] >= 1 for r in v)}
             for k, v in sorted(checked.items(), key=lambda kv: int(kv[0]))
             if not any(CG.akey(v[0]["key"]) in candidates(r) for r in v)]
    by_type = Counter(f["predicted"] for f in flags)
    suspect = [f["task"] for f in flags if not f["a_run_gives_key"]]
    gaps = [f["task"] for f in flags if f["a_run_gives_key"]]
    lines = ["", "## S8: do the readings hold the key?", "",
             f"Of the {len(disagree)} test tasks of the six types whose three runs disagree, the key is among the "
             f"answers the declared readings and derivations give in {ratio(in_readings, len(disagree))}, and among the "
             f"runs' own answers in {ratio(in_runs, len(disagree))}.",
             "", "## S9: key-reproduction flags", "",
             f"Of the {len(checked)} tasks whose check produced at least one answer, {len(flags)} have a key that no "
             "derivation and no reading of any run reproduces: "
             + (", ".join(f"{t} {n}" for t, n in by_type.most_common()) or "none") + ".", "",
             f"- **No run gives the key either** ({len(suspect)}: {', '.join(suspect) or '-'}): the key may follow a "
             "convention the catalog does not declare, or be wrong.",
             f"- **Some run gives the key, the check does not** ({len(gaps)}: {', '.join(gaps) or '-'}): a gap in the "
             "derivation, not in the key.", "",
             "All are listed in `results/checkable3_key_flags.json` and go to the blinded audit, which a person has to "
             "carry out; it is not done yet."]
    return lines, flags


def s10_standard(tasks: list, react: list, chosen) -> list[str]:
    """S10: the always-None baseline, errors per type (in checkable3_answers.md), repeats, latency and cost."""
    rows = RE.load_run(ROOT / "runs" / "checkable3_test" / "r1" / "routed")
    none_keys = sum(rows[t.key]["gt_answer"] is None for t in tasks)
    released = [t for t in tasks if chosen(t)]
    none_released = sum(rows[t.key]["gt_answer"] is None for t in released)
    made = K3.decisions(tasks, chosen)
    used = sum(d["runs_used"] for d in made) / len(made)
    react_cost = sum(r.cost or 0 for t in react for r in t.runs) / len(react)
    return ["", "## S10: the standard report", "",
            f"- **Always-None baseline.** Answering \"None\" to every test task is right on {ratio(none_keys, len(tasks))} "
            f"(the share of None keys); of the {len(released)} answers the chosen rule released, {none_released} have a "
            "None key.",
            "- **Errors per type** are in `results/checkable3_answers.md`.", "",
            "Repeats, latency and cost (crmroute, three runs, test half):", "", *RE.repeat_table(tasks), "",
            f"Under the chosen rule a deployment runs no solver on a withheld type, so it makes {used:.2f} solver runs per "
            f"task. ReAct's one run costs ${react_cost:.4f} per task at list price."]


def main() -> None:
    frozen = json.loads(K3.FROZEN.read_text(encoding="utf-8"))
    specs = json.loads(K3.RULES.read_text(encoding="utf-8"))
    crm = {split: K3.tasks_of("crmroute", split) for split in ("calibration", "test")}
    react = K3.tasks_of("react", "test")
    gate = K3.gate_of("crmroute", "test")
    chosen = K3.rule_from(specs["crmroute"], gate)
    react_rule = K3.rule_from(specs["baseline"], K3.gate_of("react", "test"))
    rows = CG.load(K3.SPLITS["test"][0] / "rewrites.jsonl")
    lines = ["# Checkable answers, round 3: secondary outcomes", "",
             "```", "vendor/CRMArena/.venv/Scripts/python scripts/checkable3_secondary.py", "```", "",
             "The pre-registered secondary outcomes (`docs/checkable3_plan.md`), computed once after the primary ones "
             "(`results/checkable3_answers.md`) from the same runs and committed rules. Nothing here is certified and "
             "nothing feeds back into a rule. Risk bounds are exact one-sided 95%; paired intervals are bootstrap 95% "
             "over the same tasks. S4 (readings proposed by the model) was not run, as the plan says.", ""]
    lines += s1_s10_chain(crm["test"], gate, frozen, chosen)
    lines += s2_s3_gates(crm["test"], gate, gate.rows, chosen, frozen)
    lines += s5_chance(rows)
    lines += s6_react(crm["test"], react, chosen, react_rule)
    lines += s7_transfer(crm)
    key_lines, flags = s8_s9_keys(rows)
    lines += key_lines
    lines += s10_standard(crm["test"], react, chosen)
    out = ROOT / "results"
    (out / "checkable3_secondary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "checkable3_key_flags.json").write_text(json.dumps(flags, indent=1) + "\n", encoding="utf-8")

    # reading tables of the unanimous answers the pinned gate held back, the three types first
    pins = LC.pins_of(K3.CONVENTIONS)
    by_task = defaultdict(list)
    for r in rows:
        by_task[r["task"]].append(r)
    held = [t for t in crm["test"] if t.predicted in R3.GATED and K3.unanimous(t)
            and CG.task_gate([gate.level(t, i, "pinned") for i in range(3)]) != "pass"]
    three = set(frozen["gate_types"])
    held.sort(key=lambda t: (t.predicted not in three, t.predicted, int(t.key[2])))
    tables = ["# Round 3: reading tables of the answers the pinned gate held back (test half)", "",
              "Unanimous answers of the six row-computed types that the gate held back, the secondary hypothesis's three "
              "types first; written by `scripts/checkable3_secondary.py` with `scripts/explain_check.py`'s table. "
              "\"asked\" marks the readings the frozen conventions (`data/conventions_original.yaml`) ask.", ""]
    for t in held:
        tables += [f"## original/{t.key[2]} ({t.predicted}, {'right' if t.runs[0].correct >= 1 else 'wrong'})", "", "```"]
        for run in sorted(by_task[str(t.key[2])], key=lambda r: r["run"]):
            tables += EX.table(run, pins)
        tables += ["```", ""]
    (out / "checkable3_reading_tables.md").write_text("\n".join(tables), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
