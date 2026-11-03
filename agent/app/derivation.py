"""Derivations: recompute an answer from the rows of one query.

Six task types ask for an answer that is computed from query rows: the state with the quickest mean case
closure (best_region_identification), the agent with the lowest or highest mean handle time (handle_time) or
transfer count (transfer_count), the month with the most cases of a product (monthly_trend_analysis), the
issue reported most for a product (top_issue_identification) and the agent who closed the most cases of an
issue (case_routing). A derivation computes that answer from one query's rows, following the question (its
direction, minimum-case filter and product) and the task context's policy (whether the minimum-case filter
counts the agent a case was transferred to). Handle time also uses the case histories the receipt holds,
because its policy leaves transferred cases out.

The round-3 release layer (docs/checkable3_devlog.md) runs it on the queries of recorded receipts, as recorded
and as rewritten for each declared reading of the question's conventions. It uses the standard library only,
like receipt_check.py, so it loads by file path without the agent package. Answers come back in
receipt_check.Claim.key() form: ("ids", (15-character Id,)), ("value", (lower-case value,)) or ("none", ()).
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

TYPES = ("best_region_identification", "handle_time", "transfer_count", "monthly_trend_analysis",
         "top_issue_identification", "case_routing")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
NONE = ("none", ())
# Salesforce record Ids, the same pattern as receipt_check.ID_RE (a unit test keeps them equal).
ID_RE = re.compile(r"\b(?:[0-9][A-Za-z0-9]{2}|a[0-9][A-Za-z0-9]|k[aA][0-9A-Za-z])[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b")
NUMBER_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10}
LOW = re.compile(r"\b(lowest|least|fewest|minimum|minimal|quickest|fastest|shortest|smallest)\b", re.I)
HIGH = re.compile(r"\b(highest|most|maximum|largest|greatest|longest|slowest|biggest)\b", re.I)
FILTER_WORDS = re.compile(r"\b(at least|more than|fewer than|less than|at most|greater than)\b", re.I)
MIN_CASES = re.compile(r"\b(more than|over|exceeding|greater than|at least)\s+(\d+|[a-z]+)\s+(?:\w+\s+)?cases?\b", re.I)
PRODUCT = re.compile(r"\bproduct Id is\s+([A-Za-z0-9]{15,18})\b", re.I)
FIXED_DIRECTION = {"best_region_identification": "min", "monthly_trend_analysis": "max",
                   "top_issue_identification": "max", "case_routing": "max"}


@dataclass(frozen=True)
class Spec:
    """What the question and the task context fix for a derivation."""
    task_type: str
    direction: str | None  # "min" or "max"; None if the question names neither
    min_cases: tuple[int, bool] | None  # (n, inclusive): "more than 1 case" is (1, False), "at least 1" is (1, True)
    scope: str  # whose cases the minimum-case filter counts: "both" (first and transferee agents) or "first"
    product: str | None  # the product the question names (15 characters)
    tie_rule: bool  # the context settles ties (case routing: product expertise, then workload)


@dataclass(frozen=True)
class Derived:
    status: str  # ok | tie | empty
    answer: tuple  # Claim.key() form; a tie and an empty result give None
    tied: tuple = ()  # on a tie, the tied answers, the one whose group sorts first first
    scores: tuple = ()  # (group, score) of every group, best first

    def answers(self) -> set:
        """The answer under each reading of a tie: None, or the tied group that sorts first."""
        return {self.answer, self.tied[0]} if self.status == "tie" else {self.answer}


def spec_for(task_type: str, question: str, context: str = "") -> Spec:
    question = question or ""
    direction = FIXED_DIRECTION.get(task_type)
    if direction is None:
        text = FILTER_WORDS.sub(" ", question)
        low, high = LOW.search(text), HIGH.search(text)
        if low and high:
            direction = "min" if low.start() < high.start() else "max"
        else:
            direction = "min" if low else "max" if high else None
    min_cases = None
    m = MIN_CASES.search(question)
    if m:
        n = m.group(2).lower()
        n = int(n) if n.isdigit() else NUMBER_WORDS.get(n)
        if n is not None:
            min_cases = (n, m.group(1).lower() == "at least")
    scope = "first" if re.search(r"applies to the first agent", context or "", re.I) else "both"
    p = PRODUCT.search(question)
    return Spec(task_type, direction, min_cases, scope, p.group(1)[:15] if p else None,
                task_type == "case_routing")


# ---- queries and rows ---------------------------------------------------------------------------


def _split_top(text: str) -> list[str]:
    """Comma-separated items outside parentheses."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return [p.strip() for p in parts if p.strip()]


