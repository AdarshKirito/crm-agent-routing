"""Round 3's blinded audit (docs/checkable3_plan.md): build the items, seal which candidate is the key, unblind labels.

Items, fixed by the plan: every wrong released test answer, a seeded random sample of right released answers of the
same size (seed 20261103, round 3's split seed), and every key-reproduction flag (results/checkable3_key_flags.json).
The reader sees each item's question, its task context, the evidence behind crmroute's first run (the queries and
their recorded rows, which can be re-run read-only on the org) and two candidate answers in random order. One is the
benchmark's key. The other is the first answer that differs from it among crmroute's three runs, ReAct's run and the
readings' answers, else "None". The reader labels each item: A is right, B is right, both defensible, neither, or
unsure.

  vendor/CRMArena/.venv/Scripts/python scripts/checkable3_audit.py prepare   # items + sealed key; commit the hashes
  vendor/CRMArena/.venv/Scripts/python scripts/checkable3_audit.py unblind --labels <labels.json>

`prepare` writes runs/checkable3_audit/items.json (what the reader sees), runs/checkable3_audit/sealed.json (which
candidate is the key, kept unread until the labels are in) and results/checkable3_audit_seal.md (both files' sha256).
`unblind` maps the labels to the plan's four (key wrong; ambiguous; crmroute wrong; unsure) and writes
results/checkable3_audit.md, with the certificate against the audit beside the one against the shipped key.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "dev"))
import checkable3_report as K3  # noqa: E402
import convention_gate as CG  # noqa: E402
import pro_records as P  # noqa: E402

R3, RE, ROOT = K3.R3, K3.RE, K3.ROOT
SEED = 20261103
AUDIT = ROOT / "runs" / "checkable3_audit"
RESULT_CHARS = 4000
LABELS = ("A", "B", "both", "neither", "unsure")


def norm(text: str) -> str:
    return " ".join(str(text).split()).strip().lower()


def shown(claim) -> str:
    """A run's answer as the reader sees it."""
    if claim.kind == "none":
        return "None"
    return ", ".join(str(v) for v in claim.values)


def key_of(row: dict) -> str:
    return "None" if row["gt_answer"] is None else str(row["gt_answer"])


def evidence(row: dict) -> list[dict]:
    """crmroute's first run: each successful tool call with its arguments and recorded result (cut to fit)."""
    out = []
    for e in (row.get("agent_info") or {}).get("receipt") or []:
        if e.get("status") != "ok":
            continue
        result = e.get("result") or ""
        out.append({"tool": e["tool"], "args": e.get("args"), "rows": e.get("totalSize"),
                    "result": result[:RESULT_CHARS] + (" ... (cut)" if len(result) > RESULT_CHARS else "")})
    return out


