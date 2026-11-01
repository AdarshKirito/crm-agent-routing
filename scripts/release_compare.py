"""Compare two systems' release decisions on the same tasks (scripts/release_eval.py --decisions-out).

Paired on task ids, 95% bootstrap intervals (5,000 resamples, seed 0, as in the other reports): coverage
(answers given / tasks), standard score (right answers given / tasks) and, for each system, risk (wrong
answers / answers given) with an exact 95% upper bound.

  python scripts/release_compare.py runs/x/crmroute_decisions.json runs/x/react_decisions.json --names crmroute react
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from release_eval import upper_bound  # noqa: E402


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {tuple(d["task"]): d for d in data["decisions"]}, data["rule"]


def paired(a: list[float], b: list[float], iters: int = 5000) -> str:
    n = len(a)
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(0)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    mean = 100 * sum(diffs) / n
    return f"{mean:+.1f} [{100 * boots[int(0.025 * iters)]:+.1f}, {100 * boots[int(0.975 * iters) - 1]:+.1f}]"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--names", nargs=2, default=["A", "B"])
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    (a, rule_a), (b, rule_b) = load(args.a), load(args.b)
    keys = sorted(a.keys() & b.keys())
    if len(keys) != len(a) or len(keys) != len(b):
        raise SystemExit(f"the two files cover different tasks ({len(a)} and {len(b)}, {len(keys)} shared)")
    lines = [f"Paired on {len(keys)} tasks. {args.names[0]}: {rule_a}. {args.names[1]}: {rule_b}.", "",
             "| system | answered (coverage) | wrong among answered (risk) | risk 95% upper bound | standard score |",
             "|---|---|---|---|---|"]
    for name, rows in zip(args.names, (a, b)):
        released = [rows[k] for k in keys if rows[k]["released"]]
        wrong = sum(1 - d["right"] for d in released)
        lines.append(f"| {name} | {len(released)} ({100 * len(released) / len(keys):.1f}%) | {int(wrong)} "
                     f"({100 * wrong / len(released) if released else 0:.1f}%) | {100 * upper_bound(int(wrong), len(released), 0.05):.1f}% | "
                     f"{100 * sum(d['right'] for d in released) / len(keys):.1f}% |")
    lines += ["", f"| difference ({args.names[0]} - {args.names[1]}) | points [95% CI] |", "|---|---|",
              f"| coverage | {paired([float(a[k]['released']) for k in keys], [float(b[k]['released']) for k in keys])} |",
              f"| standard score | {paired([a[k]['right'] for k in keys], [b[k]['right'] for k in keys])} |"]
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