def top_keyword(text: str, word: str, start: int = 0) -> int:
    """Index of the SOQL keyword `word` outside parentheses and quoted strings, or -1."""
    depth, quote = 0, False
    pattern = re.compile(rf"{word}\b", re.I)
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "'" and text[i - 1:i] != "\\":
            quote = not quote
        elif not quote:
            depth += (ch == "(") - (ch == ")")
            if depth == 0 and pattern.match(text, i) and not (text[i - 1:i].isalnum() or text[i - 1:i] == "_"):
                return i
    return -1


@dataclass(frozen=True)
class Query:
    obj: str  # the FROM object, lower case
    columns: tuple  # (expression, row key) of each SELECT item
    grouped: bool
    text: str

    def column(self, *names: str) -> str | None:
        """The row key of the plain field whose last part is one of `names` (case-insensitive)."""
        wanted = {n.lower() for n in names}
        return next((key for expr, key in self.columns if "(" not in expr and expr.split(".")[-1].lower() in wanted), None)

    def aggregate(self, function: str) -> str | None:
        """The row key of the first `function(...)` item, for example COUNT."""
        return next((key for expr, key in self.columns if re.match(rf"{function}\s*\(", expr, re.I)), None)


def parse_query(text: str) -> Query | None:
    """The FROM object and SELECT columns of a SOQL query; None if it is not one. Unaliased aggregates are
    named expr0, expr1, ... in order, as Salesforce names them."""
    text = (text or "").strip()
    if not re.match(r"SELECT\s", text, re.I):
        return None
    at = top_keyword(text, "FROM", 6)
    m = re.match(r"FROM\s+(\w+)", text[at:], re.I) if at >= 0 else None
    if not m:
        return None
    columns, expr_n = [], 0
    for item in _split_top(text[6:at]):
        if item.startswith("("):  # a child-relationship subquery has no column of its own
            continue
        aliased = re.match(r"^(.*\))\s+(\w+)$", item, re.S)
        if aliased:
            columns.append((aliased.group(1).strip(), aliased.group(2)))
        elif "(" in item:
            columns.append((item, f"expr{expr_n}"))
            expr_n += 1
        else:
            columns.append((item, item))
    return Query(m.group(1).lower(), tuple(columns), top_keyword(text, "GROUP", at) >= 0, text)


def flatten(record: dict, prefix: str = "") -> dict:
    """Related records as dotted keys: {"Account": {"ShippingState": "CA"}} -> {"Account.ShippingState": "CA"}."""
    out = {}
    for k, v in record.items():
        if k == "attributes":
            continue
        if isinstance(v, dict):
            out.update(flatten(v, f"{prefix}{k}."))
        else:
            out[f"{prefix}{k}"] = v
    return out


def rows_of(result: str) -> list[dict] | None:
    """The rows of a recorded query result (the Salesforce server's JSON), flattened; None if it holds none."""
    try:
        payload = json.loads(result or "")
    except ValueError:
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        return None
    return [flatten(r) for r in payload["records"] if isinstance(r, dict)]


def _get(row: dict, key: str | None):
    """A row value by key, case-insensitively; the Salesforce server drops empty fields, so a key may be missing."""
    if key is None:
        return None
    if key in row:
        return row[key]
    low = key.lower()
    return next((v for k, v in row.items() if k.lower() == low), None)


