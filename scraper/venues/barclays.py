from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scraper.http import get_text
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text, first_sentence
from scraper.utils.events import absolute_url, build_event, make_artists

BASE_URL = "https://www.barclayscenter.com"
CONCERTS_URL = f"{BASE_URL}/events/category/concerts"


def _text(node) -> str | None:
    return clean_text(node.get_text(" ", strip=True)) if node else None


def _parse_listing(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict[str, Any]] = []
    seen: set[tuple[str | None, str | None, str | None]] = set()

    for item in soup.select("#eventsList .entry[data-timestamp]"):
        title = _text(item.select_one(".info.clearfix h3") or item.select_one("h3"))
        if not title:
            continue

        try:
            timestamp = int(item.get("data-timestamp") or "")
        except ValueError:
            continue

        ticket_node = item.select_one(".buttons.list-only a.tickets[href], a.tickets[href]")
        info_node = item.select_one(".buttons.list-only a.more[href], a.more[href]")
        ticket_url = absolute_url(
            clean_text(ticket_node.get("href")) if ticket_node else None,
            BASE_URL,
        )
        info_url = absolute_url(
            clean_text(info_node.get("href")) if info_node else None,
            BASE_URL,
        )
        image_node = item.select_one(".thumb.grid-only img, img")
        image_url = absolute_url(
            clean_text(image_node.get("src")) if image_node else None,
            BASE_URL,
        )
        subtitle = _text(item.select_one(".info.clearfix h4") or item.select_one("h4"))
        summary = _text(item.select_one(".info-absolute .info-body"))

        event = build_event(
            venue="Barclays Center",
            date=event_date(timestamp),
            doors_time=None,
            show_time=event_time(timestamp),
            artists=make_artists([title]),
            ticket_url=ticket_url or info_url,
            info_url=info_url,
            image_url=image_url,
            description=first_sentence(summary or subtitle),
            price=None,
            category="concerts",
        )
        if not event:
            continue

        key = (event["date"], event["show_time"], event["ticket_url"])
        if key in seen:
            continue
        seen.add(key)
        events.append(event)

    return events


def scrape_barclays_center() -> list[dict[str, Any]]:
    return _parse_listing(get_text(CONCERTS_URL))
