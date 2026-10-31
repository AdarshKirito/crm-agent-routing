"""Re-run the queries behind recorded answers against the live CRMArena-Pro orgs and compare.

This does not use crmroute's Salesforce MCP server: it connects with simple_salesforce, as the
benchmark's own connector does, with the benchmark's published org logins (vendor/CRMArena/.env,
never printed). For every answer in the given runs it re-runs the receipt entries the answer rests
on: the SOQL/SOSL results that contain the answer's Ids, the empty results behind a "None", and the
knowledge articles a text answer was read from. Live rows are shaped the way the MCP server shapes
them (attributes dropped, child results as lists, text cut at 4,000 characters, empty fields
ignored) and compared with the recorded rows as a multiset; a cut-off recorded result must be
contained in the live one. Identical queries are run once per org.

  vendor/CRMArena/.venv/Scripts/python scripts/recheck_receipts.py --runs runs/checkable_practice/r1/routed \
      --task-ids data/checkable_practice.json --out runs/checkable_practice/recheck.json
"""
import argparse
import ast
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from simple_salesforce import Salesforce

sys.path.insert(0, str(Path(__file__).parent))
import release_eval as RE  # noqa: E402  (loads agent/app/receipt_check.py by path)

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT = 4000  # SF_MAX_TEXT_CHARS of the MCP server
CUT = re.compile(r"\.\.\. \[truncated \d+ chars\]$")
KNOWLEDGE_FIELDS = ("Id", "Title", "Summary", "FAQ_Answer__c")


def shape(value, keep_type: bool = False):
    """The MCP server's cleanRecord, applied to live rows and to recorded ones alike."""
    if isinstance(value, list):
        return [shape(v, keep_type) for v in value]
    if isinstance(value, dict):
        out = {}
        attrs = value.get("attributes")
        if keep_type and isinstance(attrs, dict) and attrs.get("type"):
            out["_type"] = attrs["type"]
        for k, v in value.items():
            if k == "attributes" or v is None:
                continue
            out[k] = shape(v["records"] if isinstance(v, dict) and "records" in v else v)
        return out
    if isinstance(value, str):
        return CUT.sub("", value)[:MAX_TEXT]
    return value


def rows_key(rows: list) -> Counter:
    return Counter(json.dumps(r, sort_keys=True) for r in rows)


class Org:
    def __init__(self, org: str):
        up = org.upper()
        self.sf = Salesforce(username=os.environ[f"SALESFORCE_{up}_USERNAME"], password=os.environ[f"SALESFORCE_{up}_PASSWORD"],
                             security_token=os.environ[f"SALESFORCE_{up}_SECURITY_TOKEN"])
        self.cache: dict = {}

    def run(self, tool: str, query: str):
        key = (tool, query)
        if key not in self.cache:
            try:
                if tool == "sosl_search":
                    found = self.sf.search(query).get("searchRecords") or []
                    self.cache[key] = (len(found), shape(found, keep_type=True), None)
                else:
                    out = self.sf.query_all(query)
                    self.cache[key] = (out["totalSize"], shape(out["records"]), None)
            except Exception as error:  # noqa: BLE001 - a failed re-run is reported, not raised
                self.cache[key] = (None, [], f"{type(error).__name__}: {str(error)[:200]}")
        return self.cache[key]


def support_entries(verdict, receipt: list[dict]) -> list[dict]:
    """The entries an answer rests on."""
    ok = [e for e in receipt if e.get("status") == "ok"]
    claim = verdict.claim
    if claim.kind == "ids":
        return [e for e in ok if e["n"] in verdict.support]
    if claim.kind == "none":
        return [e for e in ok if e.get("totalSize") == 0 and e["tool"] in ("soql_query", "sosl_search")]
    if claim.kind == "text":
        return [e for e in ok if e["tool"] == "search_knowledge" or "Knowledge__kav" in json.dumps(e.get("args"))]
    return [e for e in ok if e["tool"] in ("soql_query", "sosl_search")][-1:]  # values: the last query read


