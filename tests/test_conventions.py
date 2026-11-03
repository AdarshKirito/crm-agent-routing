"""Round-3 convention readings: periods found in questions and the windows of each declared reading."""
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import conventions as CV


def day(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)


def windows(question: str, task_type: str, today: str | None = None) -> dict:
    period = CV.period_of(question)
    return {r.label(): (r.start.date().isoformat(), r.end.date().isoformat())
            for r in CV.readings(period, task_type, date.fromisoformat(today) if today else None)}


def test_the_catalog_declares_what_the_code_implements():
    assert CV.catalog()["version"] == 0


def test_periods_in_questions():
    p = CV.period_of
    assert (p("In the past four months, which agent").unit, p("In the past four months, which agent").n) == ("month", 4)
    assert (p("over the last 3 quarters").kind, p("over the last 3 quarters").n) == ("relative", 3)
    assert (p("in the past 6 weeks").unit, p("in the past 2 fortnights").n) == ("week", 4)
    assert (p("in the past half-year").unit, p("in the past half-year").n) == ("month", 6)
    assert (p("over the past 1.5 years").unit, p("over the past 1.5 years").n) == ("month", 18)
    assert (p("over the past year").unit, p("over the past year").n) == ("year", 1)
    assert p("months within the last 11 where").n == 11
    assert (p("in Q3 2023").index, p("in the fourth quarter of 2022").index, p("during Q1 of 2021").year) == (3, 4, 2021)
    assert (p("in May 2021").kind, p("in May 2021").index) == ("month", 5)
    assert (p("during the winter of 2023").season, p("in Winter 2021").year, p("the 2021 winter").year) == ("winter", 2021, 2021)
    assert p("in autumn 2020").season == "fall"
    # model years in product names are not periods
    assert p("cases for the 2022 Toyota Camry Hybrid in the past 6 quarters").unit == "quarter"
    assert p("Use the case routing policy to determine the most suitable agent").kind == "none"


def test_winter_of_y_has_both_years_and_a_quarter_aligned_reading():
    w = windows("Which states had the quickest case closures during the winter of 2023?", "best_region_identification")
    assert w["season_months=meteorological;season_year=december_of_y;date_field=ClosedDate"] == ("2023-12-01", "2024-03-01")
    assert w["season_months=meteorological;season_year=december_before_y;date_field=CreatedDate"] == ("2022-12-01", "2023-03-01")
    assert w["season_months=quarter_aligned;date_field=CreatedDate"] == ("2023-01-01", "2023-04-01")
    assert len(w) == 6  # three windows, two date fields


def test_other_seasons_and_calendar_periods():
    assert windows("in fall 2022", "top_issue_identification") == {
        "season_months=meteorological": ("2022-09-01", "2022-12-01"), "season_months=quarter_aligned": ("2022-10-01", "2023-01-01")}
    assert windows("in the fourth quarter of 2022", "top_issue_identification") == {"": ("2022-10-01", "2023-01-01")}
    assert windows("in December 2022", "top_issue_identification") == {"": ("2022-12-01", "2023-01-01")}


def test_rolling_and_calendar_readings_of_past_periods():
    w = windows("In the past 3 quarters, which agent had the lowest average handle time?", "transfer_count", "2022-07-12")
    assert w == {"past_quarters=rolling;rolling_end=today_counted": ("2021-10-12", "2022-07-13"),
                 "past_quarters=rolling;rolling_end=today_not_counted": ("2021-10-12", "2022-07-12"),
                 "past_quarters=calendar": ("2021-10-01", "2022-07-01")}
    w = windows("over the last 4 months", "monthly_trend_analysis", "2023-03-16")
    assert w["past_months_years=calendar"] == ("2022-11-01", "2023-03-01")
    assert w["past_months_years=rolling;rolling_end=today_counted"] == ("2022-11-16", "2023-03-17")
    assert windows("in the past year", "monthly_trend_analysis", "2021-04-10")["past_months_years=calendar"] == ("2020-01-01", "2021-01-01")
    assert windows("in the last 2 weeks", "transfer_count", "2022-03-06") == {
        "rolling_end=today_counted": ("2022-02-20", "2022-03-07"), "rolling_end=today_not_counted": ("2022-02-20", "2022-03-06")}
    assert windows("in the past 3 quarters", "transfer_count") == {}  # no today's date: no window


def test_months_back_keeps_the_day_within_the_month():
    assert CV.months_back(date(2023, 3, 31), 1) == date(2023, 2, 28)
    assert CV.months_back(date(2024, 1, 15), 13) == date(2022, 12, 15)
    assert CV.today_of("## Handle Time Policy ...\n\n## Today's date: 2023-09-02") == date(2023, 9, 2)
