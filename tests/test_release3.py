"""Round-3 release rules: agreement over the considered runs, the gate on row-computed types, scoring."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import release3 as R3

RE = R3.RE
A, B = "005Wt000003NDqDIAW", "005Wt000003NDqEIAW"


def run(answer, correct=1.0, flags=None):
    claim = RE.rc.Claim("ids", (answer,)) if answer else RE.rc.Claim("text", ("a free-text answer",))
    return RE.RunAnswer(RE.rc.Verdict(claim, flags or {}), correct, 0.01, 1.0)


def task(predicted, *runs, tid="7"):
    return RE.Task(("original", False, tid), predicted, predicted, list(runs))


def gate(*owns, tid="7"):
    rows = [{"org": "original", "task": tid, "run": i + 1, "kind": "ids", "own": own, "readings": []}
            for i, own in enumerate(owns)]
    return R3.Gate(rows, {})


def test_three_runs_must_agree_and_be_clean_without_a_gate():
    rule = R3.make_rule(3, "none", None)
    assert rule(task("handle_time", run(A), run(A), run(A)))
    assert not rule(task("handle_time", run(A), run(A), run(B)))
    assert not rule(task("handle_time", run(A), run(A), run(A, flags={"ungrounded": 1})))


def test_a_gated_type_may_rest_on_fewer_runs_other_types_may_not():
    rule = R3.make_rule(1, "own", gate("pass", "fail", "fail"))
    assert rule(task("handle_time", run(A), run(B), run(B)))  # only run 1 is considered, and it passes
    assert not rule(task("named_entity_disambiguation", run(A), run(B), run(B)))  # not gated: all three
    assert R3.runs_needed(task("handle_time", run(A), run(B), run(B)), rule) == 1


def test_a_failed_or_unchecked_gate_withholds():
    assert not R3.make_rule(2, "own", gate("pass", "fail", "pass"))(task("handle_time", run(A), run(A), run(A)))
    assert not R3.make_rule(3, "own", gate("unchecked", "unchecked", "unchecked"))(task("handle_time", run(A), run(A), run(A)))
    assert R3.make_rule(3, "own", gate("pass", "unchecked", "unchecked"))(task("handle_time", run(A), run(A), run(A)))


def test_free_text_answers_are_never_released_and_a_gate_is_needed_below_three_runs():
    assert not R3.make_rule(3, "none", None)(task("knowledge_qa", run(None), run(None), run(None)))
    with pytest.raises(ValueError):
        R3.make_rule(2, "none", None)


def test_risk_is_scored_on_the_released_run():
    t = task("handle_time", run(A, correct=0.0), run(B), run(B))  # the majority (B) is right, run 1 (A) is not
    row = R3.evaluate([t], R3.make_rule(1, "own", gate("pass", "pass", "pass")), 0.05)
    assert (row["released"], row["wrong"]) == (1, 1)
