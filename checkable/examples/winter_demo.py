"""A one-minute tour of checkable on an in-memory SQLite table of support cases (made-up rows, no model calls).

An "agent" (here a stand-in function) answers "Which state had the most cases in winter of 2023?" by reading
winter 2023 as December 2022 to February 2023. The question has three defensible readings. Without conventions the
check cannot release the answer; after learning from two answered questions that this organisation means
December 2023 to February 2024, the check holds the agent's answer back for the right reason and the reading table
shows why. Last, the agent's receipt is re-run after the data changes.

  python examples/winter_demo.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from checkable import Recorder, check, learn, recheck, run_readings  # noqa: E402

CASES = [("TX", "2022-12-05"), ("TX", "2023-01-10"), ("CA", "2023-02-01"),
         ("CA", "2023-12-03"), ("CA", "2024-01-15"), ("TX", "2024-02-20"),
         ("NY", "2021-12-10"), ("NY", "2022-01-11"), ("TX", "2022-02-14")]

con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE cases (state TEXT, created TEXT)")
con.executemany("INSERT INTO cases VALUES (?, ?)", CASES)


def run(query: str) -> list[dict]:  # read-only: the check only ever runs SELECTs
    return [dict(r) for r in con.execute(query)]


def query_for(reading) -> str:
    """The agent's deciding query, rewritten for one reading's window."""
    return (f"SELECT state, COUNT(*) AS n FROM cases WHERE created >= '{reading.start:%Y-%m-%d}' "
            f"AND created < '{reading.end:%Y-%m-%d}' GROUP BY state ORDER BY n DESC, state")


def top_state(rows: list[dict]):
    return rows[0]["state"] if rows else None


# 1. The agent answers through a Recorder, so its query is kept as a receipt.
recorder = Recorder(run)
rows = recorder("SELECT state, COUNT(*) AS n FROM cases WHERE created >= '2022-12-01' AND created < '2023-03-01' "
                "GROUP BY state ORDER BY n DESC, state")
answer = top_state(rows)
question = "Which state had the most cases in winter of 2023?"
print(f"agent: {answer}  (from receipt 1: {recorder.receipts[0].query})\n")

# 2. Every reading of the question, with no conventions: the answer changes with the reading.
print(check(question, None, answer, query_for, top_state, run).table(), "\n")

# 3. Learn the organisation's conventions from questions it has already answered.
answered = [("most cases in winter of 2021?", "NY"), ("most cases in winter of 2022?", "TX")]
conventions = learn([(run_readings(q, None, query_for, top_state, run), key) for q, key in answered], min_tasks=2)
print("pinned:", sorted(conventions.pinned), "\nexcluded:", sorted(conventions.excluded), "\n")

# 4. The same answer under the learned conventions: only the organisation's reading is asked.
print(check(question, None, answer, query_for, top_state, run, conventions=conventions).table(), "\n")

# 5. Anyone can re-run the receipt later; after a correction to the data it no longer reproduces.
print("recheck now:", [r.status for r in recheck(recorder.receipts, run)])
con.execute("UPDATE cases SET state = 'CA' WHERE created = '2023-01-10'")
print("after an edit:", [(r.status, r.detail) for r in recheck(recorder.receipts, run)])
