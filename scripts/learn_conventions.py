"""Learn an org's conventions from the keys of tasks that are already used (round 3, docs/checkable3_devlog.md).

Reads scripts/rewrite_recheck.py output for runs on used tasks. For every declared reading the runs asked
(data/conventions_catalog.yaml), it writes how many runs support it (some combination with it reproduces
the key), how many contradict it (none does, but another reading of the same slot does), the tasks that
support it, and its status: pinned (runs of three or more tasks support it, none contradicts it), excluded
(no run supports it, at least one contradicts it) or allowed. The file is frozen before any fresh task
runs; the release layer asks a slot only its pinned readings when it has any. No fresh task's key is read.

  vendor/CRMArena/.venv/Scripts/python scripts/learn_conventions.py --records runs/checkable3_dev/d1.jsonl \
      --org original --out data/conventions_original.yaml
"""
import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import convention_gate as CG  # noqa: E402
import conventions as CV  # noqa: E402


def learned_conventions(runs: list[dict]) -> dict:
    info = CG.learn(runs)
    slots = {}
    for slot, values in CV.IMPLEMENTED.items():
        readings = {}
        for value in values:
            c = (slot, value)
            if not (info["support"][c] or info["contra"][c]):
                continue
            readings[value] = {"status": "pinned" if c in info["pinned"] else "excluded" if c in info["excluded"] else "allowed",
                               "supporting_runs": info["support"][c], "contradicting_runs": info["contra"][c],
                               "supporting_tasks": sorted(int(t) for _, t in info["support_tasks"][c])}
        if readings:
            slots[slot] = readings
    return slots


def pins_of(path: Path) -> dict:
    """slot -> pinned readings, from a frozen conventions file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {slot: {v for v, r in readings.items() if r["status"] == "pinned"}
            for slot, readings in data["slots"].items() if any(r["status"] == "pinned" for r in readings.values())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", type=Path, required=True, help="rewrite_recheck.py output for runs on used tasks")
    ap.add_argument("--org", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    runs = [r for r in CG.load(args.records) if r["kind"] in CG.CHECKABLE and r["org"] == args.org]
    out = {"org": args.org, "catalog_version": CV.catalog()["version"], "learned_from": args.records.as_posix(),
           "runs": len(runs), "tasks": len({r["task"] for r in runs}), "slots": learned_conventions(runs)}
    header = ("# Conventions learned from used tasks' keys by scripts/learn_conventions.py (round 3,\n"
              "# docs/checkable3_devlog.md). Frozen before any fresh task runs; no fresh task's key was read.\n")
    args.out.write_text(header + yaml.safe_dump(out, sort_keys=False, width=110, default_flow_style=None), encoding="utf-8")
    for slot, readings in out["slots"].items():
        print(slot, {v: (r["status"], r["supporting_runs"], r["contradicting_runs"]) for v, r in readings.items()})


if __name__ == "__main__":
    main()
