"""Does an answer survive every reasonable reading of its question?

`check` re-runs the agent's deciding query once per reading of the question's period (`periods.readings`), each
time rewritten by the caller's `query_for(reading)`, derives an answer from the rows with the caller's
`derive(rows)`, and compares it with the agent's answer. An answer that changes with the reading depends on a
convention the question leaves open.

`learn` finds an organisation's conventions from questions whose right answer is known: a reading is pinned when
it reproduces the known answer on at least `min_tasks` questions and never contradicts one, and excluded when it
never reproduces one but another reading of its slot does. `check(..., conventions=...)` then asks only the
readings the conventions allow, so an answer is held back only when it disagrees with how this organisation reads
its own questions. Ported from crmroute's round-3 convention gate (scripts/convention_gate.py).
"""
from collections import Counter, defaultdict
from collections.abc import Callable, Hashable, Iterable
from dataclasses import dataclass, field
from datetime import date

from . import periods
from .receipts import QueryFn, Rows


@dataclass(frozen=True)
class ReadingResult:
    reading: periods.Reading
    query: str
    answer: Hashable | None
    error: str | None = None


@dataclass
class Conventions:
    pinned: set = field(default_factory=set)  # {(slot, reading)}
    excluded: set = field(default_factory=set)
    support: Counter = field(default_factory=Counter)
    contra: Counter = field(default_factory=Counter)

    def asks(self, reading: periods.Reading) -> bool:
        """Whether a check under these conventions asks this reading: every slot with a pin is read as pinned, a
        slot without one keeps its readings, and excluded readings are never asked."""
        by_slot = defaultdict(set)
        for slot, value in self.pinned:
            by_slot[slot].add(value)
        return all((slot not in by_slot or value in by_slot[slot]) and (slot, value) not in self.excluded
                   for slot, value in reading.choices)

    def to_json(self) -> dict:
        slots = defaultdict(dict)
        for slot, value in set(self.support) | set(self.contra) | self.pinned | self.excluded:
            status = "pinned" if (slot, value) in self.pinned else "excluded" if (slot, value) in self.excluded else "allowed"
            slots[slot][value] = {"status": status, "supporting": self.support[(slot, value)],
                                  "contradicting": self.contra[(slot, value)]}
        return {"slots": dict(slots)}

    @classmethod
    def from_json(cls, data: dict) -> "Conventions":
        out = cls()
        for slot, values in data["slots"].items():
            for value, info in values.items():
                if info["status"] == "pinned":
                    out.pinned.add((slot, value))
                elif info["status"] == "excluded":
                    out.excluded.add((slot, value))
                out.support[(slot, value)] = info.get("supporting", 0)
                out.contra[(slot, value)] = info.get("contradicting", 0)
        return out


@dataclass
class Check:
    question: str
    answer: Hashable
    results: list[ReadingResult]
    asked: list[ReadingResult]
    decision: str  # pass | fail | unchecked | no_readings

    def table(self) -> str:
        """The reading table: why the answer was released or held back."""
        lines = [f"question: {self.question}", f"answer:   {self.answer!r}  ->  {self.decision}"]
        for r in self.results:
            mark = "[asked]" if r in self.asked else "       "
            got = f"error: {r.error}" if r.error else repr(r.answer)
            lines.append(f"  {mark} {r.reading.label()}: {r.reading.start:%Y-%m-%d} to {r.reading.end:%Y-%m-%d} -> {got}")
        return "\n".join(lines)


def run_readings(question: str, today: date | None, query_for: Callable[[periods.Reading], str],
                 derive: Callable[[Rows], Hashable], run: QueryFn, extra_slots: dict | None = None) -> list[ReadingResult]:
    out = []
    for reading in periods.readings(question, today, extra_slots):
        query = query_for(reading)
        try:
            out.append(ReadingResult(reading, query, derive(run(query))))
        except Exception as e:
            out.append(ReadingResult(reading, query, None, f"{type(e).__name__}: {e}"))
    return out


def decide(answer: Hashable, results: list[ReadingResult], conventions: Conventions | None = None,
           same: Callable[[Hashable, Hashable], bool] = lambda a, b: a == b) -> tuple[list[ReadingResult], str]:
    asked = [r for r in results if conventions is None or conventions.asks(r.reading)]
    if not results:
        return asked, "no_readings"
    if any(r.error is None and not same(r.answer, answer) for r in asked):
        return asked, "fail"
    if not asked or any(r.error for r in asked):
        return asked, "unchecked"
    return asked, "pass"


def check(question: str, today: date | None, answer: Hashable, query_for: Callable[[periods.Reading], str],
          derive: Callable[[Rows], Hashable], run: QueryFn, conventions: Conventions | None = None,
          extra_slots: dict | None = None, same: Callable[[Hashable, Hashable], bool] = lambda a, b: a == b) -> Check:
    """Check `answer` against every reading of the question's period (only those `conventions` allow, if given).
    `run` must be read-only."""
    results = run_readings(question, today, query_for, derive, run, extra_slots)
    asked, decision = decide(answer, results, conventions, same)
    return Check(question, answer, results, asked, decision)


def learn(examples: Iterable[tuple[list[ReadingResult], Hashable]], min_tasks: int = 3,
          same: Callable[[Hashable, Hashable], bool] = lambda a, b: a == b) -> Conventions:
    """Conventions from answered questions: each example is (the question's reading results, its right answer)."""
    out = Conventions()
    support_tasks = defaultdict(int)
    for results, key in examples:
        made = [(r.reading.choices, r.answer) for r in results if r.error is None]
        slots = defaultdict(set)
        for choices, _ in made:
            for slot, value in choices:
                slots[slot].add(value)
        for slot, values in slots.items():
            hit = {v for v in values if any(same(a, key) and (slot, v) in c for c, a in made)}
            for v in values:
                if v in hit:
                    out.support[(slot, v)] += 1
                    support_tasks[(slot, v)] += 1
                elif hit:
                    out.contra[(slot, v)] += 1
    out.excluded = {c for c in out.contra if out.support[c] == 0}
    by_slot = defaultdict(set)
    for slot, value in set(out.support) | set(out.contra):
        by_slot[slot].add(value)
    for slot, values in by_slot.items():  # if every reading of a slot would be excluded, none is
        if all((slot, v) in out.excluded for v in values):
            out.excluded -= {(slot, v) for v in values}
    out.pinned = {c for c in out.support if support_tasks[c] >= min_tasks and out.contra[c] == 0}
    return out
