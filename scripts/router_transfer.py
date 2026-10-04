"""How well the task-type router transfers to another org, and how many of its own examples it needs.

Offline, no LLM calls. Embeds every labelled example and test request once with the router's model
(passage vs query embedding, as TaskRouter does) and applies TaskRouter.predict's vote (similarity-
weighted, K nearest) to different example sets:

1. Between the two CRMArena-Pro orgs: examples from both, from the target org only, from the other
   org only, and the other org plus k target examples per type (data/router_eval_test.jsonl).
2. The original CRMArena org, which crmroute was not built on: Pro examples only, its own
   examples only, and Pro plus k of its own examples per type (data/router_eval_original_test.jsonl,
   examples from agent/app/data/router_examples_original.jsonl, written by scripts/add_org.py).

Usage (agent venv):  agent/.venv/Scripts/python scripts/router_transfer.py --out results/router_transfer.json
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
from app.router import EMBED_MODEL, K_NEIGHBOURS  # noqa: E402

PER_TYPE_STEPS = (1, 2, 5, 10, 20, 40)


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(c - h, 3), round(c + h, 3)]


def read(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/router_transfer.json")
    ap.add_argument("--seeds", type=int, default=10)
    args = ap.parse_args()
    from fastembed import TextEmbedding

    examples = read(ROOT / "agent/app/data/router_examples.jsonl") + read(ROOT / "agent/app/data/router_examples_original.jsonl")
    tests = read(ROOT / "data/router_eval_test.jsonl") + read(ROOT / "data/router_eval_original_test.jsonl")
    model = TextEmbedding(EMBED_MODEL)
    E = np.array(list(model.passage_embed([e["text"] for e in examples])), dtype=np.float32)
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    Q = np.array(list(model.query_embed([t["text"] for t in tests])), dtype=np.float32)
    Q /= np.linalg.norm(Q, axis=1, keepdims=True)
    labels = [e["task"] for e in examples]
    by_org = defaultdict(list)
    for i, e in enumerate(examples):
        by_org[e["org"]].append(i)

    def predict(qi: int, idx: np.ndarray) -> str:
        sims = E[idx] @ Q[qi]
        votes = defaultdict(float)
        for j in np.argsort(-sims)[:K_NEIGHBOURS]:
            votes[labels[idx[j]]] += float(max(sims[j], 0.0))
        return max(votes.items(), key=lambda kv: kv[1])[0]

    def score(idx: list[int], org: str) -> dict:
        qs = [i for i, t in enumerate(tests) if t["org"] == org]
        k = sum(predict(i, np.array(idx)) == tests[i]["task"] for i in qs)
        return {"correct": k, "n": len(qs), "accuracy": round(k / len(qs), 3), "ci95": wilson(k, len(qs))}

    def curve(base: list[int], target: str) -> dict:
        own = defaultdict(list)
        for i in by_org[target]:
            own[examples[i]["task"]].append(i)
        out = {}
        for per_type in PER_TYPE_STEPS:
            with_base, own_only = [], []
            for seed in range(args.seeds):
                rng = random.Random(seed)
                picked = [i for _, ids in sorted(own.items()) for i in rng.sample(ids, min(per_type, len(ids)))]
                with_base.append(score(base + picked, target)["accuracy"])
                own_only.append(score(picked, target)["accuracy"])
            out[per_type] = {"base_plus_own": [round(float(np.mean(with_base)), 3), round(float(np.std(with_base)), 3)],
                             "own_only": [round(float(np.mean(own_only)), 3), round(float(np.std(own_only)), 3)]}
        return out

    pro = by_org["b2b"] + by_org["b2c"]
    report = {"embed_model": EMBED_MODEL, "k_neighbours": K_NEIGHBOURS, "seeds": args.seeds,
              "examples": {o: len(v) for o, v in by_org.items()}, "pro_orgs": {}}
    both = sum(score(pro, o)["correct"] for o in ("b2b", "b2c"))
    report["pro_both_orgs_all_tests"] = {"correct": both, "n": 194, "accuracy": round(both / 194, 3)}
    print(f"Pro examples, all Pro test requests: {both}/194 (published 0.938)")
    for target, other in (("b2b", "b2c"), ("b2c", "b2b")):
        r = {"both_orgs": score(pro, target), "target_only": score(by_org[target], target),
             "other_org_only": score(by_org[other], target), "curve_other_plus_k": curve(by_org[other], target)}
        report["pro_orgs"][target] = r
        print(f"{target}: both {r['both_orgs']['accuracy']} | target only {r['target_only']['accuracy']} | "
              f"other org only {r['other_org_only']['accuracy']}")
    r = {"pro_only": score(pro, "original"), "own_only_all": score(by_org["original"], "original"),
         "curve_pro_plus_k": curve(pro, "original")}
    report["original_org"] = r
    print(f"original: Pro examples only {r['pro_only']['accuracy']} {r['pro_only']['ci95']} | "
          f"own 40/type only {r['own_only_all']['accuracy']}")
    for k, c in r["curve_pro_plus_k"].items():
        print(f"  Pro + {k:>2} own per type -> {c['base_plus_own'][0]:.3f} (sd {c['base_plus_own'][1]:.3f}) | "
              f"own {k} only -> {c['own_only'][0]:.3f}")
    Path(args.out).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
