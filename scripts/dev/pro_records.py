"""Development records for round 3 (docs/checkable3_devlog.md): crmroute's three-run CRMArena-Pro records
from rounds 1 and 2, each task with its question, task context and key. Every one of these tasks is used.
Round 3's tasks (the original org's never-used ones) are not read here.

The task context is the benchmark's metadata "required" (today's date, the type's policy), the text the
harness passes the agent as crm_task_context. Records do not keep it, so it is read from the benchmark's
dataset (the local Hugging Face cache). Run with the benchmark environment:

  vendor/CRMArena/.venv/Scripts/python scripts/dev/pro_records.py

which rebuilds the per-type tables that rounds 1 and 2 published, and prints the go/no-go populations.
"""
import json
import sys
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import checkable2_report as C2  # noqa: E402
import checkable_report as C1  # noqa: E402
import release_eval as RE  # noqa: E402

# split -> (round, run directory, task ids)
SPLITS = {f"r{n}_{name}": (n, ROOT / "runs" / f"checkable{'' if n == 1 else n}_{name}",
                           ROOT / "data" / f"checkable{'' if n == 1 else n}_{name}.json")
          for n, names in ((1, ("practice", "calibration", "test")), (2, ("calibration", "test"))) for name in names}
# The types the original CRMArena org shares with CRMArena-Pro whose answer is computed from query rows.
SIX = ("best_region_identification", "handle_time", "transfer_count", "monthly_trend_analysis",
       "top_issue_identification", "case_routing")
CHECKABLE = ("ids", "none", "value")


@dataclass
class DevTask:
    split: str
    round: int
    task: RE.Task  # the runs' verdicts and receipts, as release_eval reads them
    question: str
    context: str
    key: object  # the benchmark's answer (gt_answer)

    @property
    def unanimous(self) -> bool:
        claims = [r.verdict.claim for r in self.task.runs]
        return all(c.kind in CHECKABLE for c in claims) and all(RE.rc.same_answer(claims[0], c) for c in claims[1:])


@cache
def contexts() -> dict:
    """org -> task id -> the task's "required" metadata, from the benchmark's dataset."""
    sys.path.insert(0, str(ROOT / "vendor" / "CRMArena"))
    from crm_sandbox.data import assets

    out = {}
    for org, tasks in (("b2b", assets.TASKS_B2B), ("b2c", assets.TASKS_B2C), ("original", assets.TASKS_ORIGINAL)):
        out[org] = {str(t["idx"]): ((t.get("metadata") or {}).get("required") or "") for t in tasks}
    return out


def load(splits=tuple(SPLITS)) -> list[DevTask]:
    out = []
    for split in splits:
        n, base, ids = SPLITS[split]
        runs = C2.crm_runs(base)
        first = RE.load_run(runs[0])
        for task in RE.load_tasks(runs, ids):
            row = first[task.key]
            out.append(DevTask(split, n, task, RE.question_of(row), contexts()[task.key[0]][task.key[2]],
                               row.get("gt_answer")))
    return out


def table_after(path: Path, heading: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(heading) + 2
    end = next((i for i in range(start, len(lines)) if not lines[i].startswith("|")), len(lines))
    return lines[start:end]


def self_check(tasks: list[DevTask]) -> bool:
    """Rebuild the per-type tables of rounds 1 and 2 from these records with their certified rules."""
    r1_rule = C1.rule_named(json.loads(C1.RULES.read_text(encoding="utf-8"))["crmroute"]["rule"], 3)
    r2_rule = C2.rule_from(json.loads(C2.RULES.read_text(encoding="utf-8"))["crmroute"])
    ok = True
    for split, rule, path, heading in (
            ("r1_test", r1_rule, ROOT / "results" / "checkable_answers.md", "## crmroute's certified rule by true task type (test)"),
            ("r2_test", r2_rule, ROOT / "results" / "checkable2_answers.md", "## crmroute's chosen rule by true task type (test)")):
        rebuilt = RE.per_type([t.task for t in tasks if t.split == split], rule)
        published = table_after(path, heading)
        same = rebuilt == published
        ok &= same
        print(f"{split}: per-type table {'matches' if same else 'DIFFERS FROM'} {path.relative_to(ROOT).as_posix()}")
        if not same:
            for a, b in zip(rebuilt, published):
                if a != b:
                    print(f"  rebuilt   {a}\n  published {b}")
    return ok


def populations(tasks: list[DevTask]) -> None:
    """The go/no-go populations (docs/checkable3_devlog.md), by predicted and by true type."""
    for label, of in (("predicted", lambda t: t.task.predicted), ("true", lambda t: t.task.task_type)):
        six = [t for t in tasks if of(t) in SIX]
        answers = sum(r.verdict.claim.kind in CHECKABLE for t in six for r in t.task.runs)
        unanimous = [t for t in six if t.unanimous]
        wrong = sum(not RE.released_answer(t.task).correct for t in unanimous)
        disagree = sum(1 for t in six if len(t.task.majority()) < len(t.task.runs))
        print(f"six types by {label} type: {len(six)} tasks, {answers} checkable run answers; unanimous {len(unanimous)} "
              f"({wrong} wrong, {len(unanimous) - wrong} right); runs disagree on {disagree}")


def main() -> None:
    tasks = load()
    counts = Counter(t.split for t in tasks)
    print(f"{len(tasks)} tasks: " + ", ".join(f"{s} {counts[s]}" for s in SPLITS))
    missing = sum(not t.context for t in tasks)
    print(f"tasks without a task context in the dataset: {missing}")
    ok = self_check(tasks)
    populations(tasks)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
