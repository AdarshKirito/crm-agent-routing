"""Write the task lists for the checkable-answers evaluation (CRMArena-Pro business tasks).

Every id is new: none is in data/dev.json, data/test.json or data/fresh.json, and none is a labelled
router example (the router's nearest-type prediction would otherwise have seen the task). Per org and
business task type (19):
  practice     4 single-turn tasks: building and trying the release rule
  calibration  8 single-turn tasks: fitting the release threshold, once the method is frozen
  test         8 single-turn and 2 multi-turn tasks: run once, after calibration
Single-turn and interactive tasks share ids, so ids are disjoint across modes as in make_splits.py.
No confidentiality task is left unused, so refusals are only re-checked on earlier splits.

Usage:  vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --out-dir data --seed 20261031
        vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --extend-calibration 4 --seed 20261101

--extend-calibration K adds K more single-turn tasks per org and type to data/checkable_calibration.json,
drawn the same way and disjoint from every split above; the existing ids stay. It was used once, before
any calibration run, to raise the calibration split from 8 to 12 tasks per org and type.

Round 2 (docs/checkable_answers.md) uses every business single-turn task still unused, halved per org and type:
        vendor/CRMArena/.venv/Scripts/python scripts/make_checkable_splits.py --round2 --seed 20261102
"""
import argparse
import json
import random
from pathlib import Path

from datasets import load_dataset

from make_splits import CONFIDENTIALITY, by_type, take

SPLITS = {"practice": (4, 0), "calibration": (8, 0), "test": (8, 2)}  # (single-turn, multi-turn) per type


def used_ids(paths: list[Path], examples: list[Path]) -> dict[str, set[str]]:
    used = {"b2b": set(), "b2c": set()}
    for path in paths:
        split = json.loads(path.read_text(encoding="utf-8"))
        for org in used:
            for ids in split[org].values():
                used[org].update(str(i) for i in ids)
    for path in examples:
        for line in path.read_text(encoding="utf-8").splitlines():
            example = json.loads(line)
            if example["org"] in used:
                used[example["org"]].add(str(example["idx"]))
    return used


def extend_calibration(args) -> None:
    out_dir = Path(args.out_dir)
    paths = {name: out_dir / f"checkable_{name}.json" for name in SPLITS}
    splits = {name: json.loads(p.read_text(encoding="utf-8")) for name, p in paths.items()}
    excluded = used_ids([Path(p) for p in args.exclude] + list(paths.values()), [Path(p) for p in args.router_examples])
    ds = load_dataset("Salesforce/CRMArenaPro", "CRMArenaPro")
    rng = random.Random(args.seed)
    cal = splits["calibration"]
    for org in ["b2b", "b2c"]:
        single = by_type(ds[org])
        business = [t for t in single if t not in CONFIDENTIALITY]
        sample_id = next(iter(single[business[0]]))
        used = {type(sample_id)(i) for i in excluded[org]}
        before = set(map(str, cal[org]["single_turn"]))
        extra = take(rng, single, args.extend_calibration, business, used)
        assert not before & set(map(str, extra))
        cal[org]["single_turn"] = sorted(cal[org]["single_turn"] + extra, key=int)
    cal["extended"] = {"seed": args.seed, "per_type": args.extend_calibration}
    cal["counts"] = {org: {mode: len(ids) for mode, ids in cal[org].items()} for org in ["b2b", "b2c"]}
    paths["calibration"].write_text(json.dumps(cal, indent=1))
    print("calibration", cal["counts"], "->", paths["calibration"])