def _literal(node):
    """A Python repr of rows (lists, dicts, OrderedDict([...]), constants), read without eval."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {_literal(k): _literal(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "OrderedDict" and len(node.args) <= 1:
        return {k: v for k, v in (_literal(node.args[0]) if node.args else [])}
    raise ValueError(f"not a row literal: {type(node).__name__}")


def live_ids(org: Org, entry: dict) -> set[str]:
    """Ids in the live rows of an entry that was re-run (empty if it was not)."""
    tool, args = entry["tool"], entry.get("args") or {}
    if tool not in ("soql_query", "sosl_search"):
        return set()
    _, live, _ = org.run(tool, str(args.get("query", "")))
    return {i[:15] for i in RE.rc.ID_RE.findall(json.dumps(live))}


def recheck_entry(org: Org, entry: dict) -> dict:
    """`match`: the live result reproduces the recorded one."""
    tool, args = entry["tool"], entry.get("args") or {}
    text = entry.get("result") or ""
    try:
        recorded = json.loads(text)
    except ValueError:
        try:  # the benchmark's ReAct agent saw a Python repr of its rows (every row, no cut)
            recorded = _literal(ast.parse(text.strip(), mode="eval").body)
        except (ValueError, SyntaxError):
            return {"status": "skipped", "why": "result is neither JSON nor a row list"}
    if isinstance(recorded, list):  # ReAct's rows: every row, no cut
        recorded = {"records": recorded, "totalSize": len(recorded), "truncated": False}
    if tool in ("soql_query", "sosl_search"):
        total, live, error = org.run(tool, str(args.get("query", "")))
        if error:
            return {"status": "error", "why": error}
        rec_rows = shape(recorded.get("records") or [], keep_type=tool == "sosl_search")
        if tool == "sosl_search" and not any("_type" in r for r in rec_rows if isinstance(r, dict)):
            live = [{k: v for k, v in r.items() if k != "_type"} for r in live]  # ReAct's rows carry no type
        cut = bool(recorded.get("truncated"))
        same_rows = (rows_key(rec_rows) <= rows_key(live)) if cut else (rows_key(rec_rows) == rows_key(live))
        if tool == "sosl_search" and not cut:  # SOSL's own order and limits differ between clients: compare row sets
            same_rows = rows_key(rec_rows) <= rows_key(live) and len(rec_rows) == min(len(live), len(rec_rows))
        match = same_rows and (recorded.get("totalSize") == total or tool == "sosl_search")
        return {"status": "match" if match else "mismatch", "recorded_total": recorded.get("totalSize"), "live_total": total}
    if tool == "search_knowledge" or tool == "get_record":
        articles = recorded.get("articles") if tool == "search_knowledge" else [recorded]
        ids = [a.get("Id") for a in articles or [] if isinstance(a, dict) and a.get("Id")]
        if not ids:
            return {"status": "skipped", "why": "no record Ids to fetch"}
        obj = "Knowledge__kav" if tool == "search_knowledge" else str(args.get("object_name"))
        fields = KNOWLEDGE_FIELDS if obj.lower() == "knowledge__kav" else ("Id", *[f for f in recorded if f != "Id"])
        query = f"SELECT {', '.join(dict.fromkeys(fields))} FROM {obj} WHERE Id IN ({', '.join(repr(i) for i in ids)})"
        _, live, error = org.run("soql_query", query)
        if error:
            return {"status": "error", "why": error}
        live_by_id = {r.get("Id", "")[:15]: r for r in live}
        same = all(all(live_by_id.get(a["Id"][:15], {}).get(k) == v for k, v in shape(a).items() if k in fields)
                   for a in articles if isinstance(a, dict) and a.get("Id"))
        return {"status": "match" if same else "mismatch", "records": len(ids)}
    return {"status": "skipped", "why": f"{tool} is not re-run"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", type=Path, required=True)
    ap.add_argument("--task-ids", type=Path, required=True)
    ap.add_argument("--types-from", type=Path, help="crmroute run whose router predictions a ReAct run uses")
    ap.add_argument("--env", type=Path, default=ROOT / "vendor" / "CRMArena" / ".env")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    load_dotenv(args.env)
    orgs: dict[str, Org] = {}
    report, counts = [], Counter()
    for task in RE.load_tasks(args.runs, args.task_ids, args.types_from):
        org = orgs.setdefault(task.key[0], Org(task.key[0]))
        for i, run in enumerate(task.runs):
            entries = support_entries(run.verdict, run.receipt)
            for entry in entries:
                result = recheck_entry(org, entry)
                counts[result["status"]] += 1
                report.append({"task": list(task.key), "run": i + 1, "entry": entry["n"], "tool": entry["tool"], **result})
            if run.verdict.claim.kind == "ids" and entries:
                # every Id of the answer must come back live in some entry the answer rests on
                seen = set().union(*(live_ids(org, e) for e in entries))
                found = all(v[:15] in seen for v in run.verdict.claim.values)
                counts["answers_with_ids_found_live" if found else "answers_with_ids_missing_live"] += 1
                if not found:
                    report.append({"task": list(task.key), "run": i + 1, "status": "answer_ids_missing_live",
                                   "answer": list(run.verdict.claim.values)})
    queries = sum(len(o.cache) for o in orgs.values())
    summary = {"entries": sum(1 for r in report if "entry" in r), **counts, "live_queries_run": queries}
    print(json.dumps(summary, indent=1))
    for r in report:
        if r["status"] in ("mismatch", "error", "skipped", "answer_ids_missing_live"):
            print(r)
    if args.out:
        Path(args.out).write_text(json.dumps({"summary": summary, "entries": report}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
