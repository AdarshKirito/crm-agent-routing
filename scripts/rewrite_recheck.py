"""Rewrite each run's deciding query for every declared reading and re-run it live (round 3, docs/checkable3_devlog.md).

For each run answer of the six row-computed task types (agent/app/derivation.py):

1. Every successful SOQL query of the run that the type's derivation applies to is re-run live without its
   LIMIT, every row fetched, and derived. The deciding query is the last one whose live rows reproduce the
   run's answer, or, if none does, the last one that derives an answer (the own level then fails).
2. The question's period (scripts/conventions.py) gives one window per combination of declared readings. The
   deciding query's date conditions are replaced by each window, on the reading's date field (CreatedDate
   for the types without a date-field slot), and the rewritten query is re-run live and derived. Date
   conditions inside an OR with other conditions cannot be replaced: that reading is unrewritable.

Handle time also reads the case histories of the run's CaseHistory__c queries, re-run live. Re-runs go
straight to the org with simple_salesforce (recheck_receipts.Org), never through crmroute's server and its
cache. Each distinct query runs once and is kept, with the time it was fetched, in
data/cache/rewrite_recheck/<org>.jsonl. One JSON line per run answer goes to --out; the go/no-go checks are
computed from it (scripts/dev/gonogo.py). Run with the benchmark environment:

  vendor/CRMArena/.venv/Scripts/python scripts/rewrite_recheck.py --records pro --out runs/checkable3_dev/pro.jsonl
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
import conventions as CV  # noqa: E402
import recheck_receipts as RR  # noqa: E402
import release_eval as RE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
D = RE._load("derivation", ROOT / "agent" / "app" / "derivation.py")
CACHE = ROOT / "data" / "cache" / "rewrite_recheck"
FIELDS = r"(?:\w+\.)*(?:CreatedDate|ClosedDate)"
DATE_LITERAL = (r"(?:\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?"
                r"|YESTERDAY|TODAY|TOMORROW|(?:LAST|NEXT|THIS)_\w+(?::\d+)?|N_\w+_AGO:\d+)")
WINDOW_ATOM = re.compile(rf"^(?:{FIELDS}\s*(?:>=|<=|>|<|!=|=)\s*{DATE_LITERAL}"
                         rf"|\w+\(\s*{FIELDS}\s*\)\s*(?:>=|<=|>|<|!=|=|IN)\s*.+)$", re.I | re.S)


# ---- rewriting SOQL -------------------------------------------------------------------------------


def query_of(entry: dict) -> str:
    return str((entry.get("args") or {}).get("query", "")).strip()


def split_query(text: str) -> tuple[str, str, str] | None:
    """(SELECT ... FROM object, WHERE clause or "", the rest: GROUP BY, ORDER BY, LIMIT ...)."""
    at = D.top_keyword(text, "FROM", 6)
    if at < 0:
        return None
    where = D.top_keyword(text, "WHERE", at)
    after = where if where >= 0 else at
    ends = [i for i in (D.top_keyword(text, w, after) for w in ("GROUP", "ORDER", "LIMIT", "OFFSET", "HAVING", "WITH"))
            if i > after]
    end = min(ends) if ends else len(text)
    head = text[:where if where >= 0 else end].strip()
    clause = text[where + 5:end].strip() if where >= 0 else ""
    return head, clause, text[end:].strip()


def split_bool(expr: str, op: str) -> list[str]:
    """The parts of `expr` joined by the top-level boolean operator `op` (AND or OR)."""
    parts, start = [], 0
    while (at := D.top_keyword(expr, op, start)) >= 0:
        parts.append(expr[start:at])
        start = at + len(op)
    parts.append(expr[start:])
    return [p.strip() for p in parts if p.strip()]


def _wrapped(expr: str) -> bool:
    """Whether the parenthesis that opens `expr` is the one that closes it."""
    depth, quote = 0, False
    for i, ch in enumerate(expr):
        if ch == "'" and expr[i - 1:i] != "\\":
            quote = not quote
        elif not quote:
            depth += (ch == "(") - (ch == ")")
            if depth == 0 and i < len(expr) - 1:
                return False
    return depth == 0


def strip_parens(expr: str) -> str:
    expr = expr.strip()
    while expr.startswith("(") and expr.endswith(")") and _wrapped(expr):
        expr = expr[1:-1].strip()
    return expr


def classify(expr: str) -> str:
    """"window" if every condition in `expr` bounds a case date, "other" if none does, else "mixed"."""
    expr = strip_parens(expr)
    for op in ("AND", "OR"):
        parts = split_bool(expr, op)
        if len(parts) > 1:
            kinds = {classify(p) for p in parts}
            return kinds.pop() if len(kinds) == 1 else "mixed"
    if re.match(r"NOT\s", expr, re.I):
        return "other" if classify(expr[4:]) == "other" else "mixed"
    return "window" if WINDOW_ATOM.match(expr) else "other"


def without_limit(tail: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\b(?:LIMIT|OFFSET)\s+\d+\b", " ", tail, flags=re.I)).strip()


def drop_limit(text: str) -> str:
    """The query without its LIMIT and OFFSET; unchanged if it has neither."""
    parts = split_query(text)
    if parts is None or not re.search(r"\b(?:LIMIT|OFFSET)\b", parts[2], re.I):
        return text
    head, clause, tail = parts
    return " ".join(p for p in (head, f"WHERE {clause}" if clause else "", without_limit(tail)) if p)


def rewrite(text: str, field: str, start: datetime, end: datetime) -> str | None:
    """`text` with its date conditions replaced by field >= start AND field < end, and no LIMIT; None if a
    date condition shares an OR with another condition."""
    parts = split_query(text)
    if parts is None:
        return None
    head, clause, tail = parts
    keep = []
    for conjunct in (split_bool(clause, "AND") if clause else []):
        kind = classify(conjunct)
        if kind == "mixed":
            return None
        if kind == "other":
            keep.append(f"({conjunct})" if len(split_bool(conjunct, "OR")) > 1 else conjunct)
    window = f"{field} >= {start:%Y-%m-%dT%H:%M:%SZ} AND {field} < {end:%Y-%m-%dT%H:%M:%SZ}"
    return " ".join(p for p in (head, "WHERE " + " AND ".join(keep + [window]), without_limit(tail)) if p)


# ---- live rows ------------------------------------------------------------------------------------


class Live:
    """Live rows of SOQL queries on one org, each distinct query fetched once and kept on disk."""

    def __init__(self, org: str):
        self.org, self.conn = org, None
        self.path = CACHE / f"{org}.jsonl"
        self.rows_by_query = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                item = json.loads(line)
                self.rows_by_query[item["query"]] = item

    def rows(self, query: str) -> tuple[list[dict], str | None]:
        item = self.rows_by_query.get(query)
        if item is None:
            if self.conn is None:
                self.conn = RR.Org(self.org)
            total, rows, error = self.conn.run("soql_query", query)
            item = {"query": query, "total": total, "rows": rows, "error": error,
                    "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            self.rows_by_query[query] = item
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(item) + "\n")
        return [D.flatten(r) for r in item["rows"]], item["error"]


# ---- one run --------------------------------------------------------------------------------------

HISTORY = D.parse_query("SELECT CaseId__c, Field__c, OldValue__c, NewValue__c, CreatedDate FROM CaseHistory__c")


def case_history(live: Live, queries: list[dict]) -> dict:
    """Owner Assignment histories from the run's CaseHistory__c queries, re-run live, merged."""
    events = {}
    for e in queries:
        q = D.parse_query(query_of(e))
        if q is None or q.obj != "casehistory__c" or q.grouped or not (q.column("CaseId__c") and q.column("NewValue__c")):
            continue
        filtered = re.search(r"Field__c\s*=\s*'Owner Assignment'", query_of(e), re.I)
        if not (q.column("Field__c") or filtered):
            continue
        rows, error = live.rows(drop_limit(query_of(e)))
        for r in [] if error else rows:
            fld = r.get(q.column("Field__c")) if q.column("Field__c") else "Owner Assignment"
            row = {"CaseId__c": r.get(q.column("CaseId__c")), "Field__c": fld, "NewValue__c": r.get(q.column("NewValue__c")),
                   "CreatedDate": r.get(q.column("CreatedDate")) if q.column("CreatedDate") else None}
            events[json.dumps(row, sort_keys=True)] = row
    return D.history_from(list(events.values()), HISTORY)