def round2(args) -> None:
    """Every business single-turn task no split above has used, halved at random per org and type into
    data/checkable2_calibration.json and data/checkable2_test.json (an odd task goes to test)."""
    out_dir = Path(args.out_dir)
    earlier = [Path(p) for p in args.exclude] + [out_dir / f"checkable_{name}.json" for name in SPLITS]
    excluded = used_ids(earlier, [Path(p) for p in args.router_examples])
    ds = load_dataset("Salesforce/CRMArenaPro", "CRMArenaPro")
    rng = random.Random(args.seed)
    halves = {name: {"seed": args.seed, "excludes": [p.as_posix() for p in earlier] + args.router_examples}
              for name in ("calibration", "test")}
    for org in ["b2b", "b2c"]:
        single = by_type(ds[org])
        business = [t for t in single if t not in CONFIDENTIALITY]
        sample_id = next(iter(single[business[0]]))
        used = {type(sample_id)(i) for i in excluded[org]}
        picked = {"calibration": [], "test": []}
        for task_type in sorted(business):
            pool = [i for i in single[task_type] if i not in used]
            rng.shuffle(pool)
            picked["calibration"] += pool[:len(pool) // 2]
            picked["test"] += pool[len(pool) // 2:]
        for name, ids in picked.items():
            halves[name][org] = {"single_turn": sorted(ids, key=int), "multi_turn": []}
    for name, split in halves.items():
        split["counts"] = {org: {mode: len(ids) for mode, ids in split[org].items()} for org in ["b2b", "b2c"]}
        path = out_dir / f"checkable2_{name}.json"
        path.write_text(json.dumps(split, indent=1))
        print(name, split["counts"], "->", path)
    for org in ["b2b", "b2c"]:
        cal, test = ({str(i) for i in halves[n][org]["single_turn"]} for n in ("calibration", "test"))
        assert not cal & test, f"round-2 halves overlap in {org}"
        assert not (cal | test) & excluded[org], f"a used task or router example was drawn in {org}"
    print("round-2 splits are disjoint from each other, from every earlier split and from the router examples")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--exclude", nargs="+", default=["data/dev.json", "data/test.json", "data/fresh.json"])
    ap.add_argument("--router-examples", nargs="+", default=["agent/app/data/router_examples.jsonl"])
    ap.add_argument("--extend-calibration", type=int, default=0)
    ap.add_argument("--round2", action="store_true", help="split every remaining task (data/checkable2_*.json)")
    args = ap.parse_args()
    if args.round2:
        round2(args)
        return
    if args.extend_calibration:
        extend_calibration(args)
        return

    ds = load_dataset("Salesforce/CRMArenaPro", "CRMArenaPro")
    rng = random.Random(args.seed)
    excluded = used_ids([Path(p) for p in args.exclude], [Path(p) for p in args.router_examples])
    splits = {name: {"seed": args.seed, "excludes": args.exclude + args.router_examples} for name in SPLITS}
    for org in ["b2b", "b2c"]:
        single = by_type(ds[org])
        multi = by_type(ds[f"{org}_interactive"])
        business = [t for t in single if t not in CONFIDENTIALITY]
        assert len(business) == 19, business
        sample_id = next(iter(single[business[0]]))
        used = {type(sample_id)(i) for i in excluded[org]}  # take() compares ids as the dataset stores them
        for name, (per_single, per_multi) in SPLITS.items():
            splits[name][org] = {
                "single_turn": take(rng, single, per_single, business, used),
                "multi_turn": take(rng, multi, per_multi, business, used) if per_multi else [],
            }
    for name, split in splits.items():
        split["counts"] = {org: {mode: len(ids) for mode, ids in split[org].items()} for org in ["b2b", "b2c"]}
        path = Path(args.out_dir) / f"checkable_{name}.json"
        path.write_text(json.dumps(split, indent=1))
        print(name, split["counts"], "->", path)
    for org in ["b2b", "b2c"]:
        ids = [{str(i) for mode_ids in s[org].values() for i in mode_ids} for s in splits.values()]
        assert not (ids[0] & ids[1] or ids[0] & ids[2] or ids[1] & ids[2]), f"splits overlap in {org}"
        assert not (set().union(*ids) & excluded[org]), f"a used task or router example was drawn in {org}"
    print("splits are disjoint from each other, from earlier splits and from the router examples")


if __name__ == "__main__":
    main()
