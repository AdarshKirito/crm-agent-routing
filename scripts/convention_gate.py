"""The convention gate over scripts/rewrite_recheck.py output (round 3, docs/checkable3_devlog.md).

A run's check holds its own level (does its deciding query, re-run live, reproduce its answer?) and its
rewritten readings, each with the answer its derivation gives under each tie reading. A run passes a level
when the own level passes, where required, and every reading asked gives the run's answer. `learn` finds the
readings that used tasks' keys pin (runs of three or more tasks support it, none contradicts it) or exclude
(no run supports it, at least one contradicts it). Used by the go/no-go checks (scripts/dev/), by
scripts/learn_conventions.py and by the round-3 release layer.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

CHECKABLE = ("ids", "none", "value")
TIES = ("none", "first")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def akey(answer) -> tuple:
    return (answer[0], tuple(answer[1]))


def combos(reading: dict) -> list[tuple[tuple, tuple]]:
    """(choices including the tie slot, answer) of one rewritten reading that ran and derived an answer."""
    if reading.get("status") != "ok":
        return []
    base = tuple(tuple(c) for c in reading["choices"])
    answers = reading["answers"]
    return [(base + (("ties", t),), akey(answers.get(t) or answers["*"])) for t in TIES]


def complete(run: dict) -> bool:
    """C1: the check of this run completes at the declared level."""
    return run.get("own") in ("pass", "fail") and not run.get("why") and all(r["status"] == "ok" for r in run["readings"])


def level(run: dict, excluded: set | None = None) -> str:
    """pass | fail | unchecked of one run: the own level must pass and every reading (every one the other
    round's keys do not exclude, if `excluded` is given) must give the run's answer under each tie reading."""
    if run.get("own") == "fail":
        return "fail"
    answer = akey(run["answer"])
    unknown = run.get("own") != "pass" or bool(run.get("why"))
    for reading in run.get("readings", []):
        if excluded and any(tuple(c) in excluded for c in reading["choices"]):
            continue
        if reading.get("status") != "ok":
            unknown = True
            continue
        if any(a != answer for c, a in combos(reading) if not (excluded and c[-1] in excluded)):
            return "fail"
    return "unchecked" if unknown else "pass"


def pinned_level(run: dict, pins: dict, own_required: bool) -> str:
    """pass | fail | unchecked of one run over the pinned readings (`pins`: slot -> pinned readings; a slot
    without pins keeps all its readings). Without `own_required`, the own level decides only questions that
    have no readings; elsewhere the executed readings decide."""
    readings = run.get("readings", [])
    if run.get("own") == "fail" and (own_required or not readings):
        return "fail"
    answer = akey(run["answer"])
    unknown = bool(run.get("why")) or ((own_required or not readings) and run.get("own") != "pass")
    asked = 0
    for reading in readings:
        if any(slot in pins and value not in pins[slot] for slot, value in reading["choices"]):
            continue
        if reading.get("status") != "ok":
            unknown = True
            continue
        for choices, a in combos(reading):
            slot, value = choices[-1]
            if slot in pins and value not in pins[slot]:
                continue
            asked += 1
            if a != answer:
                return "fail"
    return "unchecked" if unknown or (readings and not asked) else "pass"


def learn(runs: list[dict]) -> dict:
    """Readings the keys of `runs` exclude (no run supports it, at least one contradicts it), and pinned ones
    (runs of three or more tasks support it, none contradicts it)."""
    support, contra, support_tasks = Counter(), Counter(), defaultdict(set)
    for run in runs:
        key = akey(run["key"])
        made = [m for r in run.get("readings", []) for m in combos(r)]
        slots = defaultdict(set)
        for choices, _ in made:
            for slot, value in choices:
                slots[slot].add(value)
        for slot, values in slots.items():
            hit = {v for v in values if any(a == key and (slot, v) in c for c, a in made)}
            for v in values:
                if v in hit:
                    support[(slot, v)] += 1
                    support_tasks[(slot, v)].add((run["org"], run["task"]))
                elif hit:
                    contra[(slot, v)] += 1
    excluded = {c for c in contra if support[c] == 0}
    by_slot = defaultdict(set)
    for slot, value in set(support) | set(contra):
        by_slot[slot].add(value)
    for slot, values in by_slot.items():  # if every reading of a slot would be excluded, none is
        if all((slot, v) in excluded for v in values):
            excluded -= {(slot, v) for v in values}
    pinned = {c for c in support if len(support_tasks[c]) >= 3 and contra[c] == 0}
    return {"excluded": excluded, "pinned": pinned, "support": support, "contra": contra,
            "support_tasks": support_tasks}


def pins_by_slot(pinned: set) -> dict:
    by_slot = defaultdict(set)
    for slot, value in pinned:
        by_slot[slot].add(value)
    return dict(by_slot)


def task_gate(levels: list[str]) -> str:
    """A task passes when no run of its majority group fails and at least one passes."""
    return "fail" if "fail" in levels else "pass" if "pass" in levels else "unchecked"
