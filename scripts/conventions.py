"""Convention readings of a question's period (round 3, docs/checkable3_devlog.md).

`period_of` finds the period a question names: a rolling one ("the past 3 quarters"), a calendar month,
quarter or season with its year, or none. `readings` lists one window per combination of the readings that
data/conventions_catalog.yaml declares for the slots the period triggers, for one task type. The ties slot is
applied to derivations, not windows (agent/app/derivation.py, Derived.answers). Windows are half-open
[start, end) in UTC; "today" is the task context's "Today's date".
"""
import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from functools import cache
from itertools import product
from pathlib import Path

import yaml

CATALOG = Path(__file__).resolve().parents[1] / "data" / "conventions_catalog.yaml"
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december")
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12}
# first month of each season of year Y under each season_months reading (meteorological winter is the year slot's)
FIRST_MONTH = {"meteorological": {"spring": 3, "summer": 6, "fall": 9},
               "quarter_aligned": {"winter": 1, "spring": 4, "summer": 7, "fall": 10}}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4}
DATE_FIELD_TYPES = ("best_region_identification", "handle_time")
# The slots and readings this code implements, in the catalog's order (checked against the catalog).
IMPLEMENTED = {"season_months": ("meteorological", "quarter_aligned"),
               "season_year": ("december_of_y", "december_before_y"),
               "past_quarters": ("rolling", "calendar"), "past_months_years": ("rolling", "calendar"),
               "rolling_end": ("today_counted", "today_not_counted"), "date_field": ("CreatedDate", "ClosedDate"),
               "ties": ("none", "first")}

UNIT = r"(day|week|fortnight|month|quarter|year)s?"
NUMBER = r"(\d+(?:\.\d+)?|" + "|".join(WORDS) + r")"
RELATIVE = re.compile(rf"\b(?:past|last|previous|preceding|recent)\s+(?:{NUMBER}\s+)?{UNIT}\b", re.I)
HALF_YEAR = re.compile(r"\b(?:past|last|previous|preceding|recent)\s+half(?:-|\s+a\s+|\s+)year\b", re.I)
BARE_COUNT = re.compile(r"\b(?:past|last|previous|preceding|recent)\s+(\d+|" + "|".join(WORDS) + r")\b", re.I)
QUARTER = re.compile(r"\bQ([1-4])\s*(?:of\s+)?(\d{4})\b|\b(first|second|third|fourth)\s+quarter\s+(?:of\s+)?(\d{4})\b", re.I)
MONTH = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(?:of\s+)?(\d{4})\b", re.I)
SEASON = re.compile(r"\b(winter|spring|summer|fall|autumn)\s+(?:of\s+)?(\d{4})\b|\b(\d{4})\s+(winter|spring|summer|fall|autumn)\b", re.I)
TODAY = re.compile(r"Today's date:\s*(\d{4}-\d{2}-\d{2})")


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
    choices: tuple  # ((slot, reading), ...) in catalog order
    start: datetime
    end: datetime
    field: str | None  # the date field (best_region_identification, handle_time), else None: the type's own

    def label(self) -> str:
        return ";".join(f"{s}={r}" for s, r in self.choices)


@cache
def catalog() -> dict:
    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    declared = {slot: tuple(spec["readings"]) for slot, spec in data["slots"].items()}
    if declared != IMPLEMENTED:
        raise SystemExit(f"{CATALOG.name} declares {declared}, the code implements {IMPLEMENTED}")
    return data


def today_of(context: str) -> date | None:
    m = TODAY.search(context or "")
    return date.fromisoformat(m.group(1)) if m else None


def _count(text: str) -> float:
    return float(text) if text[0].isdigit() else float(WORDS[text.lower()])


def period_of(question: str) -> Period:
    """The period a question names. Years alone are not periods: product names carry model years."""
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


def _utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def months_back(d: date, n: int) -> date:
    y, m = divmod(d.year * 12 + d.month - 1 - n, 12)
    return date(y, m + 1, min(d.day, calendar.monthrange(y, m + 1)[1]))


def _month_start(year: int, month: int) -> date:
    y, m = divmod(year * 12 + month - 1, 12)
    return date(y, m + 1, 1)


def _windows(period: Period, today: date | None) -> list[tuple[tuple, date, date]]:
    """(choices, first day, day after the last) for every reading combination of the period's window slots."""
    if period.kind == "month":
        start = date(period.year, period.index, 1)
        return [((), start, _month_start(period.year, period.index + 1))]
    if period.kind == "quarter":
        start = date(period.year, 3 * period.index - 2, 1)
        return [((), start, _month_start(period.year, 3 * period.index + 1))]
    if period.kind == "season":
        out = []
        for months in IMPLEMENTED["season_months"]:
            if period.season == "winter" and months == "meteorological":
                for year in IMPLEMENTED["season_year"]:
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
    for kind in (IMPLEMENTED[slot] if slot else ("rolling",)):
        if kind == "calendar":
            current = (date(today.year, 3 * ((today.month - 1) // 3) + 1, 1) if unit == "quarter" else
                       date(today.year, today.month, 1) if unit == "month" else date(today.year, 1, 1))
            out.append((((slot, "calendar"),), months_back(current, int(round(months))), current))
            continue
        if months is not None:
            start = months_back(today, int(round(months)))
        else:
            start = today - timedelta(days=round(n * (7 if unit == "week" else 1)))
        for end in IMPLEMENTED["rolling_end"]:
            choices = (((slot, "rolling"),) if slot else ()) + (("rolling_end", end),)
            out.append((choices, start, today + timedelta(days=1) if end == "today_counted" else today))
    return out


def readings(period: Period, task_type: str, today: date | None) -> list[Reading]:
    """One Reading per combination of declared readings of the slots the period triggers in this type."""
    catalog()
    fields = IMPLEMENTED["date_field"] if task_type in DATE_FIELD_TYPES else (None,)
    out = []
    for (choices, start, end), field in product(_windows(period, today), fields):
        out.append(Reading(choices + ((("date_field", field),) if field else ()), _utc(start), _utc(end), field))
    return out
