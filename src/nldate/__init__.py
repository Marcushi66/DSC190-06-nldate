"""Convert common English date expressions into ``datetime.date`` values.

The parser uses deterministic rules rather than an online service. When an input
is ambiguous or unsupported it raises ValueError instead of guessing.
"""

import calendar
import re
from datetime import date, timedelta

_MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
_MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})
_WEEKDAYS = {name.lower(): i for i, name in enumerate(calendar.day_name)}
_WEEKDAYS.update({name.lower(): i for i, name in enumerate(calendar.day_abbr)})

_SMALL = {
    "zero": 0,
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
}
_TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
_WORD_NUMBER = (
    r"(?:zero|a|an|one|two|three|four|five|six|seven|eight|nine|"
    r"ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|"
    r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
    r"(?:[ -](?:one|two|three|four|five|six|seven|eight|nine))?)"
)
_COUNT = rf"(?:\d+|{_WORD_NUMBER})"
_UNIT = r"(?:days?|weeks?|months?|years?)"
_PART = re.compile(rf"(?P<count>{_COUNT})\s+(?P<unit>{_UNIT})\b")
_ORDINAL = re.compile(r"\b(\d+)(?:st|nd|rd|th)\b")
_MONTH_ABBR_PERIOD = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\.\s*"
)


def _number(raw: str) -> int:
    """Convert a short English number or digits to an integer."""
    if raw.isdigit():
        return int(raw)
    words = raw.replace("-", " ").split()
    if len(words) == 1:
        if words[0] in _SMALL:
            return _SMALL[words[0]]
        return _TENS[words[0]]
    return _TENS[words[0]] + _SMALL[words[1]]


def _amounts(description: str) -> list[tuple[int, str]]:
    """Parse durations, such as '2 weeks and three days'."""
    amounts: list[tuple[int, str]] = []
    cursor = 0
    for match in _PART.finditer(description):
        between = description[cursor : match.start()]
        if cursor == 0:
            if between.strip():
                raise ValueError(f"Unsupported duration: {description!r}")
        elif not re.fullmatch(r"\s*(?:,|and)?\s+|\s*,\s*", between):
            raise ValueError(f"Unsupported duration: {description!r}")
        amounts.append((_number(match["count"]), match["unit"].rstrip("s")))
        cursor = match.end()
    if not amounts or description[cursor:].strip():
        raise ValueError(f"Unsupported duration: {description!r}")
    return amounts


def _shift_day(base: date, days: int) -> date:
    try:
        return base + timedelta(days=days)
    except (ValueError, OverflowError) as exc:
        raise ValueError("Date out of range") from exc


def _move(start: date, amounts: list[tuple[int, str]], sign: int) -> date:
    """Shift by calendar months/years (clamping month-ends) or exact days."""
    result = start
    for amount, unit in amounts:
        if unit in {"year", "month"}:
            change = amount * (12 if unit == "year" else 1) * sign
            year, month_index = divmod(result.year * 12 + result.month - 1 + change, 12)
            if year < 1 or year > 9999:
                raise ValueError("Date out of range")
            month = month_index + 1
            day = min(result.day, calendar.monthrange(year, month)[1])
            result = date(year, month, day)
        else:
            days = amount * (7 if unit == "week" else 1) * sign
            result = _shift_day(result, days)
    return result


def _named_date(text: str, reference: date) -> date | None:
    """Handle full or abbreviated month names in either order."""
    # December 1, 2025; Dec. 1st, 2025; December 1
    match = re.fullmatch(r"([a-z]+)\s+(\d{1,2})(?:,?\s*(\d{4}))?", text)
    if match and match[1] in _MONTHS:
        year = int(match[3]) if match[3] else reference.year
        return date(year, _MONTHS[match[1]], int(match[2]))

    # 1 December 2025; 1st of Dec. 2025
    match = re.fullmatch(
        r"(?:the\s+)?(\d{1,2})\s+(?:of\s+)?([a-z]+)(?:,?\s*(\d{4}))?", text
    )
    if match and match[2] in _MONTHS:
        year = int(match[3]) if match[3] else reference.year
        return date(year, _MONTHS[match[2]], int(match[1]))
    return None


