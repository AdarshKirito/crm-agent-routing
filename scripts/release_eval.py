"""Checkable answers: check every answer against its receipt, combine repeated runs, release or withhold.

Reads one or more runs of one system on the same task ids (run_tasks.py records). For crmroute the
receipt is in each record (agent_info.receipt); for the benchmark's ReAct agent it is rebuilt from the
trajectory (every <execute> query and the Salesforce output that followed it). Every answer goes through
agent/app/receipt_check.py, the code the agent itself uses. A release rule then decides per task, from
what a deployment would know (the receipts, the runs' agreement and the router's predicted task type,
never the true task type or the answer key), whether to give the answer or withhold it.

For each rule it reports coverage (tasks answered / all tasks), risk (wrong answers / answers given)
with an exact binomial upper bound, and the standard score (right answers / all tasks; a withheld
answer scores as a failure, as in the benchmark). --calibrate picks the most permissive rule whose
risk is certified below --alpha at confidence 1 - --delta (Learn-then-Test with fixed-sequence testing
over the rules in their pre-registered order); --rule applies a frozen rule to another split.

  python scripts/release_eval.py --runs runs/checkable_practice/r1/routed runs/checkable_practice/r2/routed \
      runs/checkable_practice/r3/routed --task-ids data/checkable_practice.json --out results/x.md
"""
import argparse
import ast
import importlib.util
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_results import CONFIDENTIALITY, expected_keys, final_reply, load_system, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rc = _load("receipt_check", ROOT / "agent" / "app" / "receipt_check.py")
specs = _load("task_specs", ROOT / "agent" / "app" / "task_specs.py")
SALESFORCE_OUTPUT = "Salesforce instance output: "
REACT_ERROR = re.compile(r"^[A-Z][A-Z_]+: ")


def react_receipt(row: dict) -> list[dict]:
    """Receipt of a ReAct trajectory: the first <execute> block of each message and the output that answered it."""
    receipt, pending = [], None
    for message in row.get("traj") or []:
        content = message.get("content") or ""
        if message.get("role") == "assistant":
            m = re.search(r"<execute>(.*?)</execute>", content, re.S)
            pending = m.group(1).strip() if m else None
        elif message.get("role") == "user" and pending is not None and content.startswith(SALESFORCE_OUTPUT):
            text = content[len(SALESFORCE_OUTPUT):]
            entry = {"n": len(receipt) + 1, "turn": 1, "tool": "sosl_search" if pending.startswith("FIND") else "soql_query",
                     "args": {"query": pending}, "status": "error" if REACT_ERROR.match(text) else "ok", "result": text,
                     "truncated": False}  # the benchmark's connector returns every row (query_all)
            if entry["status"] == "ok":
                try:
                    entry["totalSize"] = len(ast.literal_eval(text))
                except (ValueError, SyntaxError):
                    pass
            receipt.append(entry)
            pending = None
    return receipt


def is_remote(row: dict) -> bool:
    return "receipt" in (row.get("agent_info") or {})


def answer_of(row: dict) -> str:
    """The submitted answer; a task that ended any other way (turn limit, query error, request cap) has none."""
    end = (row.get("agent_info") or {}).get("end_reason") or {}
    if end.get("message") != "Submit action":
        return ""
    return end.get("content") if isinstance(end.get("content"), str) else final_reply(row)


def question_of(row: dict) -> str:
    """The request: the first user message (not the system prompt, not tool output)."""
    return next((m.get("content") or "" for m in row.get("traj") or [] if m.get("role") == "user"), "")


def context_of(row: dict) -> str:
    """What the asker supplied: their messages (and, for ReAct, the system prompt's task context)."""
    return "\n".join(m.get("content") or "" for m in row.get("traj") or [] if m.get("role") in ("user", "system")
                     and not (m.get("content") or "").startswith(SALESFORCE_OUTPUT))


@dataclass
class RunAnswer:
    verdict: object
    correct: float
    cost: float | None
    latency: float | None
    receipt: list = field(default_factory=list, repr=False)


@dataclass
class Task:
    key: tuple
    task_type: str  # true type: for reporting only, never used by a rule
    predicted: str | None  # the router's guess: what a rule may use
    runs: list[RunAnswer] = field(default_factory=list)

    def majority(self) -> list[RunAnswer]:
        clusters: list[list[RunAnswer]] = []
        for run in self.runs:
            for cluster in clusters:
                if rc.same_answer(cluster[0].verdict.claim, run.verdict.claim):
                    cluster.append(run)
                    break
            else:
                clusters.append([run])
        return max(clusters, key=len)  # ties keep the first run's answer