def product_items(live: Live, queries: list[dict], spec) -> frozenset | None:
    """The question's product's order items, from the run's OrderItem queries that name it, re-run live."""
    if spec.product is None:
        return None
    ids = set()
    for e in queries:
        q = D.parse_query(query_of(e))
        if q is None or q.obj != "orderitem" or spec.product not in query_of(e) or not q.column("Id"):
            continue
        rows, error = live.rows(drop_limit(query_of(e)))
        ids |= {D._id15(r.get(q.column("Id"))) for r in ([] if error else rows)} - {None}
    return frozenset(ids) or None


def answers_of(d, spec) -> dict | None:
    """The answer under each tie reading ({"*": answer} without a tie); None if a tie the context settles."""
    if d.status != "tie":
        return {"*": d.answer}
    if spec.tie_rule:
        return None
    return {"none": d.answer, "first": d.tied[0]}


def jsonable(answers: dict | None):
    return None if answers is None else {k: [a[0], list(a[1])] for k, a in answers.items()}


def check_run(live: Live, spec, task_type: str, receipt: list[dict], claim_key: tuple, period, today) -> dict:
    queries = [e for e in receipt if e.get("status") == "ok" and e.get("tool") == "soql_query"]
    items = product_items(live, queries, spec) if task_type in ("monthly_trend_analysis", "top_issue_identification") else None
    applicable = [e for e in queries if D.derive(spec, query_of(e), [], items=items) is not None]
    out = {"applicable": len(applicable), "derived": [], "deciding": None, "own": "unchecked", "own_answers": None,
           "groups": None, "readings": []}
    if not applicable:
        out["why"] = "no applicable query"
        return out
    history = case_history(live, queries) if task_type == "handle_time" else None
    deciding = None
    for e in applicable:
        rows, error = live.rows(drop_limit(query_of(e)))
        d = None if error else D.derive(spec, query_of(e), rows, history, items)
        answers = None if d is None else answers_of(d, spec)
        out["derived"].append({"n": e["n"], "error": error, "answers": jsonable(answers),
                               "groups": len(d.scores) if d else None})
        if answers is not None:
            if claim_key in answers.values():
                deciding = (e, d, answers, True)
            elif deciding is None or not deciding[3]:
                deciding = (e, d, answers, False)
    if deciding is None:
        out["why"] = "no live re-run derived an answer"
        return out
    e, d, answers, reproduced = deciding
    out.update(deciding=e["n"], own="pass" if reproduced else "fail", own_answers=jsonable(answers), groups=len(d.scores))
    readings = CV.readings(period, task_type, today)
    if period.kind != "none" and not readings:
        out["why"] = "a period with no readings (no today's date)"
    for reading in readings:
        field = reading.field or "CreatedDate"
        text = rewrite(query_of(e), field, reading.start, reading.end)
        item = {"choices": [list(c) for c in reading.choices], "query": text}
        if text is None:
            item["status"] = "unrewritable"
        else:
            rows, error = live.rows(text)
            rd = None if error else D.derive(spec, text, rows, history, items)
            answers = None if rd is None else answers_of(rd, spec)
            item.update(status="error" if error else "unsettled" if answers is None else "ok", error=error,
                        answers=jsonable(answers), groups=len(rd.scores) if rd else None)
        out["readings"].append(item)
    return out


