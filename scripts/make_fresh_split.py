"""Write a fresh held-out task list for CRMArena-Pro, disjoint from data/dev.json and data/test.json.

It measures changes made after the test run (for example the guard fixes) on tasks no tuning step has
seen. Defaults, per org:
  - every confidentiality single-turn task not used by dev or test (204 per org),
  - 3 single-turn tasks per business type (57), as in test,
  - 15 more single-turn tasks for each customer-facing business type (knowledge_qa,
    named_entity_disambiguation), so false refusals in customer sessions can be measured,
  - 1 multi-turn task per business type (19).
Ids stay disjoint across modes, as in make_splits.py (single-turn and interactive share ids).

Usage:  python scripts/make_fresh_split.py --out data/fresh.json --seed 20261004
"""
import argparse
import json
import random
from pathlib import Path

from datasets import load_dataset

from make_splits import CONFIDENTIALITY, by_type, take

CUSTOMER_FACING_BUSINESS = ["knowledge_qa", "named_entity_disambiguation"]  # EXTERNAL_FACING_TASKS minus refusals


def used_ids(*paths: Path) -> dict:
    used = {"b2b": set(), "b2c": set()}
    for path in paths:
        split = json.loads(path.read_text(encoding="utf-8"))
        for org in used:
            for ids in split[org].values():
                used[org].update(str(i) for i in ids)
    return used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/fresh.json")
    ap.add_argument("--seed", type=int, default=20261004)
    ap.add_argument("--exclude", nargs="+", default=["data/dev.json", "data/test.json"])
    ap.add_argument("--per-type", type=int, default=3)
    ap.add_argument("--customer-extra-per-type", type=int, default=15)
    ap.add_argument("--mt-per-type", type=int, default=1)
    args = ap.parse_args()

    ds = load_dataset("Salesforce/CRMArenaPro", "CRMArenaPro")
    rng = random.Random(args.seed)
    excluded = used_ids(*[Path(p) for p in args.exclude])
    split = {"seed": args.seed, "excludes": args.exclude}
    for org in ["b2b", "b2c"]:
        single = by_type(ds[org])
        multi = by_type(ds[f"{org}_interactive"])
        business = [t for t in single if t not in CONFIDENTIALITY]
        assert len(business) == 19, business
        # take() compares ids as stored in the dataset; keep the excluded set in that form too
        sample_id = next(iter(single[business[0]]))
        used = {type(sample_id)(i) for i in excluded[org]}
        confidential = sorted((i for t in CONFIDENTIALITY for i in single[t] if i not in used), key=int)
        used.update(confidential)
        business_single = take(rng, single, args.per_type, business, used)
        customer_extra = take(rng, single, args.customer_extra_per_type, CUSTOMER_FACING_BUSINESS, used)
        business_multi = take(rng, multi, args.mt_per_type, business, used)
        split[org] = {"single_turn": sorted(confidential + business_single + customer_extra, key=int),
                      "multi_turn": business_multi}
        split.setdefault("counts", {})[org] = {"confidentiality": len(confidential), "business_single": len(business_single),
                                               "customer_extra": len(customer_extra), "multi_turn": len(business_multi)}
    for org in ["b2b", "b2c"]:
        overlap = excluded[org] & {str(i) for ids in split[org].values() for i in ids}
        assert not overlap, f"{org}: fresh ids overlap dev/test: {sorted(overlap)[:5]}"
    Path(args.out).write_text(json.dumps(split, indent=1), encoding="utf-8")
    print(split["counts"], "->", args.out)


if __name__ == "__main__":
    main()
