from __future__ import annotations

import re
from typing import Any

from scraper.http import get_json
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text, first_sentence
from scraper.utils.events import build_event, make_artists

UNDER_K_EVENTS_URL = "https://aegwebprod.blob.core.windows.net/json/events/360/events.json"
UNDER_K_INFO_URL = "https://underthekbridge.org/events/detail/?event_id={event_id}"


def _split_support(value: str | None) -> list[str]:
    support = clean_text(value)
    if not support:
        return []
    return [part.strip() for part in re.split(r",\s*|\s+\+\s+", support) if part.strip()]


def _image_url(media: Any) -> str | None:
    if isinstance(media, dict):
        images = list(media.values())
    elif isinstance(media, list):
        images = media
    else:
        return None

    usable = [
        image
        for image in images
        if isinstance(image, dict) and image.get("file_name")
    ]
    preferred = next((image for image in usable if int(image.get("width") or 0) == 678), None)
    if preferred:
        return preferred["file_name"]
    if not usable:
        return None
    largest = max(
        usable,
        key=lambda image: int(image.get("width") or 0) * int(image.get("height") or 0),
    )
    return largest["file_name"]


def _price(raw: dict[str, Any]) -> str | None:
    values = []
    for key in ("ticketPriceLow", "ticketPriceHigh"):
        value = clean_text(str(raw.get(key) or ""))
        if value and value not in {"$0", "$0.00", "0"} and value not in values:
            values.append(value)
    if not values:
        return None
    return " - ".join(values)


def transform_aeg_event(
    raw: dict[str, Any],
    venue_name: str,
    *,
    info_url_template: str | None = None,
) -> dict[str, Any] | None:
    if raw.get("active") is False or raw.get("private") is True:
        return None
    if raw.get("publishStatus") not in (None, 1):
        return None

    title_data = raw.get("title") if isinstance(raw.get("title"), dict) else {}
    headliner = clean_text(
        title_data.get("headlinersText") or title_data.get("eventTitleText")
    )
    support = _split_support(title_data.get("supportingText"))
    artists = make_artists([headliner, *support])

    ticketing = raw.get("ticketing") if isinstance(raw.get("ticketing"), dict) else {}
    ticket_url = (
        ticketing.get("url")
        or ticketing.get("eventUrl")
        or ticketing.get("ticketURL")
    )
    event_id = raw.get("eventId")
    info_url = (
        info_url_template.format(event_id=event_id)
        if info_url_template and event_id
        else ticket_url
    )
    start = raw.get("eventDateTimeISO") or raw.get("eventDateTime")
    timezone = raw.get("eventDateTimeZone") or "America/New_York"

    return build_event(
        venue=venue_name,
        date=event_date(start, timezone),
        doors_time=event_time(raw.get("doorDateTime"), timezone),
        show_time=event_time(start, timezone),
        artists=artists,
        ticket_url=ticket_url or info_url,
        info_url=info_url,
        image_url=_image_url(raw.get("media")),
        description=first_sentence(raw.get("description") or raw.get("bio"), 320),
        price=_price(raw),
        category="concerts",
    )


def scrape_aeg_venue(
    url: str,
    venue_name: str,
    *,
    info_url_template: str | None = None,
) -> list[dict[str, Any]]:
    payload = get_json(url)
    rows = payload.get("events") if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return []

    events = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        event = transform_aeg_event(
            raw,
            venue_name,
            info_url_template=info_url_template,
        )
        if event:
            events.append(event)
    return events


def scrape_under_the_k_bridge() -> list[dict[str, Any]]:
    return scrape_aeg_venue(
        UNDER_K_EVENTS_URL,
        "Under the K Bridge",
        info_url_template=UNDER_K_INFO_URL,
    )
