from __future__ import annotations

from typing import Any

from scraper.utils.dates import now_iso
from scraper.utils.events import event_identity, slugify


def assign_slugs(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for event in events:
        base = slugify(event_identity(event))
        count = counts.get(base, 0)
        counts[base] = count + 1
        event["slug"] = base if count == 0 else f"{base}-{count + 1}"
    return events


def merge_seen_cache(
    events: list[dict[str, Any]],
    seen_cache: dict[str, dict[str, str]] | None,
    *,
    scraped_at: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    cache = dict(seen_cache or {})
    timestamp = scraped_at or now_iso()
    assign_slugs(events)

    for event in events:
        slug = event["slug"]
        record = dict(cache.get(slug) or {})
        first_seen = record.get("first_seen") or timestamp
        record["first_seen"] = first_seen
        record["last_seen"] = timestamp
        cache[slug] = record
        event["first_seen"] = first_seen
        event["last_seen"] = timestamp
        event["is_new"] = first_seen == timestamp

    return events, cache


def sort_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(events, key=lambda event: (event.get("date") or "", event.get("show_time") or event.get("doors_time") or "99:99", event.get("venue") or ""))