def prepare() -> None:
    specs = json.loads(K3.RULES.read_text(encoding="utf-8"))
    tasks = {t.key: t for t in K3.tasks_of("crmroute", "test")}
    react = {t.key: t for t in K3.tasks_of("react", "test")}
    rule = K3.rule_from(specs["crmroute"], K3.gate_of("crmroute", "test"))
    first = RE.load_run(K3.SPLITS["test"][0] / "r1" / "routed")
    rewrites = {}
    for r in CG.load(K3.SPLITS["test"][0] / "rewrites.jsonl"):
        rewrites.setdefault(str(r["task"]), []).append(r)
    flags = {f["task"]: f for f in json.loads((ROOT / "results" / "checkable3_key_flags.json").read_text(encoding="utf-8"))}

    released = sorted((k for k, t in tasks.items() if rule(t)), key=lambda k: int(k[2]))
    wrong = [k for k in released if R3.released_run(tasks[k], rule).correct < 1]
    right = [k for k in released if R3.released_run(tasks[k], rule).correct >= 1]
    sample = sorted(random.Random(SEED).sample(right, len(wrong)), key=lambda k: int(k[2]))
    chosen = {k: "released, wrong by the key" for k in wrong}
    chosen.update({k: "released, right by the key" for k in sample})
    for k in sorted(tasks, key=lambda k: int(k[2])):
        if k[2] in flags:
            chosen[k] = chosen.get(k, "") + ("; " if k in chosen else "") + "key-reproduction flag"

    rng = random.Random(SEED + 1)
    items, sealed = [], []
    for n, (k, group) in enumerate(sorted(chosen.items(), key=lambda kv: int(kv[0][2])), 1):
        row, task = first[k], tasks[k]
        key = key_of(row)
        pool = [("crmroute run %d" % (i + 1), shown(r.verdict.claim)) for i, r in enumerate(task.runs)]
        if k in react:
            pool.append(("ReAct", shown(react[k].runs[0].verdict.claim)))
        for r in sorted(rewrites.get(k[2], []), key=lambda r: r["run"]):
            for reading in r.get("readings", []):
                for _, a in CG.combos(reading):
                    pool.append((f"a reading of run {r['run']}", "None" if a[0] == "none" else ", ".join(a[1])))
        other = next(((src, a) for src, a in pool if a and norm(a) != norm(key)), ("fallback", "None"))
        if norm(other[1]) == norm(key):
            other = ("fallback", "(no other answer was produced)")
        order = [("key", key), (other[0], other[1])]
        rng.shuffle(order)
        items.append({"item": n, "task": f"original/{k[2]}", "question": RE.question_of(row),
                      "context": P.contexts()["original"].get(k[2], ""), "evidence": evidence(row),
                      "A": order[0][1], "B": order[1][1]})
        sealed.append({"item": n, "task": f"original/{k[2]}", "type": task.task_type, "group": group,
                       "key_is": "A" if order[0][0] == "key" else "B", "other_source": other[0],
                       "crmroute_answer": shown(task.runs[0].verdict.claim), "released": k in released,
                       "right_by_key": task.runs[0].correct >= 1})
    AUDIT.mkdir(parents=True, exist_ok=True)
    files = {"items.json": items, "sealed.json": sealed}
    digests = {}
    for name, data in files.items():
        text = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
        (AUDIT / name).write_text(text, encoding="utf-8", newline="\n")
        digests[name] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    groups = {}
    for s in sealed:
        groups[s["group"]] = groups.get(s["group"], 0) + 1
    lines = ["# Round 3's blinded audit: the seal", "",
             "Written by `scripts/checkable3_audit.py prepare` before any item was labelled. The reader sees "
             "`runs/checkable3_audit/items.json`; `runs/checkable3_audit/sealed.json` says which candidate is the key and "
             "stays unread until the labels are in. Their sha256:", "",
             *[f"- `{name}`: `{digest}`" for name, digest in digests.items()], "",
             f"{len(items)} items (seed {SEED}):", "", *[f"- {g}: {n}" for g, n in sorted(groups.items())], ""]
    (ROOT / "results" / "checkable3_audit_seal.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


def unblind(labels_path: Path) -> None:
    sealed = json.loads((AUDIT / "sealed.json").read_text(encoding="utf-8"))
    labels = {int(k): v for k, v in json.loads(labels_path.read_text(encoding="utf-8")).items()}
    missing = [s["item"] for s in sealed if labels.get(s["item"]) not in LABELS]
    if missing:
        raise SystemExit(f"items without a valid label ({'/'.join(LABELS)}): {missing}")
    verdicts = []
    for s in sealed:
        label, key = labels[s["item"]], s["key_is"]
        picked = "key" if label == key else "other" if label in ("A", "B") else label
        crm_is_key = s["right_by_key"]
        # crmroute's released answer is the key or, where it differs, the other candidate (run 1 comes first)
        crm_right = {"key": crm_is_key, "other": not crm_is_key, "both": True, "neither": False,
                     "unsure": crm_is_key}[picked]
        audit = {"key": "key right" if crm_is_key else "crmroute wrong", "other": "key wrong", "both": "ambiguous",
                 "neither": "key wrong, crmroute wrong", "unsure": "unsure"}[picked]
        verdicts.append({**s, "label": label, "audit": audit, "crmroute_right_by_audit": crm_right})
    lines = ["# Round 3's blinded audit", "", "```",
             f"vendor/CRMArena/.venv/Scripts/python scripts/checkable3_audit.py unblind --labels {labels_path.as_posix()}",
             "```", "", "The owner read every item blind (`results/checkable3_audit_seal.md`); no second reader was found, so "
             "there is no kappa.", "",
             "| item | task | type | group | crmroute's answer right by the key | audit |", "|---|---|---|---|---|---|"]
    lines += [f"| {v['item']} | {v['task']} | {v['type']} | {v['group']} | {'yes' if v['right_by_key'] else 'no'} | "
              f"{v['audit']} |" for v in verdicts]
    # the certificate against the audit: an audited released answer takes the audit's verdict (ambiguous counts as
    # right, unsure keeps the key's); every other released answer keeps the key's
    specs = json.loads(K3.RULES.read_text(encoding="utf-8"))
    tasks = K3.tasks_of("crmroute", "test")
    rule = K3.rule_from(specs["crmroute"], K3.gate_of("crmroute", "test"))
    released = [t for t in tasks if rule(t)]
    by_task = {v["task"]: v for v in verdicts}
    wrong_key = sum(R3.released_run(t, rule).correct < 1 for t in released)
    wrong_audit = 0
    for t in released:
        v = by_task.get(f"original/{t.key[2]}")
        wrong_audit += not (v["crmroute_right_by_audit"] if v else R3.released_run(t, rule).correct >= 1)
    n = len(released)
    lines += ["", "| measured against | released | wrong | risk | risk 95% upper bound |", "|---|---|---|---|---|",
              f"| the shipped key (primary) | {n} | {wrong_key} | {100 * wrong_key / n:.1f}% | "
              f"{100 * RE.upper_bound(wrong_key, n, 0.05):.1f}% |",
              f"| the audit (secondary) | {n} | {wrong_audit} | {100 * wrong_audit / n:.1f}% | "
              f"{100 * RE.upper_bound(wrong_audit, n, 0.05):.1f}% |"]
    (ROOT / "results" / "checkable3_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (AUDIT / "verdicts.json").write_text(json.dumps(verdicts, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["prepare", "unblind"])
    ap.add_argument("--labels", type=Path)
    args = ap.parse_args()
    if args.stage == "prepare":
        prepare()
    else:
        if not args.labels:
            raise SystemExit("unblind needs --labels")
        unblind(args.labels)


if __name__ == "__main__":
    main()
