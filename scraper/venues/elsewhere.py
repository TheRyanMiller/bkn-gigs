from __future__ import annotations

import json
from typing import Any

from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time, normalize_time
from scraper.utils.events import build_event, make_artists

BASE_URL = "https://www.elsewhere.club"


def _initial_data(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.select_one("#__NEXT_DATA__")
    if not script or not script.string:
        return {}
    return json.loads(script.string)


def _events_from_payload(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    page_props = (((payload.get("props") or {}).get("pageProps") or {}))
    data = page_props.get("initialEventData") or page_props.get("events") or {}
    if isinstance(data, list):
        return data, False
    return data.get("events") or [], bool(data.get("hasNextPage"))


def _artists(raw: dict[str, Any]) -> list[dict[str, str | None]]:
    names: list[str | None] = []
    for artist in raw.get("artists") or []:
        if isinstance(artist, dict):
            names.append(artist.get("name"))
        elif isinstance(artist, str):
            names.append(artist)
    if not names:
        names.append(raw.get("name"))
    genres = raw.get("genres") or []
    genre = genres[0].get("name") if genres and isinstance(genres[0], dict) else (genres[0] if genres else None)
    return make_artists(names, genre=genre)


def _image_url(raw: dict[str, Any]) -> str | None:
    images = raw.get("image_urls") or raw.get("images") or []
    if isinstance(images, dict):
        for value in images.values():
            if isinstance(value, str):
                return value
    if isinstance(images, list):
        for image in images:
            if isinstance(image, str):
                return image
            if isinstance(image, dict) and image.get("url"):
                return image["url"]
    return None


def _time(value: Any, timezone: str | None = None) -> str | None:
    if not value:
        return None
    text = str(value)
    if "T" in text or "-" in text:
        return event_time(text, timezone)
    return normalize_time(text)


def scrape_elsewhere() -> list[dict]:
    session = make_session()
    events: list[dict] = []
    page = 1
    while True:
        html = get_text(f"{BASE_URL}/events", session=session, headers={"Accept": "text/html"}, timeout=30) if page == 1 else get_text(f"{BASE_URL}/events?page={page}", session=session)
        raw_events, has_next_page = _events_from_payload(_initial_data(html))
        for raw in raw_events:
            if not isinstance(raw, dict):
                continue
            start = raw.get("start_date") or raw.get("starts_at") or raw.get("date")
            timezone = raw.get("timezone")
            text = " ".join(str(part) for part in (raw.get("name"), raw.get("description"), raw.get("type")) if part)
            event = build_event(
                venue="Elsewhere",
                date=event_date(start, timezone),
                doors_time=_time(raw.get("door_time"), timezone),
                show_time=_time(start, timezone),
                artists=_artists(raw),
                ticket_url=raw.get("ticket_url") or raw.get("url"),
                info_url=(f"{BASE_URL}/events/{raw.get('slug')}" if raw.get("slug") else raw.get("url")),
                image_url=_image_url(raw),
                description=raw.get("description"),
                price=raw.get("representative_ticket_price"),
                category=detect_category_from_text(text, default="concerts"),
            )
            if event:
                events.append(event)
        if not has_next_page:
            break
        page += 1
    return events

