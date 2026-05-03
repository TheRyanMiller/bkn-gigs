from __future__ import annotations

import re
from typing import Any

from scraper.http import get_json, make_session
from scraper.utils.categories import category_from_ticketing
from scraper.utils.dates import event_date, event_time, normalize_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import build_event, make_artists

BASE_URL = "https://content.livenationapi.com/v1/venues/{venue_id}/events"
API_KEY = "AbDS2tuO3ONIZJVK5p6Q2tiPRYX34Ie9RzQ1zlIb"
DOORS_RE = re.compile(r"\bdoor(?:s)?(?:\s*time)?\s*[:\-]\s*([0-9: ]+[ap]\.?m\.?|[0-9]{1,2}:[0-9]{2})", re.I)


def _image_url(event: dict[str, Any]) -> str | None:
    images = event.get("images") or []
    if not isinstance(images, list):
        return None
    ranked = sorted(
        [image for image in images if isinstance(image, dict) and image.get("url")],
        key=lambda image: int(image.get("width") or 0) * int(image.get("height") or 0),
        reverse=True,
    )
    return ranked[0]["url"] if ranked else None


def _artists(event: dict[str, Any]) -> list[dict[str, str | None]]:
    names: list[str | None] = []
    for artist in event.get("artists") or []:
        if isinstance(artist, dict):
            names.append(artist.get("name"))
        elif isinstance(artist, str):
            names.append(artist)
    if not names:
        names.append(event.get("name"))
    return make_artists(names, genre=event.get("genre"))


def _doors_time(event: dict[str, Any]) -> str | None:
    info = clean_text(event.get("important_info"))
    if not info:
        return None
    match = DOORS_RE.search(info)
    return normalize_time(match.group(1)) if match else None


def scrape_live_nation_venue(venue_name: str, venue_id: str, *, limit: int = 100) -> list[dict]:
    session = make_session()
    events: list[dict] = []
    offset = 0
    while True:
        payload = get_json(
            BASE_URL.format(venue_id=venue_id),
            session=session,
            params={"offset": offset, "limit": limit},
            headers={"x-api-key": API_KEY, "Accept": "application/json"},
        )
        raw_events = payload.get("events") if isinstance(payload, dict) else payload
        if not isinstance(raw_events, list) or not raw_events:
            break

        for raw in raw_events:
            if not isinstance(raw, dict):
                continue
            start = raw.get("start_date_local") or raw.get("startDate") or raw.get("date")
            timezone = raw.get("timezone")
            name = raw.get("name")
            description = raw.get("important_info") or raw.get("description")
            category = category_from_ticketing(raw.get("segment"), raw.get("genre"), name, default="concerts")
            event = build_event(
                venue=venue_name,
                date=event_date(start, timezone),
                doors_time=_doors_time(raw),
                show_time=event_time(raw.get("start_time_local") or start, timezone),
                artists=_artists(raw),
                ticket_url=raw.get("url"),
                info_url=raw.get("url"),
                image_url=_image_url(raw),
                description=description,
                price=None,
                category=category,
            )
            if event:
                events.append(event)

        if len(raw_events) < limit:
            break
        offset += limit
    return events

