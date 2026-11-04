"""Round 3's non-blind review (docs/checkable3_devlog.md): the 7 wrong released test answers and the 6 keys no reading
reproduces, recomputed from the original org's records under the readings of the question's period and of its policy.

The blinded audit was not conducted, because no reader with the domain knowledge was available. This review is the
author's own, made with the key in view; it says which reading gives the key and which gives crmroute's answer, and
it is reported apart from the certificate.

  vendor/CRMArena/.venv/Scripts/python scripts/dev/checkable3_review.py pull     # read-only SOQL into runs/checkable3_review/
  vendor/CRMArena/.venv/Scripts/python scripts/dev/checkable3_review.py report   # the readings of each task
"""
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "checkable3_review"
sys.path[:0] = [str(ROOT / "checkable" / "src"), str(ROOT / "scripts"), str(ROOT / "vendor" / "CRMArena")]
from checkable import periods  # noqa: E402

TASKS = ("244", "294", "337", "356", "495", "566", "759", "774", "808", "842", "887", "1078", "1081")
QUERIES = {
    "case": "SELECT Id, OwnerId, CreatedDate, ClosedDate, Status, AccountId, Account.ShippingState, IssueId__c, "
            "OrderItemId__c, ContactId, Subject FROM Case",
    "history": "SELECT Id, CaseId__c, OldValue__c, NewValue__c, Field__c, CreatedDate FROM CaseHistory__c",
    "issue": "SELECT Id, Name FROM Issue__c",
    "orderitem": "SELECT Id, Product2Id, OrderId, Order.AccountId, Order.EffectiveDate FROM OrderItem",
    "contact": "SELECT Id, AccountId FROM Contact",
    "product": "SELECT Id, Name FROM Product2",
}


def pull() -> None:
    from dotenv import load_dotenv
    from simple_salesforce import Salesforce
    load_dotenv(ROOT / "vendor" / "CRMArena" / ".env")
    sf = Salesforce(username=os.environ["SALESFORCE_USERNAME"], password=os.environ["SALESFORCE_PASSWORD"],
                    security_token=os.environ["SALESFORCE_SECURITY_TOKEN"], version="62.0")

    def clean(r):
        return {k: (clean(v) if isinstance(v, dict) else v) for k, v in r.items() if k != "attributes"}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, q in QUERIES.items():
        rows = [clean(r) for r in sf.query_all(q)["records"]]
        (OUT / f"{name}.json").write_text(json.dumps(rows), encoding="utf-8")
        print(name, len(rows))


def id15(s):
    return s[:15] if s else s


def ts(s):
    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S") if s else None


class Org:
    def __init__(self):
        load = lambda n: json.loads((OUT / f"{n}.json").read_text(encoding="utf-8"))  # noqa: E731
        self.cases = {id15(c["Id"]): c for c in load("case")}
        self.item_product = {id15(i["Id"]): id15(i["Product2Id"]) for i in load("orderitem")}
        self.items = load("orderitem")
        self.issues = {id15(i["Id"]): i["Name"] for i in load("issue")}
        self.products = {id15(p["Id"]): p["Name"] for p in load("product")}
        self.contacts = {id15(c["Id"]): c for c in load("contact")}
        self.events = defaultdict(list)  # case -> [(when, old owner, new owner)], Owner Assignment rows in time order
        for h in load("history"):
            if h.get("Field__c") == "Owner Assignment":
                self.events[id15(h["CaseId__c"])].append((ts(h["CreatedDate"]), id15(h.get("OldValue__c")),
                                                          id15(h.get("NewValue__c"))))
        for v in self.events.values():
            v.sort(key=lambda e: e[0])

    def product_cases(self, product):
        return [c for c in self.cases.values() if self.item_product.get(id15(c.get("OrderItemId__c"))) == product[:15]]

    def assignees(self, case, scope):
        """Whose case it is for a minimum-case filter: the first agent (the policy), every agent, or the owner."""
        ev = self.events.get(id15(case["Id"]), [])
        if scope == "first agent":
            return {ev[0][2]} if ev else {id15(case["OwnerId"])}
        if scope == "every agent":
            return {e[2] for e in ev} or {id15(case["OwnerId"])}
        return {id15(case["OwnerId"])}


