"""Split a task-id file into two halves per org and mode, so one system's run can go as two parallel streams.

Each half keeps every org and mode with the first or second half of its sorted ids. The halves write to
separate run directories (one results file per org and mode); scripts/release_eval.py and recheck_receipts.py
read such a run as "dir_a,dir_b".

  python scripts/split_halves.py data/checkable_test.json runs/checkable_splits/test
  -> runs/checkable_splits/test_h1.json, runs/checkable_splits/test_h2.json
"""
import json
import sys
from pathlib import Path


def main() -> None:
    source, prefix = Path(sys.argv[1]), Path(sys.argv[2])
    split = json.loads(source.read_text(encoding="utf-8"))
    halves = [{"source": source.as_posix(), "half": h + 1} for h in range(2)]
    for org in ("b2b", "b2c"):
        for half in halves:
            half[org] = {}
        for mode, ids in split[org].items():
            ordered = sorted(ids, key=int)
            cut = (len(ordered) + 1) // 2
            halves[0][org][mode], halves[1][org][mode] = ordered[:cut], ordered[cut:]
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for half in halves:
        half["counts"] = {org: {mode: len(v) for mode, v in half[org].items()} for org in ("b2b", "b2c")}
        path = prefix.parent / f"{prefix.name}_h{half['half']}.json"
        path.write_text(json.dumps(half, indent=1), encoding="utf-8")
        print(path, half["counts"])


if __name__ == "__main__":
    main()
