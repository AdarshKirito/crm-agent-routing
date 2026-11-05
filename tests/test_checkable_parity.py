"""The standalone checkable package (checkable/) against crmroute's own round-3 code it was ported from."""
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "checkable" / "src"))
import conventions as CV  # noqa: E402
import release_eval as RE  # noqa: E402

from checkable import periods, release  # noqa: E402

QUESTIONS = [
    "Which state had the fastest case resolutions in Winter 2020?",
    "Which agent handled the most cases in the past 3 quarters?",
    "the past four months", "over the last 2 years", "in the past half-year", "over the past 1.5 years",
    "in the past 6 weeks", "in the past 2 fortnights", "the last 10 days", "in Q3 2021", "the second quarter of 2022",
    "in March 2021", "summer of 2021", "2022 autumn", "within the last 11 where the months are counted",
    "the 2021 Trail Runner shoe",
]


def crm(question: str, today: date) -> set:
    return {(tuple(c for c in r.choices if c[0] != "date_field"), r.start, r.end)
            for r in CV.readings(CV.period_of(question), "monthly_trend_analysis", today)}


def ours(question: str, today: date) -> set:
    return {(r.choices, r.start, r.end) for r in periods.readings(question, today)}


def test_periods_and_windows_match_crmroute():
    for today in (date(2020, 10, 12), date(2023, 8, 20), date(2024, 2, 29)):
        for q in QUESTIONS:
            assert CV.period_of(q).__dict__ == periods.period_of(q).__dict__, q
            assert crm(q, today) == ours(q, today), (q, today)


def test_upper_bound_and_binomial_match_crmroute():
    rng = random.Random(0)
    for _ in range(200):
        n = rng.randrange(0, 400)
        k = rng.randrange(0, n + 1) if n else 0
        delta = rng.choice((0.05, 0.10))
        assert release.upper_bound(k, n, delta) == RE.upper_bound(k, n, delta)
        assert release.binom_cdf(k, n, 0.1) == RE.binom_cdf(k, n, 0.1)
