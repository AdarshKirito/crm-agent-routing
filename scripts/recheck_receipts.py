"""Re-run the queries behind recorded answers against the live CRMArena-Pro orgs and compare.

This does not use crmroute's Salesforce MCP server: it connects with simple_salesforce, as the
benchmark's own connector does, with the benchmark's published org logins (vendor/CRMArena/.env,
never printed). For every answer in the given runs it re-runs the receipt entries the answer rests
on: the SOQL/SOSL results that contain the answer's Ids, the empty results behind a "None", and the
knowledge articles a text answer was read from. Live rows are shaped the way the MCP server shapes
them (attributes dropped, child results as lists, text cut at 4,000 characters, empty fields
ignored, numbers compared by value) and compared with the recorded rows as a multiset; a recorded result that
was cut to fit a response, or thinned by the confidentiality filter, must be contained in the live one. The
re-check uses the MCP server's API version (62.0), so both see the same fields, and ignores the two fields
Salesforce updates on every view (LastViewedDate, LastReferencedDate). Identical queries are run once per org.

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
API_VERSION = "62.0"  # the MCP server's default (mcp-salesforce/src/config.ts): the same fields exist
CUT = re.compile(r"\.\.\. \[truncated \d+ chars\]$")
KNOWLEDGE_FIELDS = ("Id", "Title", "Summary", "FAQ_Answer__c")
# Salesforce updates these whenever anyone views the record (this re-check included): never compared.
VOLATILE = {"LastViewedDate", "LastReferencedDate"}
# A bare COUNT() returns its count as totalSize and no rows; query_all's totalSize counts the rows it fetched.
COUNT_ONLY = re.compile(r"^\s*SELECT\s+COUNT\(\s*\)\s+FROM\b", re.I)


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
            if k == "attributes" or k in VOLATILE or v is None:
                continue
            out[k] = shape(v["records"] if isinstance(v, dict) and "records" in v else v)
        return out
    if isinstance(value, str):
        return CUT.sub("", value)[:MAX_TEXT]
    if isinstance(value, float) and value.is_integer():
        return int(value)  # the MCP server's JSON writes 25, simple_salesforce returns 25.0
    return value


def rows_key(rows: list) -> Counter:
    return Counter(json.dumps(r, sort_keys=True) for r in rows)


class Org:
    def __init__(self, org: str):
        up = org.upper()
        self.sf = Salesforce(username=os.environ[f"SALESFORCE_{up}_USERNAME"], password=os.environ[f"SALESFORCE_{up}_PASSWORD"],
                             security_token=os.environ[f"SALESFORCE_{up}_SECURITY_TOKEN"],
                             version=os.getenv("SALESFORCE_API_VERSION", API_VERSION))
        self.cache: dict = {}

    def get(self, obj: str, record_id: str):
        """One record by Id through the REST API, shaped like the MCP server's get_record."""
        key = ("get", obj, record_id)
        if key not in self.cache:
            try:
                self.cache[key] = (shape(dict(getattr(self.sf, obj).get(record_id))), None)
            except Exception as error:  # noqa: BLE001 - a failed re-run is reported, not raised
                self.cache[key] = ({}, f"{type(error).__name__}: {str(error)[:200]}")
        return self.cache[key]

    def run(self, tool: str, query: str):
        key = (tool, query)
        if key not in self.cache:
            try:
                if tool == "sosl_search":
                    found = self.sf.search(query).get("searchRecords") or []
                    self.cache[key] = (len(found), shape(found, keep_type=True), None)
                else:
                    out = self.sf.query_all(query)
                    total = self.sf.query(query)["totalSize"] if COUNT_ONLY.match(query) else out["totalSize"]
                    self.cache[key] = (total, shape(out["records"]), None)
            except Exception as error:  # noqa: BLE001 - a failed re-run is reported, not raised
                self.cache[key] = (None, [], f"{type(error).__name__}: {str(error)[:200]}")
        return self.cache[key]



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


def _ids(rows) -> list[str]:
    return sorted({i[:15] for i in RE.rc.ID_RE.findall(json.dumps(rows))})


def recheck_entry(org: Org, entry: dict) -> dict:
    """`match`: the live result reproduces the recorded one. `live_ids`: the Ids in the live rows compared."""
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
        # the recorded rows are what the model saw: cut to fit a response, or thinned by the confidentiality
        # filter in a customer session; either way they must all be in the live result
        cut = bool(recorded.get("truncated")) or "withheld_confidential" in recorded
        same_rows = (rows_key(rec_rows) <= rows_key(live)) if cut else (rows_key(rec_rows) == rows_key(live))
        if tool == "sosl_search" and not cut:  # SOSL's own order and limits differ between clients: compare row sets
            same_rows = rows_key(rec_rows) <= rows_key(live) and len(rec_rows) == min(len(live), len(rec_rows))
        match = same_rows and (recorded.get("totalSize") == total or tool == "sosl_search" or cut)
        return {"status": "match" if match else "mismatch", "recorded_total": recorded.get("totalSize"),
                "live_total": total, "live_ids": _ids(live)}
    if tool == "search_knowledge":
        articles = [a for a in recorded.get("articles") or [] if isinstance(a, dict) and a.get("Id")]
        if not articles:
            return {"status": "skipped", "why": "no article Ids to fetch"}
        query = (f"SELECT {', '.join(KNOWLEDGE_FIELDS)} FROM Knowledge__kav "
                 f"WHERE Id IN ({', '.join(repr(a['Id']) for a in articles)})")
        _, live, error = org.run("soql_query", query)
        if error:
            return {"status": "error", "why": error}
        by_id = {r.get("Id", "")[:15]: r for r in live}
        same = all(by_id.get(a["Id"][:15], {}).get(k) == v for a in articles for k, v in shape(a).items()
                   if k in KNOWLEDGE_FIELDS)
        return {"status": "match" if same else "mismatch", "records": len(articles), "live_ids": _ids(live)}
    if tool == "get_record":
        record_id, obj = str(args.get("record_id", "")), str(args.get("object_name", ""))
        live, error = org.get(obj, record_id)
        if error:
            return {"status": "error", "why": error}
        same = all(live.get(k) == v for k, v in shape(recorded).items())
        return {"status": "match" if same else "mismatch", "live_ids": _ids(live)}
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
            entries = RE.support_entries(run.verdict, run.receipt)
            for entry in entries:
                result = recheck_entry(org, entry)
                counts[result["status"]] += 1
                report.append({"task": list(task.key), "run": i + 1, "entry": entry["n"], "tool": entry["tool"], **result})
            if run.verdict.claim.kind == "ids" and entries:
                # every Id of the answer must come back live in some entry the answer rests on
                seen = {i for r in report[-len(entries):] for i in r.get("live_ids") or []}
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
            print({k: v for k, v in r.items() if k != "live_ids"})
    if args.out:
        Path(args.out).write_text(json.dumps({"summary": summary, "entries": report}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
