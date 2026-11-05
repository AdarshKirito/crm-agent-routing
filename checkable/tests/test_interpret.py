import sqlite3
from datetime import date

import pytest

from checkable import Conventions, check, learn, run_readings

CASES = [  # (state, created) - TX leads in Dec 2022-Feb 2023, CA in Dec 2023-Feb 2024
    ("TX", "2022-12-05"), ("TX", "2023-01-10"), ("CA", "2023-02-01"),
    ("CA", "2023-12-03"), ("CA", "2024-01-15"), ("TX", "2024-02-20"),
    ("NY", "2021-12-10"), ("NY", "2022-01-11"), ("TX", "2022-02-14"),
]


@pytest.fixture
def run():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE cases (state TEXT, created TEXT)")
    con.executemany("INSERT INTO cases VALUES (?, ?)", CASES)
    return lambda q: [dict(r) for r in con.execute(q)]


def query_for(reading):
    return (f"SELECT state, COUNT(*) AS n FROM cases WHERE created >= '{reading.start:%Y-%m-%d}' "
            f"AND created < '{reading.end:%Y-%m-%d}' GROUP BY state ORDER BY n DESC, state")


def top_state(rows):
    return rows[0]["state"] if rows else None


def test_an_answer_that_depends_on_the_winter_year_fails(run):
    c = check("Which state had the most cases in winter of 2023?", None, "TX", query_for, top_state, run)
    assert c.decision == "fail"
    assert {r.answer for r in c.results} == {"TX", "CA"}
    assert "[asked]" in c.table()


def test_learned_conventions_ask_only_the_pinned_year(run):
    examples = []
    for year, key in ((2021, "NY"), (2022, "TX")):  # this org reads winter Y as December Y to February Y+1
        results = run_readings(f"most cases in winter of {year}?", None, query_for, top_state, run)
        examples.append((results, key))
    conv = learn(examples, min_tasks=2)
    assert {("season_year", "december_of_y"), ("season_months", "meteorological")} <= conv.pinned
    assert conv.excluded == {("season_year", "december_before_y"), ("season_months", "quarter_aligned")}
    c = check("Which state had the most cases in winter of 2023?", None, "CA", query_for, top_state, run, conventions=conv)
    assert c.decision == "pass" and len(c.asked) == 1
    assert check("Which state had the most cases in winter of 2023?", None, "TX", query_for, top_state, run,
                 conventions=conv).decision == "fail"
    assert Conventions.from_json(conv.to_json()).pinned == conv.pinned


def test_no_period_means_no_readings_and_errors_leave_it_unchecked(run):
    assert check("Which state has the most cases?", None, "TX", query_for, top_state, run).decision == "no_readings"

    def broken(q):
        raise RuntimeError("timeout")
    assert check("cases in winter of 2023", date(2024, 5, 1), "TX", query_for, top_state, broken).decision == "unchecked"