def load_tasks(run_dirs: list[Path], task_ids: Path, types_from: Path | None = None) -> list[Task]:
    wanted = {k for k in expected_keys(task_ids)}
    runs = [load_system(d) for d in run_dirs]
    for d, rows in zip(run_dirs, runs):
        missing = wanted - rows.keys()
        if missing:
            raise SystemExit(f"{d}: {len(missing)} tasks of the split are missing")
    router = load_system(types_from) if types_from else None
    if router is None and not any(is_remote(runs[0][k]) for k in wanted):
        raise SystemExit("ReAct records hold no router prediction: pass --types-from with a crmroute run of the same tasks")
    tasks = []
    for key in sorted(wanted):
        first = runs[0][key]
        if first["task_type"] in CONFIDENTIALITY:
            continue
        source = router[key] if router else first
        predicted = ((source.get("agent_info") or {}).get("route") or {}).get("task_type")
        task = Task(key, first["task_type"], predicted)
        form = specs.spec_for(predicted).answer
        for rows in runs:
            row = rows[key]
            receipt = (row["agent_info"].get("receipt") or []) if is_remote(row) else react_receipt(row)
            verdict = rc.check(answer_of(row) or "", form, receipt, context_of(row), question_of(row))
            info = row.get("agent_info") or {}
            latency = sum(t.get("latency_s") or 0 for t in info.get("turns") or []) if is_remote(row) else None
            task.runs.append(RunAnswer(verdict, score(row, 0.5)[1], info.get("total_cost"), latency, receipt))
        tasks.append(task)
    return tasks


# ---- release rules ------------------------------------------------------------------------------
# A rule sees only the runs' verdicts, their agreement and the predicted task type.

SOFT = ("budget", "none_without_empty", "truncated_support")


def clean(run: RunAnswer, soft: tuple[str, ...]) -> bool:
    return run.verdict.ok and not any(run.verdict.flags.get(f) for f in soft)


def make_rule(min_agree: int, soft: tuple[str, ...], withheld_types: frozenset = frozenset()):
    def rule(task: Task) -> bool:
        if task.predicted in withheld_types:
            return False
        group = task.majority()
        return sum(clean(r, soft) for r in group) >= min_agree
    rule.__name__ = (f"agree>={min_agree}" + (f", no {'/'.join(soft)}" if soft else "")
                     + (f", withhold {len(withheld_types)} types" if withheld_types else ""))
    return rule


def released_answer(task: Task) -> RunAnswer:
    return task.majority()[0]


# ---- statistics ---------------------------------------------------------------------------------

def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def upper_bound(errors: int, n: int, delta: float) -> float:
    """Exact (Clopper-Pearson) one-sided upper confidence bound on the error rate."""
    if n == 0:
        return 1.0
    if errors >= n:
        return 1.0
    lo, hi = errors / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_cdf(errors, n, mid) > delta:
            lo = mid
        else:
            hi = mid
    return hi


def evaluate(tasks: list[Task], rule, delta: float) -> dict:
    released = [t for t in tasks if rule(t)]
    wrong = sum(1 - released_answer(t).correct for t in released)
    right = len(released) - wrong
    return {"rule": rule.__name__, "tasks": len(tasks), "released": len(released), "wrong": int(wrong),
            "coverage": len(released) / len(tasks) if tasks else 0.0,
            "risk": wrong / len(released) if released else 0.0,
            "risk_ub": upper_bound(int(wrong), len(released), delta),
            "score": right / len(tasks) if tasks else 0.0}


def calibrate(tasks: list[Task], rules: list, alpha: float, delta: float) -> tuple[object | None, list[dict]]:
    """Fixed-sequence Learn-then-Test: rules run from the strictest; stop at the first that fails."""
    chosen, rows = None, []
    for rule in rules:
        row = evaluate(tasks, rule, delta)
        released, wrong = row["released"], row["wrong"]
        # p-value of H0 "risk > alpha": P(Binomial(released, alpha) <= wrong)
        row["p"] = binom_cdf(wrong, released, alpha) if released else 1.0
        row["certified"] = row["p"] <= delta
        rows.append(row)
        if not row["certified"]:
            break
        chosen = rule
    return chosen, rows


def fmt(row: dict) -> str:
    return (f"| {row['rule']} | {row['released']} of {row['tasks']} ({100 * row['coverage']:.1f}%) | "
            f"{row['wrong']} ({100 * row['risk']:.1f}%) | {100 * row['risk_ub']:.1f}% | {100 * row['score']:.1f}% |")


TABLE = ["| rule | answered (coverage) | wrong among answered (risk) | risk upper bound | standard score |",
         "|---|---|---|---|---|"]


