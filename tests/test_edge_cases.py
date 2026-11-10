"""100 extra nldate test cases: 80 valid dates and 20 invalid inputs.

These tests encode reasonable expected behavior for common English expressions.
The course README does not prescribe all formats or semantics; a failure may
reflect an unimplemented extension rather than a required autograder behavior.
Run: uv run pytest -v tests/test_edge_cases.py
"""

from datetime import date

import pytest

from nldate import parse

VALID_CASES = [
    # Keywords, whitespace, and leap-year reference dates (8 cases)
    pytest.param(
        "today", date(2024, 2, 29), date(2024, 2, 29), id="keyword_today_leap_day"
    ),
    pytest.param(
        "TOMORROW",
        date(2024, 2, 28),
        date(2024, 2, 29),
        id="keyword_uppercase_tomorrow_leap_day",
    ),
    pytest.param(
        "yesterday",
        date(2025, 1, 1),
        date(2024, 12, 31),
        id="keyword_yesterday_cross_year",
    ),
    pytest.param(
        "  Today   ",
        date(2026, 12, 31),
        date(2026, 12, 31),
        id="keyword_today_extra_whitespace",
    ),
    pytest.param(
        "DAY AFTER TOMORROW",
        date(2025, 12, 30),
        date(2026, 1, 1),
        id="keyword_day_after_tomorrow_cross_year",
    ),
    pytest.param(
        "the day before yesterday",
        date(2024, 3, 1),
        date(2024, 2, 28),
        id="keyword_day_before_yesterday_leap_year",
    ),
    pytest.param("now", date(2025, 6, 15), date(2025, 6, 15), id="keyword_now"),
    pytest.param(
        "the day after tomorrow",
        date(2024, 2, 28),
        date(2024, 3, 1),
        id="keyword_day_after_tomorrow_leap_year",
    ),
    # ISO and US-style numeric dates (12 cases)
    pytest.param(
        "2024-02-29", date(2026, 1, 1), date(2024, 2, 29), id="iso_leap_day_2024"
    ),
    pytest.param(
        "2000-02-29", date(2026, 1, 1), date(2000, 2, 29), id="iso_century_leap_2000"
    ),
    pytest.param(
        "1900-02-28",
        date(2026, 1, 1),
        date(1900, 2, 28),
        id="iso_century_non_leap_1900",
    ),
    pytest.param(
        "2026-12-31", date(2026, 1, 1), date(2026, 12, 31), id="iso_end_of_year"
    ),
    pytest.param(
        "2025-01-01", date(2026, 1, 1), date(2025, 1, 1), id="iso_start_of_year"
    ),
    pytest.param(
        "0001-01-01", date(2026, 1, 1), date(1, 1, 1), id="iso_minimum_supported_year"
    ),
    pytest.param(
        "9999-12-31",
        date(2026, 1, 1),
        date(9999, 12, 31),
        id="iso_maximum_supported_year",
    ),
    pytest.param(
        "02/29/2024", date(2026, 1, 1), date(2024, 2, 29), id="us_numeric_leap_day"
    ),
    pytest.param(
        "12/31/2025", date(2026, 1, 1), date(2025, 12, 31), id="us_numeric_end_of_year"
    ),
    pytest.param(
        "01/01/2026", date(2025, 1, 1), date(2026, 1, 1), id="us_numeric_start_of_year"
    ),
    pytest.param(
        "2/3/2025",
        date(2025, 1, 1),
        date(2025, 2, 3),
        id="us_numeric_single_digit_month_and_day",
    ),
    pytest.param(
        " 2025-12-01 ", date(2026, 1, 1), date(2025, 12, 1), id="iso_extra_whitespace"
    ),
    # Month names, abbreviations, ordinal suffixes (12 cases)
    pytest.param(
        "Feb 29th, 2024",
        date(2026, 1, 1),
        date(2024, 2, 29),
        id="month_abbr_ordinal_leap",
    ),
    pytest.param(
        "February 29, 2000",
        date(2026, 1, 1),
        date(2000, 2, 29),
        id="month_full_leap_century",
    ),
    pytest.param(
        "FEB 28, 1900", date(2026, 1, 1), date(1900, 2, 28), id="month_uppercase_abbr"
    ),
    pytest.param(
        "February 28th, 2025",
        date(2026, 1, 1),
        date(2025, 2, 28),
        id="month_full_ordinal",
    ),
    pytest.param(
        "29 February 2024",
        date(2026, 1, 1),
        date(2024, 2, 29),
        id="day_first_full_month",
    ),
    pytest.param("1 Jan 2026", date(2025, 1, 1), date(2026, 1, 1), id="day_first_abbr"),
    pytest.param(
        "December 31st, 2025",
        date(2026, 1, 1),
        date(2025, 12, 31),
        id="month_year_end_ordinal",
    ),
    pytest.param(
        "mar 1 2024", date(2026, 1, 1), date(2024, 3, 1), id="month_abbr_lowercase"
    ),
    pytest.param(
        "October 30, 2026",
        date(2025, 1, 1),
        date(2026, 10, 30),
        id="month_full_october",
    ),
    pytest.param(
        "31 december 2025",
        date(2026, 1, 1),
        date(2025, 12, 31),
        id="day_first_lowercase",
    ),
    pytest.param(
        "September 9th",
        date(2026, 1, 1),
        date(2026, 9, 9),
        id="month_no_year_reference_year",
    ),
    pytest.param(
        "31 Dec",
        date(2026, 1, 1),
        date(2026, 12, 31),
        id="day_first_no_year_reference_year",
    ),
    # Weekdays, same-day semantics, and crossing years (13 cases)
    pytest.param(
        "next Monday",
        date(2025, 12, 1),
        date(2025, 12, 8),
        id="next_monday_when_today_is_monday",
    ),
    pytest.param(
        "last Monday",
        date(2025, 12, 1),
        date(2025, 11, 24),
        id="last_monday_when_today_is_monday",
    ),
    pytest.param(
        "this Monday",
        date(2025, 12, 1),
        date(2025, 12, 1),
        id="this_monday_when_today_is_monday",
    ),
    pytest.param(
        "next Sunday", date(2025, 12, 31), date(2026, 1, 4), id="next_sunday_cross_year"
    ),
    pytest.param(
        "last Thursday",
        date(2026, 1, 1),
        date(2025, 12, 25),
        id="last_thursday_cross_year",
    ),
    pytest.param(
        "this Friday", date(2025, 12, 31), date(2026, 1, 2), id="this_friday_cross_year"
    ),
    pytest.param(
        "next Tue", date(2026, 11, 9), date(2026, 11, 10), id="next_tuesday_abbr"
    ),
    pytest.param(
        "last Wed", date(2026, 11, 9), date(2026, 11, 4), id="last_wednesday_abbr"
    ),
    pytest.param(
        "this Wednesday", date(2026, 11, 9), date(2026, 11, 11), id="this_wednesday"
    ),
    pytest.param(
        "next fri",
        date(2026, 11, 13),
        date(2026, 11, 20),
        id="next_friday_same_weekday_abbr",
    ),
    pytest.param(
        "last sat",
        date(2026, 11, 14),
        date(2026, 11, 7),
        id="last_saturday_same_weekday_abbr",
    ),
    pytest.param(
        "this sun", date(2026, 11, 14), date(2026, 11, 15), id="this_sunday_abbr"
    ),
    pytest.param(
        "next mon",
        date(2026, 11, 15),
        date(2026, 11, 16),
        id="next_monday_abbr_from_sunday",
    ),
    # Relative days, weeks, months, years, and month-end clipping (25 cases)
    pytest.param(
        "in 1 day",
        date(2025, 12, 31),
        date(2026, 1, 1),
        id="one_day_forward_year_boundary",
    ),
    pytest.param(
        "in 30 days",
        date(2024, 1, 31),
        date(2024, 3, 1),
        id="thirty_days_forward_leap_february",
    ),
    pytest.param(
        "in 366 days",
        date(2024, 1, 1),
        date(2025, 1, 1),
        id="three_hundred_sixty_six_days",
    ),
    pytest.param(
        "1 day ago", date(2025, 1, 1), date(2024, 12, 31), id="one_day_ago_cross_year"
    ),
    pytest.param(
        "90 days ago", date(2025, 4, 1), date(2025, 1, 1), id="ninety_days_ago"
    ),
    pytest.param(
        "1 week ago",
        date(2024, 3, 1),
        date(2024, 2, 23),
        id="one_week_ago_leap_february",
    ),
    pytest.param(
        "in 2 weeks",
        date(2025, 12, 25),
        date(2026, 1, 8),
        id="two_weeks_forward_year_boundary",
    ),
    pytest.param(
        "3 weeks from now",
        date(2025, 12, 20),
        date(2026, 1, 10),
        id="three_weeks_from_now_cross_year",
    ),
    pytest.param(
        "4 days from now",
        date(2024, 2, 27),
        date(2024, 3, 2),
        id="four_days_from_now_across_leap_day",
    ),
    pytest.param(
        "two weeks ago",
        date(2024, 3, 1),
        date(2024, 2, 16),
        id="two_weeks_ago_spelled_out",
    ),
    pytest.param(
        "in three days",
        date(2025, 12, 30),
        date(2026, 1, 2),
        id="three_days_forward_spelled_out",
    ),
    pytest.param(
        "five days ago",
        date(2024, 3, 1),
        date(2024, 2, 25),
        id="five_days_ago_spelled_out",
    ),
    pytest.param(
        "a day ago", date(2024, 3, 1), date(2024, 2, 29), id="a_day_ago_leap_day"
    ),
    pytest.param(
        "a week from now", date(2025, 12, 30), date(2026, 1, 6), id="a_week_from_now"
    ),
    pytest.param(
        "in 1 month",
        date(2025, 1, 31),
        date(2025, 2, 28),
        id="one_month_forward_non_leap_clip",
    ),
    pytest.param(
        "in one month",
        date(2024, 1, 31),
        date(2024, 2, 29),
        id="one_month_forward_leap_clip_spelled_out",
    ),
    pytest.param(
        "1 month ago",
        date(2024, 3, 31),
        date(2024, 2, 29),
        id="one_month_ago_leap_clip",
    ),
    pytest.param(
        "in 12 months",
        date(2024, 2, 29),
        date(2025, 2, 28),
        id="twelve_months_forward_from_leap_day",
    ),
    pytest.param(
        "in 1 year",
        date(2024, 2, 29),
        date(2025, 2, 28),
        id="one_year_forward_from_leap_day",
    ),
    pytest.param(
        "1 year ago", date(2025, 2, 28), date(2024, 2, 28), id="one_year_ago_non_leap"
    ),
    pytest.param(
        "2 years ago",
        date(2024, 2, 29),
        date(2022, 2, 28),
        id="two_years_ago_from_leap_day",
    ),
    pytest.param(
        "in two years",
        date(2025, 12, 31),
        date(2027, 12, 31),
        id="two_years_forward_spelled_out",
    ),
    pytest.param(
        "in 13 months",
        date(2025, 11, 30),
        date(2026, 12, 30),
        id="thirteen_months_forward_cross_year",
    ),
    pytest.param(
        "1 month from now",
        date(2024, 8, 31),
        date(2024, 9, 30),
        id="one_month_from_now_clip_september",
    ),
    pytest.param(
        "in twenty days",
        date(2025, 12, 15),
        date(2026, 1, 4),
        id="twenty_days_forward_spelled_out",
    ),
    # Compound dates and dates relative to other dates (10 cases)
    pytest.param(
        "5 days before January 1st, 2026",
        date(2025, 1, 1),
        date(2025, 12, 27),
        id="five_days_before_new_year",
    ),
    pytest.param(
        "1 week after February 27th, 2024",
        date(2025, 1, 1),
        date(2024, 3, 5),
        id="week_after_leap_february",
    ),
    pytest.param(
        "2 months before March 31, 2025",
        date(2025, 1, 1),
        date(2025, 1, 31),
        id="two_months_before_month_end",
    ),
    pytest.param(
        "1 month after January 31st, 2024",
        date(2025, 1, 1),
        date(2024, 2, 29),
        id="one_month_after_leap_january_31",
    ),
    pytest.param(
        "1 year after February 29th, 2024",
        date(2025, 1, 1),
        date(2025, 2, 28),
        id="one_year_after_leap_day_clip",
    ),
    pytest.param(
        "1 year before February 29th, 2024",
        date(2025, 1, 1),
        date(2023, 2, 28),
        id="one_year_before_leap_day_clip",
    ),
    pytest.param(
        "2 years and 3 months after December 31, 2024",
        date(2025, 1, 1),
        date(2027, 3, 31),
        id="compound_two_years_three_months",
    ),
    pytest.param(
        "3 weeks after yesterday",
        date(2026, 1, 1),
        date(2026, 1, 21),
        id="three_weeks_after_yesterday",
    ),
    pytest.param(
        "two weeks from tomorrow",
        date(2025, 12, 25),
        date(2026, 1, 9),
        id="two_weeks_from_tomorrow_spelled_out",
    ),
    pytest.param(
        "4 days before next Monday",
        date(2025, 12, 31),
        date(2026, 1, 1),
        id="four_days_before_next_monday",
    ),
]


