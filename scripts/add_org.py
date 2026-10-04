"""Onboard an org crmroute was not built on: the files the agent needs for it, from its own tasks.

- agent/app/data/schema_<org>.md: the org's schema text, built with the benchmark's own
  ChatAgent._build_schema (what the ReAct baseline sees).
- agent/app/data/router_examples_<org>.jsonl: labelled example requests for the task-type router,
  drawn only from tasks NOT in the org's test list. Load them next to the shipped examples with
  CRMROUTE_ROUTER_EXAMPLES=router_examples.jsonl,router_examples_<org>.jsonl.
- data/router_eval_<org>_test.jsonl: the org's test requests with labels, for measuring router
  accuracy only (the agent never loads it).

The org's routing table comes from its own dev runs: scripts/fit_routing.py --org <org>.
Only the original CRMArena org is wired up (its tasks and schema ship with the benchmark).

Usage (CRMArena venv):  python scripts/add_org.py --org original --test data/original_test.json
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", default="original", choices=["original"])
    ap.add_argument("--test", default="data/original_test.json")
    ap.add_argument("--crmarena", default="vendor/CRMArena")
    ap.add_argument("--out-dir", default="agent/app/data")
    ap.add_argument("--eval-out", default="")
    ap.add_argument("--per-type", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    sys.path.insert(0, args.crmarena)
    from crm_sandbox.agents.chat_agent import ChatAgent
    from crm_sandbox.data.assets import SCHEMA_ORIGINAL, TASKS_ORIGINAL

    schema, tasks = {"original": (SCHEMA_ORIGINAL, TASKS_ORIGINAL)}[args.org]
    out = Path(args.out_dir)
    text = ChatAgent._build_schema(None, schema)
    (out / f"schema_{args.org}.md").write_text(text, encoding="utf-8")
    print(f"schema_{args.org}.md: {len(text)} chars")

    test = json.loads(Path(args.test).read_text(encoding="utf-8"))[args.org]
    excluded = {str(i) for ids in test.values() for i in ids}

    def text_of(t):
        context = (t["metadata"] or {}).get("required") or ""
        return f"{t['query'].strip()}\n{context.strip()}".strip()

    by_type = defaultdict(list)
    for t in tasks:
        if str(t["idx"]) not in excluded:
            by_type[t["task"]].append(t)
    rng = random.Random(args.seed)
    examples = [{"org": args.org, "task": task_type, "idx": t["idx"], "text": text_of(t)}
                for task_type, rows in sorted(by_type.items())
                for t in rng.sample(rows, min(args.per_type, len(rows)))]
    path = out / f"router_examples_{args.org}.jsonl"
    path.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in examples) + "\n", encoding="utf-8")
    print(f"{path}: {len(examples)} examples over {len(by_type)} task types (test tasks excluded)")

    rows = [{"org": args.org, "mode": "single_turn", "idx": t["idx"], "task": t["task"], "text": text_of(t)}
            for t in tasks if str(t["idx"]) in excluded]
    eval_path = Path(args.eval_out or f"data/router_eval_{args.org}_test.jsonl")
    eval_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    print(f"{eval_path}: {len(rows)} test requests (evaluation only)")


if __name__ == "__main__":
    main()
