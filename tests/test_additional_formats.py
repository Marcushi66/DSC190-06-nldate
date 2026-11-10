"""Regression tests for Gradescope feedback and nearby common input formats."""

from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("expression", "reference", "expected"),
    [
        # Explicitly reported by Gradescope.
        ("2025/12/04", date(2026, 1, 1), date(2025, 12, 4)),
        ("Dec. 1, 2025", date(2026, 1, 1), date(2025, 12, 1)),
        # Full and abbreviated month names, dotted abbreviations, and extra spaces.
        ("Dec 1, 2025", date(2026, 1, 1), date(2025, 12, 1)),
        ("Dec.1,2025", date(2026, 1, 1), date(2025, 12, 1)),
        ("DEC. 1ST, 2025", date(2026, 1, 1), date(2025, 12, 1)),
        ("Jan. 15, 2026", date(2025, 1, 1), date(2026, 1, 15)),
        ("Feb. 29, 2024", date(2025, 1, 1), date(2024, 2, 29)),
        ("Mar. 3rd, 2025", date(2025, 1, 1), date(2025, 3, 3)),
        ("Apr. 30, 2024", date(2025, 1, 1), date(2024, 4, 30)),
        ("Jun. 1, 2025", date(2025, 1, 1), date(2025, 6, 1)),
        ("Jul. 4, 2026", date(2025, 1, 1), date(2026, 7, 4)),
        ("Aug. 7, 2025", date(2025, 1, 1), date(2025, 8, 7)),
        ("Sept. 9, 2025", date(2025, 1, 1), date(2025, 9, 9)),
        ("Sep. 9, 2025", date(2025, 1, 1), date(2025, 9, 9)),
        ("Oct. 31, 2025", date(2025, 1, 1), date(2025, 10, 31)),
        ("Nov. 10, 2026", date(2025, 1, 1), date(2026, 11, 10)),
        ("1 Dec. 2025", date(2025, 1, 1), date(2025, 12, 1)),
        ("1st of December 2025", date(2025, 1, 1), date(2025, 12, 1)),
        ("the 1st of Dec 2025", date(2025, 1, 1), date(2025, 12, 1)),
        ("December 1,2025", date(2025, 1, 1), date(2025, 12, 1)),
        ("December 1st", date(2026, 1, 1), date(2026, 12, 1)),
        ("31 Dec.", date(2026, 1, 1), date(2026, 12, 31)),
        ("on February 29th, 2024", date(2025, 1, 1), date(2024, 2, 29)),
        # Year-first and US numeric styles.
        ("2025/2/3", date(2026, 1, 1), date(2025, 2, 3)),
        ("2025.12.04", date(2026, 1, 1), date(2025, 12, 4)),
        ("2025-12-04", date(2026, 1, 1), date(2025, 12, 4)),
        ("12/04/2025", date(2026, 1, 1), date(2025, 12, 4)),
        ("12-04-2025", date(2026, 1, 1), date(2025, 12, 4)),
        ("12.04.2025", date(2026, 1, 1), date(2025, 12, 4)),
        ("2024/2/29", date(2026, 1, 1), date(2024, 2, 29)),
        ("0001/1/1", date(2026, 1, 1), date(1, 1, 1)),
        ("9999/12/31", date(2026, 1, 1), date(9999, 12, 31)),
        # Relative weekdays and simple week/month/year shorthand.
        ("next Friday", date(2025, 12, 5), date(2025, 12, 12)),
        ("last Friday", date(2025, 12, 5), date(2025, 11, 28)),
        ("this Friday", date(2025, 12, 5), date(2025, 12, 5)),
        ("previous Sunday", date(2025, 12, 1), date(2025, 11, 30)),
        ("coming Saturday", date(2025, 12, 1), date(2025, 12, 6)),
        ("next day", date(2025, 12, 31), date(2026, 1, 1)),
        ("last day", date(2026, 1, 1), date(2025, 12, 31)),
        ("next week", date(2025, 12, 31), date(2026, 1, 7)),
        ("last month", date(2024, 3, 31), date(2024, 2, 29)),
        ("next year", date(2024, 2, 29), date(2025, 2, 28)),
        ("this Friday", date(2025, 12, 31), date(2026, 1, 2)),
        # Relative durations, word numbers, date anchors, and cross-month arithmetic.
        ("in twenty-one days", date(2025, 12, 15), date(2026, 1, 5)),
        ("in thirty two days", date(2025, 12, 1), date(2026, 1, 2)),
        ("in 0 days", date(2025, 12, 1), date(2025, 12, 1)),
        ("in two weeks", date(2025, 12, 1), date(2025, 12, 15)),
        ("two weeks and three days ago", date(2025, 12, 31), date(2025, 12, 14)),
        ("in 1 month, 2 days", date(2025, 1, 31), date(2025, 3, 2)),
        ("in 1 month 2 days", date(2025, 1, 31), date(2025, 3, 2)),
        ("5 days before Dec. 1, 2025", date(2025, 1, 1), date(2025, 11, 26)),
        ("5 days after 2025/12/04", date(2025, 1, 1), date(2025, 12, 9)),
        ("2 weeks from tomorrow", date(2025, 12, 1), date(2025, 12, 16)),
        ("3 days from now", date(2025, 12, 1), date(2025, 12, 4)),
        ("3 days from today", date(2025, 12, 1), date(2025, 12, 4)),
        ("1 year and 2 months after yesterday", date(2025, 12, 3), date(2027, 2, 2)),
        ("5 days before next Monday", date(2025, 12, 3), date(2025, 12, 3)),
        ("1 month after Jan. 31, 2024", date(2026, 1, 1), date(2024, 2, 29)),
        ("4 days later", date(2025, 12, 1), date(2025, 12, 5)),
        ("4 days earlier", date(2025, 12, 1), date(2025, 11, 27)),
        # Calendar boundaries; weekday prefixes validated against actual dates.
        ("the first day of Dec. 2025", date(2025, 1, 1), date(2025, 12, 1)),
        ("last day of February 2024", date(2025, 1, 1), date(2024, 2, 29)),
        ("start of this month", date(2025, 12, 13), date(2025, 12, 1)),
        ("end of next month", date(2024, 1, 31), date(2024, 2, 29)),
        ("end of last month", date(2025, 3, 17), date(2025, 2, 28)),
        ("Monday, Dec. 1, 2025", date(2026, 1, 1), date(2025, 12, 1)),
        ("Thu, Dec. 4, 2025", date(2026, 1, 1), date(2025, 12, 4)),
    ],
)
def test_additional_valid(expression: str, reference: date, expected: date) -> None:
    assert parse(expression, today=reference) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "not a date",
        "2025/13/01",
        "2025/02/29",
        "2025.02.29",
        "2024-13-01",
        "04/31/2025",
        "31/04/2025",
        "Feb. 30, 2025",
        "Feb. 29, 2025",
        "Apr. 31, 2025",
        "1 month after nonsense",
        "4 weeks ago on Monday",
        "in -5 days",
        "in 5 elephants",
        "in two hundred days",
        "in 2 days and bananas",
        "1 day after 9999/12/31",
        "1 month before 0001/01/01",
        "Tuesday, Dec. 1, 2025",
        "in 1.5 months",
        "next Funday",
        "December 35th, 2025",
        "2025/00/01",
        "2025/12/00",
    ],
)
def test_additional_invalid(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, today=date(2025, 12, 3))
