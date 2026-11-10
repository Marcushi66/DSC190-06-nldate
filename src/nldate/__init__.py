"""Parse common natural-language dates using the Python standard library."""

import calendar
import re
from datetime import date, timedelta

_MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
_MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})

_WEEKDAYS = {name.lower(): i for i, name in enumerate(calendar.day_name)}
_WEEKDAYS.update({name.lower(): i for i, name in enumerate(calendar.day_abbr)})

_NUMBERS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}

_COUNT = (
    r"(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|"
    r"ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    r"seventeen|eighteen|nineteen|twenty)"
)

_UNIT = r"(?:days?|weeks?|months?|years?)"
_PART = re.compile(rf"({_COUNT})\s+({_UNIT})")


def _amounts(description: str) -> list[tuple[int, str]]:
    """Read a duration like '1 year and two months'."""
    parts = re.split(r"\s+and\s+|\s*,\s*", description)
    amounts: list[tuple[int, str]] = []

    for part in parts:
        match = _PART.fullmatch(part)

        if not match:
            raise ValueError(f"Unsupported duration: {description!r}")

        quantity = match[1]
        value = int(quantity) if quantity.isdigit() else _NUMBERS[quantity]
        amounts.append((value, match[2].rstrip("s")))

    return amounts


def _move(start: date, amounts: list[tuple[int, str]], sign: int) -> date:
    """Apply calendar years/months and timedeltas to a date."""
    result = start

    for amount, unit in amounts:
        if unit in {"year", "month"}:
            delta_months = amount * (12 if unit == "year" else 1) * sign
            month_index = result.year * 12 + result.month - 1 + delta_months

            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1

            if not (1 <= year <= 9999):
                raise ValueError("Date out of range")

            day = min(result.day, calendar.monthrange(year, month)[1])
            result = date(year, month, day)

        else:
            days = amount * (7 if unit == "week" else 1) * sign

            try:
                result += timedelta(days=days)
            except OverflowError as exc:
                raise ValueError("Date out of range") from exc

    return result


def parse(s: str, today: date | None = None) -> date:
    """Convert a recognized English date expression to a date."""
    reference = today if today is not None else date.today()

    text = " ".join(s.strip().lower().split())
    text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", text)

    if not text:
        raise ValueError("Empty date expression")

    # Day after tomorrow / day before yesterday
    if text in {"the day after tomorrow", "day after tomorrow"}:
        return reference + timedelta(days=2)

    if text in {"the day before yesterday", "day before yesterday"}:
        return reference - timedelta(days=2)

    # Current date
    if text == "now":
        return reference

    # Basic relative dates
    if text in {"today", "tomorrow", "yesterday"}:
        offsets = {
            "today": 0,
            "tomorrow": 1,
            "yesterday": -1,
        }
        return reference + timedelta(days=offsets[text])

    # ISO dates: YYYY-MM-DD
    match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)

    # Year-first slash dates: YYYY/MM/DD
    match = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)

    # US numeric dates: MM/DD/YYYY
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match:
        month, day, year = map(int, match.groups())
        return date(year, month, day)

    # Month-first dates
    match = re.fullmatch(r"([a-z]+)\s+(\d{1,2})(?:,?\s+(\d{4}))?", text)

    if match and match[1] in _MONTHS:
        year = int(match[3]) if match[3] else reference.year
        return date(year, _MONTHS[match[1]], int(match[2]))

    # Day-first dates
    match = re.fullmatch(r"(\d{1,2})\s+([a-z]+)(?:\s+(\d{4}))?", text)

    if match and match[2] in _MONTHS:
        year = int(match[3]) if match[3] else reference.year
        return date(year, _MONTHS[match[2]], int(match[1]))

    # Relative weekdays
    match = re.fullmatch(r"(next|last|this)\s+([a-z]+)", text)

    if match and match[2] in _WEEKDAYS:
        target = _WEEKDAYS[match[2]]

        if match[1] == "this":
            offset = target - reference.weekday()

        elif match[1] == "next":
            offset = (target - reference.weekday()) % 7 or 7

        else:
            offset = -((reference.weekday() - target) % 7 or 7)

        return reference + timedelta(days=offset)

    # Next/last day, week, month, or year
    match = re.fullmatch(r"(next|last)\s+(day|week|month|year)", text)

    if match:
        sign = 1 if match[1] == "next" else -1
        return _move(reference, [(1, match[2])], sign)

    # Durations before or after another date
    match = re.fullmatch(r"(.+?)\s+(before|after|from)\s+(.+)", text)

    if match:
        amounts = _amounts(match[1])
        anchor = parse(match[3], today=reference)
        sign = -1 if match[2] == "before" else 1

        return _move(anchor, amounts, sign)

    # Future dates
    match = re.fullmatch(r"in\s+(.+)", text)

    if match:
        return _move(reference, _amounts(match[1]), 1)

    # Past dates and dates from now
    match = re.fullmatch(r"(.+?)\s+(ago|from now)", text)

    if match:
        sign = -1 if match[2] == "ago" else 1
        return _move(reference, _amounts(match[1]), sign)

    # Unsupported input
    raise ValueError(f"Unrecognized date expression: {s!r}")