# ---- records --------------------------------------------------------------------------------------


def key_claim(gt, form: str) -> list:
    values = gt if isinstance(gt, list) else [gt]
    if all(v is None for v in values):
        return ["none", []]
    claim = RE.rc.parse_claim(", ".join(str(v) for v in values if v is not None), form)
    return [claim.kind, list(claim.key()[1])]


def pro_records():
    sys.path.insert(0, str(ROOT / "scripts" / "dev"))
    import pro_records as P

    for t in P.load():
        yield t.split, t.task, t.question, t.context, t.key, t.unanimous


def original_react_records():
    """ReAct's recorded trajectories on the original org's test tasks, typed by crmroute's routed run."""
    sys.path.insert(0, str(ROOT / "scripts" / "dev"))
    import pro_records as P

    base = ROOT / "runs" / "original_test"
    first = RE.load_run(base / "react")
    for task in RE.load_tasks([base / "react"], ROOT / "data" / "original_test.json", base / "routed"):
        row = first[task.key]
        yield "original_test", task, RE.question_of(row), P.contexts()["original"][task.key[2]], row.get("gt_answer"), None


def d1_records():
    """Round 3's development run D1: one routed run on the original org's 510 used tasks, as two streams."""
    sys.path.insert(0, str(ROOT / "scripts" / "dev"))
    import pro_records as P

    base = ROOT / "runs" / "checkable3_dev"
    run = Path(f"{base / 'd1_h1' / 'routed'},{base / 'd1_h2' / 'routed'}")
    first = RE.load_run(run)
    for task in RE.load_tasks([run], ROOT / "data" / "checkable3_dev.json"):
        row = first[task.key]
        yield "d1", task, RE.question_of(row), P.contexts()["original"][task.key[2]], row.get("gt_answer"), None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", choices=["pro", "original_react", "d1"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tasks", default="", help="only these org/id pairs, comma-separated (development)")
    ap.add_argument("--env", type=Path, default=ROOT / "vendor" / "CRMArena" / ".env")
    args = ap.parse_args()
    load_dotenv(args.env)
    CV.catalog()
    wanted = {tuple(x.split("/")) for x in args.tasks.split(",") if x}
    lives: dict[str, Live] = {}
    records = {"pro": pro_records, "original_react": original_react_records, "d1": d1_records}[args.records]()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with args.out.open("w", encoding="utf-8") as out:
        for split, task, question, context, gt, unanimous in records:
            org, _, tid = task.key
            if task.predicted not in D.TYPES or (wanted and (org, tid) not in wanted):
                continue
            live = lives.setdefault(org, Live(org))
            spec = D.spec_for(task.predicted, question, context)
            period, today = CV.period_of(question), CV.today_of(context)
            form = RE.specs.spec_for(task.task_type).answer
            for i, run in enumerate(task.runs):
                claim = run.verdict.claim
                row = {"split": split, "org": org, "task": tid, "run": i + 1, "predicted": task.predicted,
                       "type": task.task_type, "kind": claim.kind, "answer": [claim.key()[0], list(claim.key()[1])],
                       "correct": run.correct, "key": key_claim(gt, form), "unanimous": unanimous,
                       "period": {"kind": period.kind, "text": period.text}}
                if claim.kind in ("ids", "none", "value"):
                    row.update(check_run(live, spec, task.predicted, run.receipt, claim.key(), period, today))
                out.write(json.dumps(row) + "\n")
            n += 1
            if n % 25 == 0:
                print(f"{n} tasks", flush=True)
    queries = {org: len(live.rows_by_query) for org, live in lives.items()}
    print(f"done: {n} tasks; distinct live queries kept per org: {queries}")


if __name__ == "__main__":
    main()