INVALID_CASES = [
    pytest.param("", date(2025, 1, 1), id="invalid_empty_string"),
    pytest.param("   ", date(2025, 1, 1), id="invalid_whitespace_only"),
    pytest.param("not a date", date(2025, 1, 1), id="invalid_unrelated_words"),
    pytest.param("February 30, 2025", date(2025, 1, 1), id="invalid_february_30"),
    pytest.param("2025-02-29", date(2025, 1, 1), id="invalid_non_leap_february_29_iso"),
    pytest.param("2024-02-30", date(2025, 1, 1), id="invalid_leap_february_30_iso"),
    pytest.param("2025-13-01", date(2025, 1, 1), id="invalid_iso_month_13"),
    pytest.param("2025-00-10", date(2025, 1, 1), id="invalid_iso_month_zero"),
    pytest.param("2025-01-00", date(2025, 1, 1), id="invalid_iso_day_zero"),
    pytest.param(
        "13/32/2025", date(2025, 1, 1), id="invalid_numeric_month_13_and_day_32"
    ),
    pytest.param(
        "02/29/2025", date(2025, 1, 1), id="invalid_numeric_non_leap_february_29"
    ),
    pytest.param("31 April 2025", date(2025, 1, 1), id="invalid_april_31_day_first"),
    pytest.param(
        "September 31st, 2025", date(2025, 1, 1), id="invalid_september_31_ordinal"
    ),
    pytest.param("yesterdays", date(2025, 1, 1), id="invalid_misspelled_yesterday"),
    pytest.param("next Funday", date(2025, 1, 1), id="invalid_weekday_name"),
    pytest.param("in days", date(2025, 1, 1), id="invalid_missing_duration_count"),
    pytest.param("two elephants ago", date(2025, 1, 1), id="invalid_duration_unit"),
    pytest.param(
        "1 month before nonsense", date(2025, 1, 1), id="invalid_relative_anchor"
    ),
    pytest.param(
        "1 day after 9999-12-31",
        date(2025, 1, 1),
        id="invalid_day_overflow_after_max_date",
    ),
    pytest.param(
        "1 month before 0001-01-01",
        date(2025, 1, 1),
        id="invalid_month_underflow_before_min_date",
    ),
]


@pytest.mark.parametrize(("expression", "reference", "expected"), VALID_CASES)
def test_parse_special_valid_dates(
    expression: str, reference: date, expected: date
) -> None:
    assert parse(expression, today=reference) == expected


@pytest.mark.parametrize(("expression", "reference"), INVALID_CASES)
def test_parse_special_invalid_dates(expression: str, reference: date) -> None:
    with pytest.raises(ValueError):
        parse(expression, today=reference)
