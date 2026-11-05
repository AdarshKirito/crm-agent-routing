"""Round-3 go/no-go arithmetic: gate levels, cross-fitted exclusions and the task rule, on synthetic runs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "dev"))
import gonogo as G

TX, MO = ["value", ["tx"]], ["value", ["mo"]]


def reading(year, answer, status="ok", **tie):
    return {"choices": [["season_year", year]], "status": status,
            "answers": tie or {"*": answer} if status == "ok" else None}


def run(answer=TX, key=MO, own="pass", readings=(), **extra):
    return {"org": "b2b", "task": "1", "answer": answer, "key": key, "own": own, "readings": list(readings), **extra}


def test_levels_need_the_own_level_and_every_reading_to_give_the_answer():
    assert G.level(run(readings=[reading("december_of_y", TX), reading("december_before_y", TX)])) == "pass"
    assert G.level(run(readings=[reading("december_of_y", MO), reading("december_before_y", TX)])) == "fail"
    assert G.level(run(own="fail", readings=[reading("december_of_y", TX)])) == "fail"
    assert G.level(run(readings=[reading("december_of_y", TX), reading("december_before_y", None, "error")])) == "unchecked"
    assert G.level(run(own="unchecked", why="no applicable query")) == "unchecked"
    assert G.complete(run(readings=[reading("december_of_y", MO)])) and not G.complete(run(own="unchecked"))


def test_an_excluded_reading_is_not_asked():
    r = run(readings=[reading("december_of_y", TX), reading("december_before_y", MO)])
    assert G.level(r) == "fail" and G.level(r, {("season_year", "december_before_y")}) == "pass"


def test_keys_exclude_a_reading_no_run_supports_and_one_contradicts():
    learned = G.learn([run(readings=[reading("december_of_y", MO), reading("december_before_y", TX)])])
    assert learned["excluded"] == {("season_year", "december_before_y")}
    supported = G.learn([run(readings=[reading("december_of_y", MO), reading("december_before_y", TX)]),
                         run(key=TX, readings=[reading("december_of_y", MO), reading("december_before_y", TX)])])
    assert supported["excluded"] == set()  # each reading has a supporting run


def test_a_reading_some_run_supports_is_kept_and_ties_are_a_slot():
    both = G.learn([run(key=MO, readings=[reading("december_of_y", MO), reading("december_before_y", TX)]),
                    run(key=TX, readings=[reading("december_of_y", MO), reading("december_before_y", TX)])])
    assert ("season_year", "december_of_y") not in both["excluded"]
    tie = G.learn([run(key=TX, readings=[reading("december_of_y", None, none=["none", []], first=TX)])])
    assert tie["excluded"] == {("ties", "none")}


def test_a_task_passes_when_no_run_fails_and_one_passes():
    assert G.task_gate(["pass", "unchecked", "pass"]) == "pass"
    assert G.task_gate(["pass", "fail", "pass"]) == "fail"
    assert G.task_gate(["unchecked"] * 3) == "unchecked"
