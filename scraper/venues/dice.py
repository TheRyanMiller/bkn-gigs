from __future__ import annotations

import json
import logging
from typing import Any

import requests

from scraper.http import get_json, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time, normalize_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import build_event, make_artists, normalize_price

BASE_URL = "https://partners-endpoint.dice.fm/api/v2/events"
log = logging.getLogger(__name__)


def _params(venue_filters: list[str] | None, promoter_filters: list[str] | None, page: int) -> list[tuple[str, str]]:
    params = [("page[size]", "24"), ("page[number]", str(page)), ("types", "linkout,event")]
    for venue in venue_filters or []:
        params.append(("filter[venues][]", venue))
    for promoter in promoter_filters or []:
        params.append(("filter[promoters][]", promoter))
    return params


def _find_url(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    if isinstance(value, dict):
        for item in value.values():
            found = _find_url(item)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = _find_url(item)
            if found:
                return found
    return None


def _artists(raw: dict[str, Any]) -> list[dict[str, str | None]]:
    names: list[str | None] = []
    for key in ("detailed_artists", "artists", "lineup"):
        for artist in raw.get(key) or []:
            if isinstance(artist, dict):
                names.append(artist.get("name") or artist.get("display_name"))
            elif isinstance(artist, str):
                names.append(artist)
    if not names:
        names.append(raw.get("name"))
    genres = raw.get("genre_tags") or []
    genre = genres[0] if genres else None
    return make_artists(names, genre=genre)


def _price(raw: dict[str, Any]) -> str | None:
    amounts: list[float] = []
    for ticket in raw.get("ticket_types") or []:
        if not isinstance(ticket, dict):
            continue
        for key in ("total_price", "price", "face_value"):
            value = ticket.get(key)
            if isinstance(value, dict):
                value = value.get("amount") or value.get("total")
            if isinstance(value, (int, float)) and value > 0:
                amounts.append(value / 100 if value > 1000 else float(value))
    if not amounts:
        return normalize_price(raw.get("price"))
    lowest = min(amounts)
    return f"From ${lowest:.2f}".replace(".00", "")


def _doors_time(raw: dict[str, Any]) -> str | None:
    text = json.dumps(raw.get("lineup") or raw.get("details") or raw.get("description") or "")
    marker = "doors"
    lower = text.lower()
    if marker not in lower:
        return None
    index = lower.find(marker)
    return normalize_time(text[index : index + 80])


def _category(raw: dict[str, Any], default: str) -> str:
    tag_text = " ".join(
        str(value)
        for key in ("genre_tags", "type_tags", "tags", "name", "description", "raw_description")
        for value in ([raw.get(key)] if isinstance(raw.get(key), str) else raw.get(key) or [])
    )
    return detect_category_from_text(tag_text, default=default)


def scrape_dice_events(
    venue_name: str,
    *,
    api_key: str,
    venue_filters: list[str] | None = None,
    promoter_filters: list[str] | None = None,
    default_category: str = "concerts",
    max_pages: int = 20,
) -> list[dict]:
    session = make_session()
    headers = {"x-api-key": api_key, "Accept": "application/json"}
    events: list[dict] = []

    for page in range(1, max_pages + 1):
        try:
            payload = get_json(BASE_URL, session=session, headers=headers, params=_params(venue_filters, promoter_filters, page))
        except requests.HTTPError as exc:
            log.warning("DICE request failed for %s page %s: %s", venue_name, page, exc)
            break
        raw_events = payload.get("data") if isinstance(payload, dict) else []
        if not raw_events:
            break

        for raw in raw_events:
            if not isinstance(raw, dict):
                continue
            timezone = raw.get("timezone")
            start = raw.get("date") or raw.get("start_date") or raw.get("starts_at")
            event = build_event(
                venue=venue_name,
                date=event_date(start, timezone),
                doors_time=_doors_time(raw),
                show_time=event_time(start, timezone),
                artists=_artists(raw),
                ticket_url=raw.get("url") or raw.get("event_url"),
                info_url=raw.get("url") or raw.get("event_url"),
                image_url=_find_url(raw.get("images") or raw.get("image")),
                description=raw.get("raw_description") or raw.get("description"),
                price=_price(raw),
                category=_category(raw, default_category),
            )
            if event:
                events.append(event)

        if len(raw_events) < 24:
            break

    return events
