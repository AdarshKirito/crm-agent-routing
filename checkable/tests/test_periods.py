from datetime import date, datetime, timezone

from checkable import period_of, readings


def utc(y, m, d):
    return datetime(y, m, d, tzinfo=timezone.utc)


def windows(question, today=None, extra=None):
    return {r.choices: (r.start, r.end) for r in readings(question, today, extra)}


def test_winter_has_both_years_and_the_quarter_aligned_reading():
    w = windows("Which state had the most cases in winter of 2023?")
    assert w[(("season_months", "meteorological"), ("season_year", "december_of_y"))] == (utc(2023, 12, 1), utc(2024, 3, 1))
    assert w[(("season_months", "meteorological"), ("season_year", "december_before_y"))] == (utc(2022, 12, 1), utc(2023, 3, 1))
    assert w[(("season_months", "quarter_aligned"),)] == (utc(2023, 1, 1), utc(2023, 4, 1))
    assert len(w) == 3


def test_past_quarters_rolling_and_calendar():
    w = windows("cases in the past 2 quarters", date(2023, 8, 20))
    assert w[(("past_quarters", "rolling"), ("rolling_end", "today_counted"))] == (utc(2023, 2, 20), utc(2023, 8, 21))
    assert w[(("past_quarters", "rolling"), ("rolling_end", "today_not_counted"))] == (utc(2023, 2, 20), utc(2023, 8, 20))
    assert w[(("past_quarters", "calendar"),)] == (utc(2023, 1, 1), utc(2023, 7, 1))


def test_month_and_quarter_have_one_reading():
    assert windows("revenue in March 2021") == {(): (utc(2021, 3, 1), utc(2021, 4, 1))}
    assert windows("revenue in Q4 2021") == {(): (utc(2021, 10, 1), utc(2022, 1, 1))}


def test_relative_period_needs_today_and_a_bare_year_is_no_period():
    assert readings("cases in the past 3 months", None) == []
    assert period_of("the 2021 Trail Runner shoe").kind == "none"


def test_extra_slots_cross_every_window():
    w = windows("summer 2021", extra={"date_field": ("created_at", "closed_at")})
    assert len(w) == 4
    assert (("season_months", "meteorological"), ("date_field", "closed_at")) in w
