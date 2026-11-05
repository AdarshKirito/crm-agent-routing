"""Release rules and their certificate.

An agent answers each question k times. A release rule decides from those runs (and anything else it is given,
such as a reading check) whether to give the answer or withhold it. `certify` runs fixed-sequence Learn-then-Test
(Angelopoulos et al., 2021) over a list of rules ordered strictest first, on questions with known answers: each
rule's null hypothesis is "risk above alpha", tested with an exact binomial p-value; testing stops at the first
rule that is not certified, and of the certified rules the one that answers the most questions is chosen. With
probability at least 1 - delta over the draw of the calibration questions, the chosen rule's risk (the share of
wrong answers among those it gives) on new questions from the same distribution is at most alpha.

The guarantee assumes the new questions are exchangeable with the calibration ones, and "wrong" is relative to the
labels you calibrate on. Ported from crmroute's release layer (scripts/release_eval.py, scripts/release3.py).
"""
import math
from collections.abc import Callable, Hashable, Iterable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Run:
    answer: Hashable
    correct: bool | None = None  # known on calibration and test questions only
    flags: frozenset = frozenset()  # soft warnings a rule may refuse, e.g. {"budget", "tool_error"}


@dataclass
class Question:
    id: Hashable
    kind: str  # the question's predicted type; a rule may withhold whole types
    runs: list[Run]
    gate: str | None = None  # an optional reading check's decision: pass | fail | unchecked | no_readings
    extra: dict = field(default_factory=dict)


Rule = Callable[[Question], bool]


def agreement_rule(runs: int | None = None, refuse_flags: Iterable[str] = (), withhold_kinds: Iterable[str] = (),
                   gated_kinds: Iterable[str] = (), name: str | None = None) -> Rule:
    """Release when the first `runs` runs (all, if None) give the same answer, none carries a refused flag, the
    question's type is not withheld, and, for a gated type, the reading check passed."""
    refuse, withheld, gated = frozenset(refuse_flags), frozenset(withhold_kinds), frozenset(gated_kinds)

    def rule(q: Question) -> bool:
        if q.kind in withheld:
            return False
        considered = q.runs[:runs] if runs else q.runs
        if not considered or any(r.answer != considered[0].answer or r.flags & refuse for r in considered):
            return False
        return q.kind not in gated or q.gate == "pass"

    parts = [f"{'all' if runs is None else runs} runs agree"]
    if refuse:
        parts.append("no " + "/".join(sorted(refuse)))
    if withheld:
        parts.append("withhold " + "/".join(sorted(withheld)))
    if gated:
        parts.append("reading check on " + "/".join(sorted(gated)))
    rule.__name__ = name or ", ".join(parts)
    return rule


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def upper_bound(errors: int, n: int, delta: float) -> float:
    """Exact (Clopper-Pearson) one-sided upper confidence bound on an error rate, at confidence 1 - delta."""
    if n == 0 or errors >= n:
        return 1.0
    lo, hi = errors / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_cdf(errors, n, mid) > delta:
            lo = mid
        else:
            hi = mid
    return hi


@dataclass(frozen=True)
class Outcome:
    rule: str
    questions: int
    released: int
    wrong: int
    coverage: float
    risk: float
    risk_upper: float
    p_value: float | None = None
    certified: bool | None = None


def evaluate(questions: list[Question], rule: Rule, delta: float = 0.05) -> Outcome:
    """Coverage and risk of `rule`, scored on the first run's answer (the runs a rule releases agree)."""
    released = [q for q in questions if rule(q)]
    if any(q.runs[0].correct is None for q in released):
        raise ValueError("every released question needs a known answer (Run.correct) to be scored")
    wrong = sum(not q.runs[0].correct for q in released)
    n = len(released)
    return Outcome(rule.__name__, len(questions), n, wrong, n / len(questions) if questions else 0.0,
                   wrong / n if n else 0.0, upper_bound(wrong, n, delta))


@dataclass
class Certificate:
    rule: Rule | None  # None: no rule was certified, so every answer is withheld
    alpha: float
    delta: float
    tested: list[Outcome]

    def table(self) -> str:
        lines = ["rule | answered | wrong | risk | p-value | certified"]
        for o in self.tested:
            lines.append(f"{o.rule} | {o.released} of {o.questions} ({100 * o.coverage:.1f}%) | {o.wrong} | "
                         f"{100 * o.risk:.1f}% | {o.p_value:.4f} | {'yes' if o.certified else 'no'}")
        lines.append(f"chosen: {self.rule.__name__ if self.rule else 'none (withhold every answer)'}")
        return "\n".join(lines)


def certify(calibration: list[Question], rules: list[Rule], alpha: float = 0.10, delta: float = 0.10) -> Certificate:
    """Fixed-sequence Learn-then-Test over `rules`, strictest first. Commit the chosen rule before you look at
    any test question."""
    tested, best = [], None
    for rule in rules:
        o = evaluate(calibration, rule, delta)
        p = binom_cdf(o.wrong, o.released, alpha) if o.released else 1.0
        o = Outcome(**{**o.__dict__, "p_value": p, "certified": p <= delta})
        tested.append(o)
        if not o.certified:
            break
        if best is None or o.released > best[1].released:
            best = (rule, o)
    return Certificate(best[0] if best else None, alpha, delta, tested)
