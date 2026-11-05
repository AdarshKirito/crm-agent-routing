"""The periods business questions name, and every reading of them.

"Winter of 2023", "the past 3 quarters" and "last month" each have more than one defensible window. `period_of`
finds the period a question names; `readings` lists one window per combination of the declared readings of the
slots that period triggers. Windows are half-open [start, end) in UTC, and "today" is the date the question is
asked on. Ported from crmroute's round-3 convention catalog (scripts/conventions.py).

Declared slots (`SLOTS`):

- season_months: meteorological (winter Dec-Feb, spring Mar-May, ...) or quarter_aligned (winter Jan-Mar, ...)
- season_year: for a meteorological "winter Y", December of Y or December of Y-1
- past_quarters: rolling (3N months back from today) or calendar (the N completed quarters before this one)
- past_months_years: rolling or calendar, as for quarters
- rolling_end: a rolling window counts today, or ends before it
"""
import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from itertools import product

MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december")
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12}
FIRST_MONTH = {"meteorological": {"spring": 3, "summer": 6, "fall": 9},
               "quarter_aligned": {"winter": 1, "spring": 4, "summer": 7, "fall": 10}}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4}
SLOTS = {"season_months": ("meteorological", "quarter_aligned"),
         "season_year": ("december_of_y", "december_before_y"),
         "past_quarters": ("rolling", "calendar"), "past_months_years": ("rolling", "calendar"),
         "rolling_end": ("today_counted", "today_not_counted")}

UNIT = r"(day|week|fortnight|month|quarter|year)s?"
NUMBER = r"(\d+(?:\.\d+)?|" + "|".join(WORDS) + r")"
RELATIVE = re.compile(rf"\b(?:past|last|previous|preceding|recent)\s+(?:{NUMBER}\s+)?{UNIT}\b", re.I)
HALF_YEAR = re.compile(r"\b(?:past|last|previous|preceding|recent)\s+half(?:-|\s+a\s+|\s+)year\b", re.I)
BARE_COUNT = re.compile(r"\b(?:past|last|previous|preceding|recent)\s+(\d+|" + "|".join(WORDS) + r")\b", re.I)
QUARTER = re.compile(r"\bQ([1-4])\s*(?:of\s+)?(\d{4})\b|\b(first|second|third|fourth)\s+quarter\s+(?:of\s+)?(\d{4})\b", re.I)
MONTH = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(?:of\s+)?(\d{4})\b", re.I)
SEASON = re.compile(r"\b(winter|spring|summer|fall|autumn)\s+(?:of\s+)?(\d{4})\b|\b(\d{4})\s+(winter|spring|summer|fall|autumn)\b",
                    re.I)


@dataclass(frozen=True)
class Period:
    kind: str  # relative | month | quarter | season | none
    text: str = ""
    unit: str | None = None  # relative: day, week, month, quarter or year
    n: float | None = None  # relative: how many units
    year: int | None = None
    index: int | None = None  # month 1-12 or quarter 1-4
    season: str | None = None


@dataclass(frozen=True)
class Reading:
    """One window of a period under one combination of readings, plus any extra slots the caller declared."""
    choices: tuple  # ((slot, reading), ...)
    start: datetime
    end: datetime

    def get(self, slot: str, default=None):
        return dict(self.choices).get(slot, default)

    def label(self) -> str:
        return "; ".join(f"{s} = {r}" for s, r in self.choices) or "the period as named"


def _count(text: str) -> float:
    return float(text) if text[0].isdigit() else float(WORDS[text.lower()])


