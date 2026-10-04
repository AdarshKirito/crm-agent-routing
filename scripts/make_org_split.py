"""Write dev and test task-id lists for the original CRMArena org (an org crmroute was not built on).

Dev (fitting the org's routing table) and test (measured once) are disjoint, with the same number of
tasks per type. The original org has single-turn tasks only.

Usage (CRMArena venv):  python scripts/make_org_split.py --out-dir data --seed 20261004
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crmarena", default="vendor/CRMArena")
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--seed", type=int, default=20261004)
    ap.add_argument("--dev-per-type", type=int, default=10)
    ap.add_argument("--test-per-type", type=int, default=10)
    args = ap.parse_args()
    sys.path.insert(0, args.crmarena)
    from crm_sandbox.data.assets import TASKS_ORIGINAL

    by_type = defaultdict(list)
    for t in TASKS_ORIGINAL:
        by_type[t["task"]].append(t["idx"])
    rng = random.Random(args.seed)
    dev, test = [], []
    for task_type in sorted(by_type):
        ids = sorted(by_type[task_type], key=int)
        picked = rng.sample(ids, args.dev_per_type + args.test_per_type)
        test += picked[:args.test_per_type]
        dev += picked[args.test_per_type:]
    assert not set(dev) & set(test)
    for name, ids in (("dev", dev), ("test", test)):
        split = {"seed": args.seed, "org": "original", "per_type": len(ids) // len(by_type),
                 "original": {"single_turn": sorted(ids, key=int), "multi_turn": []}}
        path = Path(args.out_dir) / f"original_{name}.json"
        path.write_text(json.dumps(split, indent=1), encoding="utf-8")
        print(f"{path}: {len(ids)} tasks over {len(by_type)} task types")


if __name__ == "__main__":
    main()
