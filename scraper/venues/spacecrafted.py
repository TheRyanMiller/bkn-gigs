from __future__ import annotations

from typing import Any

from scraper.http import get_json, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time
from scraper.utils.events import build_event, make_artists

EVENTS_URL = "https://www.eventbrite.com/organizer-profile/api/organizers/17899496497/events/"
PAGE_SIZE = 50


def _eventbrite_event(raw: dict[str, Any]) -> dict | None:
    if raw.get("is_cancelled") or raw.get("is_online_event"):
        return None

    title = raw.get("name")
    ticket_url = raw.get("url")
    start_date = raw.get("start_date")
    start_time = raw.get("start_time")
    timezone = raw.get("timezone")
    start = f"{start_date}T{start_time}" if start_date and start_time else start_date
    description = raw.get("summary")

    image = raw.get("image") or {}
    availability = raw.get("ticket_availability") or {}
    minimum_price = availability.get("minimum_ticket_price") or {}
    price_value = minimum_price.get("major_value")
    price = "Free" if availability.get("is_free") else f"From ${price_value}" if price_value else None

    return build_event(
        venue="Union Hall",
        date=event_date(start, timezone),
        doors_time=None,
        show_time=event_time(start, timezone),
        artists=make_artists([title]),
        ticket_url=ticket_url,
        info_url=ticket_url,
        image_url=image.get("url"),
        description=description,
        price=price,
        category=detect_category_from_text(title, description, default="comedy"),
    )


def scrape_union_hall(*, max_pages: int = 10) -> list[dict]:
    session = make_session()
    events: list[dict] = []

    for page in range(1, max_pages + 1):
        payload = get_json(
            EVENTS_URL,
            session=session,
            params={"page": page, "pageSize": PAGE_SIZE},
            headers={"Accept": "application/json"},
        )
        raw_events = payload.get("events") if isinstance(payload, dict) else []
        for raw in raw_events or []:
            if isinstance(raw, dict):
                event = _eventbrite_event(raw)
                if event:
                    events.append(event)
        if not payload.get("hasMore"):
            break

    return events
