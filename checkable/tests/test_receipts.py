import sqlite3

import pytest

from checkable import Recorder, recheck


@pytest.fixture
def db():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE cases (id TEXT, state TEXT, amount REAL)")
    con.executemany("INSERT INTO cases VALUES (?, ?, ?)", [("c1", "TX", 10), ("c2", "CA", 5.5), ("c3", "TX", 2)])
    return con


def run_on(con):
    return lambda q: [dict(r) for r in con.execute(q)]


def test_recorder_keeps_every_call_and_errors(db):
    rec = Recorder(run_on(db))
    rec("SELECT state, COUNT(*) AS n FROM cases GROUP BY state")
    with pytest.raises(sqlite3.OperationalError):
        rec("SELECT nope FROM cases")
    assert [r.n for r in rec.receipts] == [1, 2]
    assert rec.receipts[0].rows == [{"state": "CA", "n": 1}, {"state": "TX", "n": 2}]
    assert rec.receipts[1].error.startswith("OperationalError")


def test_recheck_matches_ignores_order_and_number_type_then_sees_a_change(db):
    rec = Recorder(run_on(db))
    rec("SELECT id, amount FROM cases")
    out = recheck(rec.receipts, lambda q: list(reversed([{"id": r["id"], "amount": int(r["amount"]) if r["amount"] == int(r["amount"]) else r["amount"]}
                                                       for r in run_on(db)(q)])))
    assert out[0].status == "match"
    db.execute("UPDATE cases SET amount = 11 WHERE id = 'c1'")
    out = recheck(rec.receipts, run_on(db))
    assert out[0].status == "mismatch" and "1 recorded rows missing live" in out[0].detail


def test_recheck_contained_and_volatile_fields(db):
    rec = Recorder(lambda q: [{"id": "c1", "viewed": "t0"}])
    rec("SELECT id FROM cases LIMIT 1")
    live = lambda q: [{"id": "c1", "viewed": "t9"}, {"id": "c2", "viewed": "t9"}]  # noqa: E731
    assert recheck(rec.receipts, live, volatile=["viewed"])[0].status == "mismatch"
    assert recheck(rec.receipts, live, volatile=["viewed"], contained=True)[0].status == "match"