def _calendar_phrase(text: str, reference: date) -> date | None:
    """Recognize simple month boundaries and day/month/weekday combinations."""
    match = re.fullmatch(r"(?:the\s+)?(?:first|last)\s+day\s+of\s+(.+)", text)
    if match:
        anchor_text = match[1]
        month = re.fullmatch(r"([a-z]+)(?:\s+(\d{4}))?", anchor_text)
        if month and month[1] in _MONTHS:
            year = int(month[2]) if month[2] else reference.year
            month_num = _MONTHS[month[1]]
            day = (
                1
                if "first" in text.split()
                else calendar.monthrange(year, month_num)[1]
            )
            return date(year, month_num, day)

    match = re.fullmatch(
        r"(?:the\s+)?(start|beginning|end)\s+of\s+(this|next|last)\s+month", text
    )
    if match:
        offset = {"this": 0, "next": 1, "last": -1}[match[2]]
        shifted = _move(reference, [(abs(offset), "month")], 1 if offset >= 0 else -1)
        day = (
            1
            if match[1] in {"start", "beginning"}
            else calendar.monthrange(shifted.year, shifted.month)[1]
        )
        return date(shifted.year, shifted.month, day)
    return None


def parse(s: str, today: date | None = None) -> date:
    """Return the date referred to by a supported natural-language expression.

    ``today`` provides the reference date for relative expressions. Without it,
    the machine's current local date is used. Unrecognized inputs raise ValueError.
    """
    reference = today if today is not None else date.today()
    text = " ".join(s.strip().lower().split())
    if not text:
        raise ValueError("Empty date expression")

    text = _ORDINAL.sub(r"\1", text)
    text = _MONTH_ABBR_PERIOD.sub(r"\1 ", text)
    text = text.replace("sept ", "sep ")
    text = re.sub(r",\s*", ", ", text)
    text = " ".join(text.split())
    text = re.sub(r"^(?:on)\s+", "", text)

    keywords = {
        "today": 0,
        "now": 0,
        "tomorrow": 1,
        "yesterday": -1,
        "the day after tomorrow": 2,
        "day after tomorrow": 2,
        "the day before yesterday": -2,
        "day before yesterday": -2,
    }
    if text in keywords:
        return _shift_day(reference, keywords[text])

    # ISO, slash, and dot year-first dates; strictly validate calendar days.
    match = re.fullmatch(r"(\d{4})([-/.])(\d{1,2})\2(\d{1,2})", text)
    if match:
        return date(int(match[1]), int(match[3]), int(match[4]))

    # US month-first numeric dates, e.g. 12/04/2025 or 12-04-2025.
    match = re.fullmatch(r"(\d{1,2})([-/.])(\d{1,2})\2(\d{4})", text)
    if match:
        return date(int(match[4]), int(match[1]), int(match[3]))

    # Optional weekday prefix before an absolute date.
    match = re.fullmatch(r"([a-z]+),\s*(.+)", text)
    if match and match[1] in _WEEKDAYS:
        parsed = parse(match[2], today=reference)
        if parsed.weekday() != _WEEKDAYS[match[1]]:
            raise ValueError("Weekday does not match the date")
        return parsed

    named = _named_date(text, reference)
    if named is not None:
        return named

    month_boundary = _calendar_phrase(text, reference)
    if month_boundary is not None:
        return month_boundary

    # next Tuesday / last Friday / this Wednesday
    match = re.fullmatch(r"(next|last|previous|this|coming)\s+([a-z]+)", text)
    if match and match[2] in _WEEKDAYS:
        target = _WEEKDAYS[match[2]]
        if match[1] == "this":
            offset = target - reference.weekday()
        elif match[1] in {"next", "coming"}:
            offset = (target - reference.weekday()) % 7 or 7
        else:
            offset = -((reference.weekday() - target) % 7 or 7)
        return _shift_day(reference, offset)

    match = re.fullmatch(r"(next|last|previous)\s+(day|week|month|year)", text)
    if match:
        sign = 1 if match[1] == "next" else -1
        return _move(reference, [(1, match[2])], sign)

    # Three days before Dec. 1, 2025; two weeks from tomorrow.
    match = re.fullmatch(r"(.+?)\s+(before|after|from)\s+(.+)", text)
    if match:
        amounts = _amounts(match[1])
        anchor = parse(match[3], today=reference)
        sign = -1 if match[2] == "before" else 1
        return _move(anchor, amounts, sign)

    match = re.fullmatch(r"in\s+(.+)", text)
    if match:
        return _move(reference, _amounts(match[1]), 1)

    match = re.fullmatch(r"(.+?)\s+(ago|from now|later|earlier)", text)
    if match:
        sign = -1 if match[2] in {"ago", "earlier"} else 1
        return _move(reference, _amounts(match[1]), sign)

    raise ValueError(f"Unrecognized date expression: {s!r}")
