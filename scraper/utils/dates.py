from __future__ import annotations

import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from dateutil import parser

from scraper.config import LOCAL_TIMEZONE

LOCAL_TZ = ZoneInfo(LOCAL_TIMEZONE)


def today_local() -> date:
    return datetime.now(LOCAL_TZ).date()


def now_iso() -> str:
    return datetime.now(LOCAL_TZ).replace(microsecond=0).isoformat()


def parse_datetime(value: str | int | float | None, timezone: str | None = None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 10_000_000_000:
            raw = raw / 1000
        return datetime.fromtimestamp(raw, LOCAL_TZ)

    text = str(value).strip()
    if not text:
        return None
    parsed = parser.parse(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(timezone or LOCAL_TIMEZONE))
    return parsed.astimezone(LOCAL_TZ)


def event_date(value: str | int | float | None, timezone: str | None = None) -> str | None:
    parsed = parse_datetime(value, timezone)
    return parsed.date().isoformat() if parsed else None


def event_time(value: str | int | float | None, timezone: str | None = None) -> str | None:
    parsed = parse_datetime(value, timezone)
    return parsed.strftime("%H:%M") if parsed else None


def normalize_time(value: str | None, timezone: str | None = None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None

    match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)?\b", text, re.I)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    suffix = (match.group(3) or "").lower().replace(".", "")
    if suffix == "pm" and hour != 12:
        hour += 12
    elif suffix == "am" and hour == 12:
        hour = 0

    if hour > 23 or minute > 59:
        return None
    return time(hour, minute).strftime("%H:%M")


def combine_date_time(day: str | date, time_value: str | None, timezone: str | None = None) -> datetime | None:
    if not time_value:
        return parse_datetime(day.isoformat() if isinstance(day, date) else day, timezone)
    parsed_time = normalize_time(time_value)
    if not parsed_time:
        return parse_datetime(day.isoformat() if isinstance(day, date) else day, timezone)
    day_value = day if isinstance(day, date) else date.fromisoformat(day)
    hour, minute = [int(part) for part in parsed_time.split(":")]
    return datetime(day_value.year, day_value.month, day_value.day, hour, minute, tzinfo=ZoneInfo(timezone or LOCAL_TIMEZONE)).astimezone(LOCAL_TZ)

