from __future__ import annotations

import re
from typing import Any

from scraper.http import get_json, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, normalize_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

BCC_JSON_URL = "https://www.brooklyncc.com/show-schedule?format=json-pretty"
EVENTBRITE_RE = re.compile(r"https://www\.eventbrite\.com/[^\s\"'<>]+", re.I)


def _label_time(text: str, label: str) -> str | None:
    match = re.search(rf"{label}\s*:?\s*([0-9]{{1,2}}(?::[0-9]{{2}})?\s*[ap]\.?m\.?)", text, re.I)
    return normalize_time(match.group(1)) if match else None


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            return payload["items"]
        collection = payload.get("collection")
        if isinstance(collection, dict) and isinstance(collection.get("items"), list):
            return collection["items"]
    return []


def scrape_brooklyn_comedy_collective() -> list[dict]:
    payload = get_json(BCC_JSON_URL, session=make_session(), headers={"Accept": "application/json"})
    events: list[dict] = []
    for item in _items(payload):
        if item.get("recordType") not in (None, 12):
            continue
        title = item.get("title")
        body = item.get("body") or item.get("excerpt")
        text = clean_text(body) or ""
        ticket_match = EVENTBRITE_RE.search(body or "")
        ticket_url = ticket_match.group(0) if ticket_match else absolute_url(item.get("fullUrl"), "https://www.brooklyncc.com")
        event = build_event(
            venue="Brooklyn Comedy Collective",
            date=event_date(item.get("startDate") or item.get("structuredContent", {}).get("startDate")),
            doors_time=_label_time(text, "doors"),
            show_time=_label_time(text, "show"),
            artists=make_artists([title]),
            ticket_url=ticket_url,
            info_url=absolute_url(item.get("fullUrl"), "https://www.brooklyncc.com"),
            image_url=absolute_url(item.get("assetUrl"), "https://www.brooklyncc.com"),
            description=text,
            price=None,
            category=detect_category_from_text(title, text, default="comedy"),
        )
        if event:
            events.append(event)
    return events

