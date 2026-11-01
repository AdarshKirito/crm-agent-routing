"""Ask crmroute one question and get a checkable answer, or a handoff.

Sends the question to k independent sessions of a running crmroute server (the container that
scripts/run_systems.sh starts, or `docker run -p 8080:8080 ... crmroute:checkable`), checks every answer
against its receipt (agent/app/receipt_check.py) and applies a release rule from scripts/release_eval.py.
It prints the released answer with the queries and record Ids it rests on, or says it is withheld and why.
The k sessions run in parallel, so the wait is the slowest session's.

  python scripts/ask.py --url http://127.0.0.1:8080 --org b2b --runs 3 \
      "Which agent had the quickest average case handle time in the past 4 months? Today's date: 2021-03-01"
"""
import argparse
import json
import sys
import time
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import release_eval as RE  # noqa: E402

APP, USER = "app", "ask"


def _call(url: str, method: str = "GET", body: dict | None = None, timeout: float = 900.0) -> dict | list:
    request = urllib.request.Request(url, method=method, headers={"Content-Type": "application/json"},
                                     data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def one_session(base: str, org: str, audience: str, context: str, question: str) -> dict:
    session = f"ask-{org}-{uuid.uuid4().hex[:8]}"
    _call(f"{base}/apps/{APP}/users/{USER}/sessions", "POST", {"session_id": session, "state": {
        "crm_org": org, "crm_audience": audience, "crm_interactive": False, "crm_task_context": context}})
    start = time.monotonic()
    _call(f"{base}/run", "POST", {"app_name": APP, "user_id": USER, "session_id": session,
                                  "new_message": {"role": "user", "parts": [{"text": question}]}, "streaming": False})
    state = _call(f"{base}/apps/{APP}/users/{USER}/sessions/{session}").get("state", {})
    return {"answer": state.get("crm_final_response") or "", "receipt": state.get("crm_receipt") or [],
            "route": state.get("crm_route") or {}, "cost": (state.get("crm_usage") or {}).get("total_cost_usd"),
            "latency": time.monotonic() - start}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--org", default="b2b", choices=["b2b", "b2c", "original"])
    ap.add_argument("--customer", action="store_true", help="ask as a logged-in customer (the guard screens it)")
    ap.add_argument("--context", default="", help="task context, e.g. the asker's Contact Id or today's date")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--rule", default="", help="a rule of release_eval's family (default: the strictest)")
    ap.add_argument("--withhold-forms", default="text,bant")
    args = ap.parse_args()

    audience = "customer" if args.customer else "employee"
    with ThreadPoolExecutor(args.runs) as pool:
        sessions = list(pool.map(lambda _: one_session(args.url.rstrip("/"), args.org, audience, args.context,
                                                       args.question), range(args.runs)))
    predicted = sessions[0]["route"].get("task_type")
    form = RE.specs.spec_for(predicted).answer
    runs = [RE.RunAnswer(RE.rc.check(s["answer"], form, s["receipt"], f"{args.question}\n{args.context}", args.question),
                         0.0, s["cost"], s["latency"], s["receipt"]) for s in sessions]
    task = RE.Task(("ask",), predicted or "", predicted, runs)
    family = RE.default_rules(args.runs, frozenset(f for f in args.withhold_forms.split(",") if f))
    rule = next((r for r in family if r.__name__ == args.rule), None) if args.rule else family[0]
    if rule is None:
        raise SystemExit(f"no rule named {args.rule!r}; the family is: {[r.__name__ for r in family]}")

    print(f"task type (router): {predicted}  |  answer form: {form}  |  rule: {rule.__name__}")
    for i, (s, run) in enumerate(zip(sessions, runs), 1):
        print(f"  run {i}: {s['answer'][:100]!r}  flags: {sorted(run.verdict.flags) or 'none'}  "
              f"({s['latency']:.1f} s, ${s['cost'] or 0:.4f})")
    if rule(task):
        best = RE.released_answer(task)
        print(f"\nANSWER: {sessions[runs.index(best)]['answer']}")
        print("Evidence (re-run with scripts/recheck_receipts.py, or paste the queries into any SOQL client):")
        for entry in best.receipt:
            if entry["n"] in best.verdict.support or (best.verdict.claim.kind == "none" and entry.get("totalSize") == 0):
                print(f"  [{entry['n']}] {entry['tool']}: {json.dumps(entry.get('args'))[:300]}  -> {entry.get('totalSize')} rows")
    else:
        reasons = []
        if form in rule.withheld_types or predicted in rule.withheld_types:
            reasons.append(f"answers of form '{form}' cannot be checked against record fields")
        majority = task.majority()
        if len(majority) < rule.min_agree:
            reasons.append(f"only {len(majority)} of {args.runs} runs agree")
        flagged = sorted({f for r in majority for f in r.verdict.flags if f in RE.rc.HARD_FLAGS + rule.soft})
        if flagged:
            reasons.append(f"receipt flags: {', '.join(flagged)}")
        print(f"\nWITHHELD: {'; '.join(reasons) or 'the rule did not release it'}. Hand this request to a person.")
    print(f"\nwait (slowest run): {max(s['latency'] for s in sessions):.1f} s; "
          f"cost (all runs): ${sum(s['cost'] or 0 for s in sessions):.4f}")


if __name__ == "__main__":
    main()