def period_of(question: str) -> Period:
    """The period a question names. A year alone is not a period: product names carry model years."""
    q = question or ""
    m = QUARTER.search(q)
    if m:
        index = int(m.group(1)) if m.group(1) else ORDINALS[m.group(3).lower()]
        return Period("quarter", m.group(0), year=int(m.group(2) or m.group(4)), index=index)
    m = MONTH.search(q)
    if m:
        return Period("month", m.group(0), year=int(m.group(2)), index=MONTHS.index(m.group(1).lower()) + 1)
    m = SEASON.search(q)
    if m:
        name = (m.group(1) or m.group(4)).lower()
        return Period("season", m.group(0), year=int(m.group(2) or m.group(3)), season="fall" if name == "autumn" else name)
    m = HALF_YEAR.search(q)
    if m:
        return Period("relative", m.group(0), unit="month", n=6.0)
    m = RELATIVE.search(q)
    if m:
        unit, n = m.group(2).lower(), _count(m.group(1)) if m.group(1) else 1.0
        if unit == "fortnight":
            unit, n = "week", 2 * n
        if unit == "year" and n != int(n):
            unit, n = "month", 12 * n
        return Period("relative", m.group(0), unit=unit, n=n)
    m = BARE_COUNT.search(q)  # "within the last 11 where ...": the unit is the question's other unit
    if m and re.search(r"\bmonths?\b", q, re.I):
        return Period("relative", m.group(0), unit="month", n=_count(m.group(1)))
    return Period("none")


def months_back(d: date, n: int) -> date:
    y, m = divmod(d.year * 12 + d.month - 1 - n, 12)
    return date(y, m + 1, min(d.day, calendar.monthrange(y, m + 1)[1]))


def _month_start(year: int, month: int) -> date:
    y, m = divmod(year * 12 + month - 1, 12)
    return date(y, m + 1, 1)


def _utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def windows(period: Period, today: date | None) -> list[tuple[tuple, date, date]]:
    """(choices, first day, day after the last day) for every reading combination of the period's slots."""
    if period.kind == "month":
        return [((), date(period.year, period.index, 1), _month_start(period.year, period.index + 1))]
    if period.kind == "quarter":
        return [((), date(period.year, 3 * period.index - 2, 1), _month_start(period.year, 3 * period.index + 1))]
    if period.kind == "season":
        out = []
        for months in SLOTS["season_months"]:
            if period.season == "winter" and months == "meteorological":
                for year in SLOTS["season_year"]:
                    y = period.year if year == "december_of_y" else period.year - 1
                    out.append(((("season_months", months), ("season_year", year)), date(y, 12, 1), date(y + 1, 3, 1)))
            else:
                first = FIRST_MONTH[months][period.season]
                out.append(((("season_months", months),), date(period.year, first, 1), _month_start(period.year, first + 3)))
        return out
    if period.kind != "relative" or today is None:
        return []
    out = []
    n, unit = period.n, period.unit
    slot = {"quarter": "past_quarters", "month": "past_months_years", "year": "past_months_years"}.get(unit)
    months = {"quarter": 3 * n, "month": n, "year": 12 * n}.get(unit)
    for kind in (SLOTS[slot] if slot else ("rolling",)):
        if kind == "calendar":
            current = (date(today.year, 3 * ((today.month - 1) // 3) + 1, 1) if unit == "quarter" else
                       date(today.year, today.month, 1) if unit == "month" else date(today.year, 1, 1))
            out.append((((slot, "calendar"),), months_back(current, int(round(months))), current))
            continue
        start = (months_back(today, int(round(months))) if months is not None
                 else today - timedelta(days=round(n * (7 if unit == "week" else 1))))
        for end in SLOTS["rolling_end"]:
            choices = (((slot, "rolling"),) if slot else ()) + (("rolling_end", end),)
            out.append((choices, start, today + timedelta(days=1) if end == "today_counted" else today))
    return out


def readings(question: str, today: date | None, extra_slots: dict | None = None) -> list[Reading]:
    """Every reading of the period `question` names, crossed with the caller's own slots (for example
    {"date_field": ("created_at", "closed_at")}). A question that names no period has no readings."""
    extra = list((extra_slots or {}).items())
    out = []
    for choices, start, end in windows(period_of(question), today):
        for picks in product(*[[(slot, r) for r in values] for slot, values in extra]):
            out.append(Reading(choices + tuple(picks), _utc(start), _utc(end)))
    return out
