"""Receipts: the read-only queries an answer rests on, kept so anyone can re-run them.

Wrap the function your agent uses to query the database in a `Recorder`; every call is kept as a `Receipt`
(the query, its rows and a hash of them). `recheck` re-runs receipts later, against the live database, and says
which still return the same rows. Rows are compared as a multiset: order is ignored, numbers compare by value,
and fields named in `volatile` (timestamps a database updates on every read) are dropped first.
"""
import hashlib
import json
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

Rows = list[dict]
QueryFn = Callable[[str], Rows]


def _canon(value):
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        return {k: _canon(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_canon(v) for v in value]
    return str(value)


def _row_key(row: dict, volatile: frozenset) -> str:
    return json.dumps(_canon({k: v for k, v in row.items() if k not in volatile}), sort_keys=True)


def rows_hash(rows: Rows, volatile: Iterable[str] = ()) -> str:
    keys = sorted(_row_key(r, frozenset(volatile)) for r in rows)
    return hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest()


@dataclass
class Receipt:
    n: int
    query: str
    rows: Rows
    sha256: str
    error: str | None = None

    def to_json(self) -> dict:
        return {"n": self.n, "query": self.query, "rows": self.rows, "sha256": self.sha256, "error": self.error}


@dataclass
class Recorder:
    """Wraps a read-only query function and keeps a receipt of every call. Pass `recorder` (it is callable) to the
    agent instead of the raw function."""
    run: QueryFn
    volatile: frozenset = frozenset()
    receipts: list[Receipt] = field(default_factory=list)

    def __call__(self, query: str) -> Rows:
        try:
            rows = list(self.run(query))
        except Exception as e:  # the agent sees the error; the receipt keeps it
            self.receipts.append(Receipt(len(self.receipts) + 1, query, [], "", error=f"{type(e).__name__}: {e}"))
            raise
        self.receipts.append(Receipt(len(self.receipts) + 1, query, rows, rows_hash(rows, self.volatile)))
        return rows


@dataclass(frozen=True)
class Recheck:
    n: int
    query: str
    status: str  # match | mismatch | error | skipped
    recorded: int
    live: int | None
    detail: str = ""


def recheck(receipts: Iterable[Receipt], run: QueryFn, volatile: Iterable[str] = (), contained: bool = False) -> list[Recheck]:
    """Re-run each receipt's query with `run` and compare rows. With `contained`, a recorded result only has to be
    contained in the live one (use it when the agent's view of a result was cut to fit)."""
    vol = frozenset(volatile)
    out = []
    for r in receipts:
        if r.error:
            out.append(Recheck(r.n, r.query, "skipped", 0, None, "the recorded call failed"))
            continue
        try:
            live = list(run(r.query))
        except Exception as e:
            out.append(Recheck(r.n, r.query, "error", len(r.rows), None, f"{type(e).__name__}: {e}"))
            continue
        want, got = Counter(_row_key(x, vol) for x in r.rows), Counter(_row_key(x, vol) for x in live)
        same = (not (want - got)) if contained else want == got
        detail = "" if same else f"{sum((want - got).values())} recorded rows missing live, {sum((got - want).values())} new"
        out.append(Recheck(r.n, r.query, "match" if same else "mismatch", len(r.rows), len(live), detail))
    return out
