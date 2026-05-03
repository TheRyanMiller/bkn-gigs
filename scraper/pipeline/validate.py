from __future__ import annotations

import re
from typing import Any

from scraper.config import CATEGORIES

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
REQUIRED_FIELDS = {"venue", "date", "artists", "ticket_url", "category"}


def validate_event(event: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not event.get(field):
            errors.append(f"missing {field}")

    if event.get("date") and not DATE_RE.match(str(event["date"])):
        errors.append("date must be YYYY-MM-DD")

    for field in ("doors_time", "show_time"):
        value = event.get(field)
        if value is not None and not TIME_RE.match(str(value)):
            errors.append(f"{field} must be HH:MM or null")

    if event.get("category") and event["category"] not in CATEGORIES:
        errors.append(f"invalid category {event['category']!r}")

    artists = event.get("artists")
    if not isinstance(artists, list) or not artists:
        errors.append("artists must be a non-empty list")
    else:
        for index, artist in enumerate(artists):
            if not isinstance(artist, dict) or not artist.get("name"):
                errors.append(f"artists[{index}] missing name")
            for key in ("genre", "spotify_url"):
                if isinstance(artist, dict) and key not in artist:
                    errors.append(f"artists[{index}] missing {key}")

    return errors


def validate_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[str] = []
    for index, event in enumerate(events):
        errors = validate_event(event)
        if errors:
            failures.append(f"event {index} ({event.get('venue', 'unknown')}): {', '.join(errors)}")
    if failures:
        raise ValueError("Invalid events:\n" + "\n".join(failures[:25]))
    return events

