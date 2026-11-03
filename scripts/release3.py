"""Round 3's release rules (docs/checkable3_devlog.md): round 2's rules plus a gate on the row-computed types.

A rule considers the first one, two or all three runs of a task (routed run 1, routed run 2, the 3.8 Flash
run), which must all give the same answer and be clean (scripts/release_eval.py clean: no hard flag, none of
the rule's soft flags). On the six types whose answer is computed from query rows (agent/app/derivation.py)
a rule may also gate the answer with scripts/rewrite_recheck.py's live re-check of each considered run's
receipt: no considered run may fail the gate, and at least one must pass it (scripts/convention_gate.py).
Fewer than three runs are allowed only for gated types; every other type needs all three, as in round 2.
Withheld task types and answer forms are never released.

Gate levels: none; "own", the derivation over the run's deciding query, re-run live, reproduces its answer;
"pinned", the deciding query rewritten for each reading the used tasks' keys pin (scripts/learn_conventions.py),
re-run live, gives the answer, the own level deciding questions without readings.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import convention_gate as CG  # noqa: E402
import release_eval as RE  # noqa: E402

GATED = ("best_region_identification", "handle_time", "transfer_count", "monthly_trend_analysis",
         "top_issue_identification", "case_routing")
GATES = ("none", "own", "pinned")


class Gate:
    """Gate levels of each run, from rewrite_recheck.py rows keyed by (org, task id, run number)."""

    def __init__(self, rows: list[dict], pins: dict):
        self.rows = {(r["org"], str(r["task"]), int(r["run"])): r for r in rows}
        self.pins = pins

    def level(self, task: RE.Task, run_index: int, kind: str) -> str:
        row = self.rows.get((task.key[0], str(task.key[2]), run_index + 1))
        if row is None or row["kind"] not in CG.CHECKABLE:
            return "unchecked"
        if kind == "own":
            return row.get("own", "unchecked")
        if kind == "pinned":
            return CG.pinned_level(row, self.pins, own_required=False)
        raise ValueError(f"unknown gate level {kind!r}")


def make_rule(runs_used: int, gate_kind: str, gate: Gate | None, soft: tuple[str, ...] = (),
              withheld_types: frozenset = frozenset(), withheld_forms: frozenset = RE.UNCHECKABLE_FORMS):
    if gate_kind not in GATES or (gate_kind != "none" and gate is None):
        raise ValueError(f"gate {gate_kind!r} needs gate results")
    if runs_used < 3 and gate_kind == "none":
        raise ValueError("fewer than three runs are allowed only with a gate")

    def rule(task: RE.Task) -> bool:
        if task.predicted in withheld_types or RE.specs.spec_for(task.predicted).answer in withheld_forms:
            return False
        gated = gate_kind != "none" and task.predicted in GATED
        considered = task.runs[:runs_used if gated else 3]
        first = considered[0].verdict.claim
        if not all(RE.rc.same_answer(first, r.verdict.claim) and RE.clean(r, soft) for r in considered):
            return False
        if gated:
            return CG.task_gate([gate.level(task, i, gate_kind) for i in range(len(considered))]) == "pass"
        return True

    rule.__name__ = (f"runs 1-{runs_used} agree" if runs_used > 1 else "run 1") + (
        f" on gated types, gate {gate_kind}" if gate_kind != "none" else "") + (
        f", no {'/'.join(soft)}" if soft else "") + (
        f", withhold {len(withheld_types)} types" if withheld_types else "") + (
        f", withhold {'/'.join(sorted(withheld_forms))} answers" if withheld_forms else "")
    rule.runs_used, rule.gate_kind, rule.soft = runs_used, gate_kind, soft
    rule.withheld_types = frozenset(withheld_types)
    return rule


def released_run(task: RE.Task, rule) -> RE.RunAnswer:
    """The run whose answer a released task gives (the first considered run; they all agree)."""
    return task.runs[0]


def runs_needed(task: RE.Task, rule) -> int:
    """Solver runs a deployment makes for this task under `rule`: none for a withheld type, the gated
    types' runs_used for a gated type, three otherwise."""
    if task.predicted in rule.withheld_types:
        return 0
    return rule.runs_used if rule.gate_kind != "none" and task.predicted in GATED else 3


def evaluate(tasks: list[RE.Task], rule, delta: float) -> dict:
    """Coverage, risk (scored on the released run's answer) and its exact upper bound, as release_eval.evaluate."""
    released = [t for t in tasks if rule(t)]
    wrong = int(sum(1 - released_run(t, rule).correct for t in released))
    return {"rule": rule.__name__, "tasks": len(tasks), "released": len(released), "wrong": wrong,
            "coverage": len(released) / len(tasks) if tasks else 0.0,
            "risk": wrong / len(released) if released else 0.0,
            "risk_ub": RE.upper_bound(wrong, len(released), delta),
            "score": (len(released) - wrong) / len(tasks) if tasks else 0.0}


def calibrate_widest(tasks: list[RE.Task], rules: list, alpha: float, delta: float):
    """Fixed-sequence Learn-then-Test over `rules` in their order, stopping at the first that is not
    certified; of the certified rules, the one that answers the most calibration tasks."""
    rows = []
    for rule in rules:
        row = evaluate(tasks, rule, delta)
        row["p"] = RE.binom_cdf(row["wrong"], row["released"], alpha) if row["released"] else 1.0
        row["certified"] = row["p"] <= delta
        rows.append(row)
        if not row["certified"]:
            break
    certified = [(rule, row) for rule, row in zip(rules, rows) if row["certified"]]
    return (max(certified, key=lambda c: c[1]["released"])[0] if certified else None), rows