def per_type(tasks: list[Task], rule) -> list[str]:
    by = defaultdict(list)
    for t in tasks:
        by[t.task_type].append(t)
    lines = ["| task type (true) | tasks | answered | wrong among answered | right without the rule |", "|---|---|---|---|---|"]
    for name, group in sorted(by.items()):
        released = [t for t in group if rule(t)]
        wrong = sum(1 - released_answer(t).correct for t in released)
        lines.append(f"| {name} | {len(group)} | {len(released)} | {int(wrong)} | "
                     f"{int(sum(t.runs[0].correct for t in group))} |")
    return lines


def flag_table(tasks: list[Task]) -> list[str]:
    """How often each flag fires on the first run, and how often answers with it are right."""
    counts, right = Counter(), Counter()
    for t in tasks:
        run = t.runs[0]
        names = [f for f, v in run.verdict.flags.items() if v] or ["(none)"]
        for f in names:
            counts[f] += 1
            right[f] += run.correct
    lines = ["| flag (first run) | answers | right |", "|---|---|---|"]
    for f, n in counts.most_common():
        lines.append(f"| {f} | {n} | {int(right[f])} ({100 * right[f] / n:.0f}%) |")
    return lines


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(math.ceil(q * len(ordered))) - 1)] if ordered else float("nan")


def repeat_table(tasks: list[Task]) -> list[str]:
    """Consistency over the k runs, and what answering costs in time and money."""
    k = len(tasks[0].runs) if tasks else 0
    agree = Counter(len(t.majority()) for t in tasks)
    pass_k = sum(all(r.correct for r in t.runs) for t in tasks)
    mean_right = sum(sum(r.correct for r in t.runs) / k for t in tasks)
    lines = ["| measure | value |", "|---|---|",
             f"| tasks | {len(tasks)} |",
             f"| mean success of one run | {100 * mean_right / len(tasks):.1f}% |",
             f"| pass^{k} (every run right) | {pass_k} ({100 * pass_k / len(tasks):.1f}%) |"]
    lines += [f"| runs giving the majority answer = {a} | {agree.get(a, 0)} tasks |" for a in range(k, 0, -1)]
    latencies = [r.latency for t in tasks for r in t.runs if r.latency is not None]
    if latencies:
        parallel = [max(r.latency or 0 for r in t.runs) for t in tasks]
        lines += [f"| latency of one run, p50 / p95 | {percentile(latencies, 0.5):.1f} s / {percentile(latencies, 0.95):.1f} s |",
                  f"| latency with the {k} runs in parallel (slowest run), p50 / p95 | "
                  f"{percentile(parallel, 0.5):.1f} s / {percentile(parallel, 0.95):.1f} s |"]
    costs = [sum(r.cost or 0 for r in t.runs) for t in tasks]
    lines.append(f"| list-price cost per task, all {k} runs | ${sum(costs) / len(costs):.4f} |")
    return lines


def default_rules(k: int) -> list:
    """The candidate family, strictest first."""
    rules = []
    for agree in range(k, 0, -1):
        rules.append(make_rule(agree, SOFT))
        rules.append(make_rule(agree, ("budget", "none_without_empty")))
        rules.append(make_rule(agree, ()))
    return rules


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", type=Path, required=True, help="run directories of one system, same tasks")
    ap.add_argument("--task-ids", type=Path, required=True)
    ap.add_argument("--types-from", type=Path, help="crmroute run whose router predictions a ReAct run uses")
    ap.add_argument("--alpha", type=float, default=0.10)
    ap.add_argument("--delta", type=float, default=0.10)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    tasks = load_tasks(args.runs, args.task_ids, args.types_from)
    k = len(args.runs)
    lines = [f"# Release evaluation: {', '.join(p.as_posix() for p in args.runs)}", "",
             f"{len(tasks)} business tasks, {k} run(s) each; alpha {args.alpha}, delta {args.delta}.", ""]
    lines += ["## Each run alone, every answer released", "", *TABLE]
    for i in range(k):
        single = [Task(t.key, t.task_type, t.predicted, [t.runs[i]]) for t in tasks]
        lines.append(fmt(evaluate(single, make_rule(0, ()), args.delta)).replace("agree>=0", f"run {i + 1}, no rule"))
    chosen, rows = calibrate(tasks, default_rules(k), args.alpha, args.delta)
    lines += ["", "## Candidate rules, strictest first (Learn-then-Test stops at the first uncertified rule)", "",
              TABLE[0] + " certified |", TABLE[1] + "---|"]
    lines += [fmt(r) + f" {'yes' if r['certified'] else 'no'} (p={r['p']:.3f}) |" for r in rows]
    lines += ["", f"Chosen: {chosen.__name__ if chosen else 'none (no rule certified)'}", ""]
    if chosen:
        lines += ["## Chosen rule by true task type", "", *per_type(tasks, chosen), ""]
    lines += ["## Repeats, latency and cost", "", *repeat_table(tasks), ""]
    lines += ["## Receipt flags", "", *flag_table(tasks), ""]
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