def inside(when, r):
    return when is not None and r.start.replace(tzinfo=None) <= when < r.end.replace(tzinfo=None)


def best(scores, direction):
    if not scores:
        return "None"
    top = (min if direction == "min" else max)(scores.values())
    tied = sorted(k for k, v in scores.items() if abs(v - top) < 1e-9)
    return tied[0] if len(tied) == 1 else "tie " + "/".join(tied)


SCOPES = ("first agent", "every agent", "current owner")


def transfer_count(org, q, today, n_min, direction, average):
    out = []
    for r in periods.readings(q, today):
        cases = [org.cases[c] for c, ev in org.events.items() if c in org.cases and inside(ts(org.cases[c]["CreatedDate"]), r)]
        transfers = Counter(old for c in cases for _, old, _ in org.events[id15(c["Id"])][1:] if old)
        for scope in SCOPES:
            managed = Counter(a for c in cases for a in org.assignees(c, scope))
            for pool in ("every agent", "agents with a transfer"):
                cand = [a for a, m in managed.items() if m > n_min and (pool == "every agent" or transfers[a] > 0)]
                scores = {a: (transfers[a] / managed[a] if average else transfers[a]) for a in cand}
                out.append((f"{r.label()}; filter counts {scope}; ranks {pool}", best(scores, direction)))
    return out


def handle_time(org, q, today, n_min, direction):
    out = []
    for r in periods.readings(q, today):
        window = [c for c in org.cases.values() if c["ClosedDate"] and inside(ts(c["CreatedDate"]), r)]
        durations = defaultdict(list)
        for c in window:
            if len(org.events.get(id15(c["Id"]), [])) <= 1:  # the policy leaves transferred cases out
                durations[id15(c["OwnerId"])].append((ts(c["ClosedDate"]) - ts(c["CreatedDate"])).total_seconds())
        for scope in SCOPES:
            managed = Counter(a for c in window for a in org.assignees(c, scope))
            scores = {a: sum(d) / len(d) for a, d in durations.items() if managed[a] > n_min}
            out.append((f"{r.label()}; filter counts {scope}", best(scores, direction)))
    return out


def top_issue(org, q, today, product):
    out = []
    for r in periods.readings(q, today):
        counts = Counter(id15(c["IssueId__c"]) for c in org.product_cases(product)
                         if c["IssueId__c"] and inside(ts(c["CreatedDate"]), r))
        out.append((f"{r.label()} ({sum(counts.values())} cases)", best(dict(counts), "max")))
    return out


def monthly(org, q, today, product):
    out = []
    for r in periods.readings(q, today):
        per = Counter(ts(c["CreatedDate"]).strftime("%B") for c in org.product_cases(product) if inside(ts(c["CreatedDate"]), r))
        out.append((f"{r.label()} ({dict(per)})", best(dict(per), "max")))
    return out


def best_region(org, q, today):
    out = []
    for r in periods.readings(q, today, {"date_field": ("CreatedDate", "ClosedDate")}):
        field = r.get("date_field")
        d = defaultdict(list)
        for c in org.cases.values():
            state = (c.get("Account") or {}).get("ShippingState")
            if state and c["ClosedDate"] and c["Status"] == "Closed" and inside(ts(c[field]), r):
                d[state].append((ts(c["ClosedDate"]) - ts(c["CreatedDate"])).total_seconds())
        out.append((r.label(), best({s: sum(v) / len(v) for s, v in d.items()}, "min")))
    return out


