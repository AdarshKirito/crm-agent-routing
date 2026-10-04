"""Guard and checker effects of a change, measured on the same tasks before and after it.

Reads two runs of one system on the same split (for example the measured agent and the fixed agent on
data/fresh.json) and reports, paired on task ids:
  - refusal rate on confidential requests, overall, per type, and on the quote-rule wording
    (order quantity limits, products bought together), found with a fixed regex on the request;
  - false refusals: how often customer-facing business requests were refused by the guard;
  - the checker: answers that ended with unverified Ids, and what was sent instead;
  - policy-classifier fallbacks (no usable verdict).
Business accuracy and cost come from scripts/analyze_results.py on the same runs.

Usage:  python scripts/fresh_analysis.py --before runs/fresh_before/routed --after runs/fresh_after/routed \
            --task-ids data/fresh.json --out results/fresh_guard_checker.json
"""
import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_results import CONFIDENTIALITY, expected_keys, load_system, score  # noqa: E402
from judge_agreement import question_of  # noqa: E402

CUSTOMER_BUSINESS = {"knowledge_qa", "named_entity_disambiguation"}  # EXTERNAL_FACING_TASKS minus refusals
QUOTE_RULE_WORDING = re.compile(
    r"\b(how many|maximum|max|limit|at once|single order|in one order|per order|units can)\b"
    r"|\b(together|combined|combine|alongside|along with|in conjunction)\b", re.I)


def paired_diff(before: list[float], after: list[float], iters: int = 5000) -> dict:
    n = len(before)
    diffs = [a - b for a, b in zip(after, before)]
    rng = random.Random(0)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    return {"n": n, "before_pct": round(100 * sum(before) / n, 1), "after_pct": round(100 * sum(after) / n, 1),
            "diff_points": round(100 * sum(diffs) / n, 1),
            "diff_ci95": [round(100 * boots[int(0.025 * iters)], 1), round(100 * boots[int(0.975 * iters) - 1], 1)]}


def guard(row: dict) -> dict:
    return (row.get("agent_info") or {}).get("guard") or {}


def check(row: dict) -> dict:
    return (row.get("agent_info") or {}).get("check") or {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--task-ids", type=Path, required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    before, after = load_system(Path(args.before)), load_system(Path(args.after))
    wanted = expected_keys(args.task_ids)
    keys = sorted(k for k in wanted if k in before and k in after and not before[k].get("error") and not after[k].get("error"))
    report = {"before": args.before, "after": args.after, "task_ids": args.task_ids.as_posix(),
              "paired_tasks": len(keys), "of_expected": len(wanted)}

    conf = [k for k in keys if before[k]["task_type"] in CONFIDENTIALITY]
    refused = lambda rows, ks: [score(rows[k], 0.5)[1] for k in ks]  # noqa: E731 - reward 1 = refused
    report["confidential_refusal"] = {"all": paired_diff(refused(before, conf), refused(after, conf))}
    for t in sorted(CONFIDENTIALITY):
        ks = [k for k in conf if before[k]["task_type"] == t]
        report["confidential_refusal"][t] = paired_diff(refused(before, ks), refused(after, ks))
    quote = [k for k in conf if before[k]["task_type"] == "confidential_company_knowledge"
             and QUOTE_RULE_WORDING.search(question_of(before[k]))]
    report["confidential_refusal"]["quote_rule_wording"] = paired_diff(refused(before, quote), refused(after, quote))

    cust = [k for k in keys if before[k]["task_type"] in CUSTOMER_BUSINESS and not k[1]]
    is_refused = lambda rows, ks: [1.0 if guard(rows[k]).get("decision") == "refuse" else 0.0 for k in ks]  # noqa: E731
    report["customer_business_false_refusal"] = paired_diff(is_refused(before, cust), is_refused(after, cust))
    report["customer_business_success"] = paired_diff([score(before[k], 0.5)[1] for k in cust],
                                                      [score(after[k], 0.5)[1] for k in cust])

    biz = [k for k in keys if before[k]["task_type"] not in CONFIDENTIALITY]
    unverified = lambda rows: [k for k in biz if check(rows[k]).get("unverified") or  # noqa: E731
                               any("do not appear" in p for p in check(rows[k]).get("problems") or [])]
    report["checker"] = {}
    for name, rows in (("before", before), ("after", after)):
        ks = unverified(rows)
        report["checker"][name] = {
            "answers_with_unverified_ids": len(ks),
            "abstained": sum(1 for k in ks if check(rows[k]).get("abstained")),
            "sent_none": sum(1 for k in ks if not check(rows[k]).get("abstained") and not (check(rows[k]).get("answer") or "").strip()),
            "kept_verified_ids": sum(1 for k in ks if (check(rows[k]).get("answer") or "").strip() and not check(rows[k]).get("abstained")),
            "of_which_correct": sum(1 for k in ks if score(rows[k], 0.5)[1] == 1),
            "check_recorded": sum(1 for k in biz if check(rows[k])),
        }
    report["classifier_fallbacks"] = {name: sum(1 for k in keys if "classifier unavailable" in (guard(rows[k]).get("rationale") or ""))
                                      for name, rows in (("before", before), ("after", after))}
    report["guard_sources_after"] = dict(Counter(f"{guard(after[k]).get('source')}:{guard(after[k]).get('decision')}" for k in keys))
    text = json.dumps(report, indent=1)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