def _time(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    text = value.replace("Z", "+0000")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            t = datetime.strptime(text, fmt)
            return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _id15(value) -> str | None:
    return value[:15] if isinstance(value, str) and ID_RE.fullmatch(value) else None


def _number(value) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


# ---- picking ------------------------------------------------------------------------------------


def as_id(group: str) -> tuple:
    return ("ids", (group,))


def as_value(group: str) -> tuple:
    return ("value", (group.lower(),))


def as_month(group: str) -> tuple:  # "2023-05"
    return ("value", (MONTHS[int(group[5:7]) - 1].lower(),))


def pick(scores: dict, direction: str, answer_of) -> Derived:
    """The unique best group (lowest or highest score). Best groups that name the same answer (May of two
    years) count as one; otherwise a shared best score is a tie. No group gives None."""
    if not scores:
        return Derived("empty", NONE)
    ranked = tuple(sorted(scores.items(), key=lambda kv: (kv[1] if direction == "min" else -kv[1], kv[0])))
    best = ranked[0][1]
    answers = list(dict.fromkeys(answer_of(g) for g, s in ranked if abs(s - best) < 1e-9))
    if len(answers) > 1:
        return Derived("tie", NONE, tuple(answers), ranked)
    return Derived("ok", answers[0], (), ranked)


def _passes(count: int, min_cases: tuple[int, bool] | None) -> bool:
    if min_cases is None:
        return count >= 1
    n, inclusive = min_cases
    return count >= n if inclusive else count > n


def history_from(rows: list[dict], query: Query) -> dict:
    """Case Id -> the agents its Owner Assignment rows name, in time order (rows of a CaseHistory__c query)."""
    case, new, fld, when = (query.column("CaseId__c"), query.column("NewValue__c"), query.column("Field__c"),
                            query.column("CreatedDate"))
    if query.obj != "casehistory__c" or query.grouped or not (case and new):
        return {}
    events = defaultdict(list)
    for r in rows:
        if fld and _get(r, fld) != "Owner Assignment":
            continue
        c, agent = _id15(_get(r, case)), _id15(_get(r, new))
        if c and agent:
            events[c].append((_time(_get(r, when)) or datetime.min.replace(tzinfo=timezone.utc), agent))
    return {c: [a for _, a in sorted(v)] for c, v in events.items()}


def _managed(agents: list[str], scope: str) -> set[str]:
    return set(agents) if scope == "both" else {agents[0]}


# ---- the six derivations ------------------------------------------------------------------------


def _counts(rows: list[dict], query: Query, group: str, keep=None) -> dict | None:
    """Score per group: the COUNT (or SUM) column of a grouped query, or the number of rows per group."""
    measure = (query.aggregate("COUNT") or query.aggregate("SUM")) if query.grouped else None
    if query.grouped and measure is None:
        return None
    out: dict = defaultdict(float)
    for r in rows:
        value = _get(r, group)
        if value is None or (keep and not keep(r)):
            continue
        n = _number(_get(r, measure)) if query.grouped else 1.0
        if n is not None:
            out[_id15(value) or str(value)] += n
    return dict(out)


def _product_rows(query: Query, spec: Spec):
    """How rows are limited to the question's product: "query" (its text names the product), a row filter
    (rows carry a product field), or None (they are not, so the query cannot decide)."""
    if spec.product is None or spec.product in query.text:
        return "query"
    col = next((key for expr, key in query.columns if "(" not in expr and expr.lower().endswith("product2id")), None)
    return (lambda r: (_id15(_get(r, col)) or "") == spec.product) if col else None


def _mean_closure(rows, query, group_col, skip=frozenset(), id_col=None) -> dict:
    created, closed = query.column("CreatedDate"), query.column("ClosedDate")
    durations = defaultdict(list)
    for r in rows:
        if id_col and _id15(_get(r, id_col)) in skip:
            continue
        g, a, b = _get(r, group_col), _time(_get(r, created)), _time(_get(r, closed))
        if g is not None and a is not None and b is not None:
            durations[_id15(g) or str(g)].append((b - a).total_seconds())
    return {g: sum(v) / len(v) for g, v in durations.items()}


def derive(spec: Spec, query_text: str, rows: list[dict], history: dict | None = None) -> Derived | None:
    """The type's answer from one query's rows; None if this query cannot decide it (another object, a
    missing field, no direction). `history` (history_from over the receipt's case histories) gives handle
    time its transferred cases and its minimum-case filter the agents of each case."""
    q = parse_query(query_text)
    if q is None or spec.direction is None:
        return None
    t = spec.task_type
    if t == "best_region_identification":
        state = q.column("ShippingState", "BillingState")
        if q.obj != "case" or q.grouped or not (state and q.column("CreatedDate") and q.column("ClosedDate")):
            return None
        return pick(_mean_closure(rows, q, state), spec.direction, as_value)
    if t == "handle_time":
        owner, id_col = q.column("OwnerId"), q.column("Id")
        if q.obj != "case" or q.grouped or not (owner and q.column("CreatedDate") and q.column("ClosedDate")):
            return None
        history = history or {}
        transferred = frozenset(c for c, agents in history.items() if len(agents) > 1)
        means = _mean_closure(rows, q, owner, transferred, id_col)
        managed = Counter()
        for r in rows:
            case, agent = _id15(_get(r, id_col)), _id15(_get(r, owner))
            if case in history:
                managed.update(_managed(history[case], spec.scope))
            elif agent:
                managed[agent] += 1
        return pick({a: m for a, m in means.items() if _passes(managed[a], spec.min_cases)}, spec.direction, as_id)
    if t == "transfer_count":
        old = q.column("OldValue__c")
        if q.obj != "casehistory__c" or not old:
            return None
        if q.grouped:
            counts = _counts(rows, q, old, lambda r: _id15(_get(r, old)))
            return None if counts is None else pick(counts, spec.direction, as_id)
        fld = q.column("Field__c")
        kept = [r for r in rows if not fld or _get(r, fld) == "Owner Assignment"]
        transfers = Counter(a for a in (_id15(_get(r, old)) for r in kept) if a)
        cases = history_from(kept, q)
        if cases:
            managed = Counter()
            for agents in cases.values():
                managed.update(_managed(agents, spec.scope))
            candidates = {a for a, n in managed.items() if _passes(n, spec.min_cases)}
        else:
            candidates = set(transfers)
        return pick({a: transfers[a] for a in candidates}, spec.direction, as_id)
    if t == "monthly_trend_analysis":
        product = _product_rows(q, spec)
        if q.obj != "case" or product is None:
            return None
        keep = None if product == "query" else product
        if q.grouped:
            month = next((key for expr, key in q.columns if re.match(r"CALENDAR_MONTH\s*\(", expr, re.I)), None)
            count = q.aggregate("COUNT")
            if not (month and count):
                return None
            scores = defaultdict(float)
            for r in rows:
                m, n = _number(_get(r, month)), _number(_get(r, count))
                if m and 1 <= m <= 12 and n is not None and (keep is None or keep(r)):
                    scores[MONTHS[int(m) - 1]] += n
            return pick(dict(scores), "max", as_value)
        created = q.column("CreatedDate")
        if not created:
            return None
        per = Counter()
        for r in rows:
            when = _time(_get(r, created))
            if when and (keep is None or keep(r)):
                per[f"{when.year:04d}-{when.month:02d}"] += 1
        return pick(dict(per), "max", as_month)
    if t == "top_issue_identification":
        product, issue = _product_rows(q, spec), q.column("IssueId__c")
        if q.obj != "case" or product is None or not issue:
            return None
        counts = _counts(rows, q, issue, None if product == "query" else product)
        return None if counts is None else pick(counts, "max", as_id)
    if t == "case_routing":
        owner = q.column("OwnerId")
        if q.obj != "case" or not owner:
            return None
        status = None if q.grouped else q.column("Status")
        counts = _counts(rows, q, owner, (lambda r: _get(r, status) == "Closed") if status else None)
        return None if counts is None else pick(counts, "max", as_id)
    return None