def case_routing(org, product_name):
    product = next(p for p, n in org.products.items() if n == product_name)
    out = []
    for issue, name in sorted(org.issues.items(), key=lambda kv: kv[1]):
        closed = Counter(id15(c["OwnerId"]) for c in org.cases.values() if id15(c["IssueId__c"]) == issue and c["Status"] == "Closed")
        if not closed:
            continue
        top = max(closed.values())
        tied = [a for a, n in closed.items() if n == top]
        if len(tied) > 1:  # the policy: product expertise, then the fewest open cases
            prod = Counter(id15(c["OwnerId"]) for c in org.product_cases(product) if c["Status"] == "Closed")
            tied = [a for a in tied if prod.get(a, 0) == max(prod.get(b, 0) for b in tied)]
            if len(tied) > 1:
                open_ = Counter(id15(c["OwnerId"]) for c in org.cases.values() if c["Status"] != "Closed")
                tied = [a for a in tied if open_.get(a, 0) == min(open_.get(b, 0) for b in tied)]
        out.append((f"most similar issue = {name}", "/".join(sorted(tied))))
    return out


def purchases(org, contact, day):
    account = org.contacts[contact[:15]]["AccountId"]
    return [(f"bought {day}", f"{id15(i['Product2Id'])} {org.products.get(id15(i['Product2Id']))}") for i in org.items
            if (i.get("Order") or {}).get("AccountId") == account and (i["Order"].get("EffectiveDate") or "") == day]


def report() -> None:
    from crm_sandbox.data import assets
    import release_eval as RE
    spec = importlib.util.spec_from_file_location("derivation", ROOT / "agent" / "app" / "derivation.py")
    D = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(D)
    org = Org()
    tasks = {str(t["idx"]): t for t in assets.TASKS_ORIGINAL}
    runs = [RE.load_run(ROOT / "runs" / "checkable3_test" / d) for d in ("r1/routed", "r2/routed", "f1/full")]
    for tid in TASKS:
        t, key = tasks[tid], ("original", False, tid)
        question, policy = RE.question_of(runs[0][key]), t["metadata"].get("required", "")
        m = re.search(r"Today's date:\s*(\d{4}-\d{2}-\d{2})", policy + question)
        today = date.fromisoformat(m.group(1)) if m else None
        s = D.spec_for(t["task"], question, policy)
        n_min = s.min_cases[0] if s.min_cases else 0
        typ = t["task"]
        if typ == "transfer_count":
            lines = transfer_count(org, question, today, n_min, s.direction, "average" in question.lower())
        elif typ == "handle_time":
            lines = handle_time(org, question, today, n_min, s.direction)
        elif typ == "top_issue_identification":
            lines = top_issue(org, question, today, s.product)
        elif typ == "monthly_trend_analysis":
            lines = monthly(org, question, today, s.product)
        elif typ == "best_region_identification":
            lines = best_region(org, question, today)
        elif typ == "case_routing":
            lines = case_routing(org, "Sport Luxe Sneakers")
        else:
            m = re.search(r"Contact Id interacting:\s*(\w+)", policy)
            lines = purchases(org, m.group(1), "2024-12-03")
        answers = [RE.answer_of(r[key]) or "None" for r in runs]
        print(f"\n## original/{tid} {typ} (today {today})\n{question.splitlines()[0][:300]}")
        print(f"key: {t['answer']}\ncrmroute's runs: {', '.join(answers)}")
        k15, a15 = str(t["answer"])[:15].lower(), {a[:15].lower() for a in answers}
        for label, value in lines:
            v = str(value).lower()
            tags = [n for n, hit in (("key", k15 in v.split("/") or v == k15 or v.startswith(k15 + " ")),
                                     ("crmroute", any(a in v.split("/") or v == a or v.startswith(a + " ") for a in a15))) if hit]
            print(f"  {label}: {value}" + (f"  <- {', '.join(tags)}" if tags else ""))


if __name__ == "__main__":
    {"pull": pull, "report": report}[sys.argv[1] if len(sys.argv) > 1 else "report"]()
