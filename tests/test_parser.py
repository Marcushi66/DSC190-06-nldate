from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    "text, today, expected",
    [
        ("today", date(2025, 12, 3), date(2025, 12, 3)),
        ("tomorrow", date(2025, 12, 3), date(2025, 12, 4)),
        ("yesterday", date(2025, 12, 3), date(2025, 12, 2)),
        ("2025-12-01", date(2025, 12, 3), date(2025, 12, 1)),
        ("December 1st, 2025", date(2025, 12, 3), date(2025, 12, 1)),
        ("December 1, 2025", date(2025, 12, 3), date(2025, 12, 1)),
        ("in 3 days", date(2025, 12, 3), date(2025, 12, 6)),
        ("3 days ago", date(2025, 12, 3), date(2025, 11, 30)),
        ("next Tuesday", date(2025, 12, 3), date(2025, 12, 9)),
        ("last Friday", date(2025, 12, 3), date(2025, 11, 28)),
        (
            "5 days before December 1st, 2025",
            date(2025, 12, 3),
            date(2025, 11, 26),
        ),
        (
            "3 days after December 1st, 2025",
            date(2025, 12, 3),
            date(2025, 12, 4),
        ),
        (
            "2 weeks from tomorrow",
            date(2025, 12, 3),
            date(2025, 12, 18),
        ),
        (
            "1 year and 2 months after yesterday",
            date(2025, 12, 3),
            date(2027, 2, 2),
        ),
        (
            "February 29th, 2024",
            date(2025, 12, 3),
            date(2024, 2, 29),
        ),
    ],
)
def test_parse_valid_dates(text, today, expected):
    assert parse(text, today=today) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "not a date",
        "February 30, 2025",
    ],
)
def test_parse_invalid_dates(text):
    with pytest.raises(ValueError):
        parse(text, today=date(2025, 12, 3))
