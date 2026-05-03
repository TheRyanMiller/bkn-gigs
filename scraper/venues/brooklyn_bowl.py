from __future__ import annotations

from datetime import date, datetime
from typing import Any

from bs4 import BeautifulSoup

from scraper.http import get_json, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

BASE_URL = "https://www.brooklynbowl.com"


def _month_iter(start: date, count: int):
    year = start.year
    month = start.month
    for _ in range(count):
        yield year, month
        month += 1
        if month == 13:
            month = 1
            year += 1


def _html_chunks(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, dict):
        chunks: list[str] = []
        for item in value.values():
            chunks.extend(_html_chunks(item))
        return chunks
    return []


def _parse_item(html: str, day: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    item = soup.select_one("[data-venue-uri='brooklyn']") or soup
    if item is soup and "data-venue-uri=\"brooklyn\"" not in html and "Brooklyn" not in item.get_text(" "):
        return None

    title_node = item.select_one(".event-title, .title, h3, h2, a")
    title = clean_text(title_node.get_text(" ", strip=True)) if title_node else None
    if not title:
        return None
    title_lower = title.lower()
    if (
        title_lower.startswith("closed")
        or "closed for a private event" in title_lower
        or "full venue closed" in title_lower
        or "gift card" in title_lower
    ):
        return None

    support = clean_text((item.select_one(".support, h4, .event-support") or BeautifulSoup("", "html.parser")).get_text(" ", strip=True))
    link_node = item.select_one("a[href*='/brooklyn/events/'], a[href*='/event/'], a[href]")
    info_url = absolute_url(link_node.get("href") if link_node else None, BASE_URL)
    image_node = item.select_one("img")
    image_url = absolute_url((image_node.get("data-src") or image_node.get("src")) if image_node else None, BASE_URL)
    description = support
    artists = make_artists([title, support])
    return build_event(
        venue="Brooklyn Bowl",
        date=day,
        doors_time=None,
        show_time=None,
        artists=artists,
        ticket_url=info_url,
        info_url=info_url,
        image_url=image_url,
        description=description,
        price=None,
        category=detect_category_from_text(title, support, default="concerts"),
    )


def scrape_brooklyn_bowl(*, months: int = 8) -> list[dict]:
    session = make_session()
    session.cookies.set("selectedVenue", "brooklyn", domain="www.brooklynbowl.com")
    events: list[dict] = []
    seen: set[str] = set()
    for year, month in _month_iter(date.today(), months):
        payload = get_json(
            f"{BASE_URL}/events/calendar/{year}/{month}",
            session=session,
            params={"v": "2", "detail_partial": "modules/events/partials/full_page_calendar_event_item"},
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        if not isinstance(payload, dict):
            continue
        for raw_day, raw_html in payload.items():
            try:
                day = datetime.strptime(raw_day, "%m-%d-%Y").date().isoformat()
            except ValueError:
                continue
            for chunk in _html_chunks(raw_html):
                event = _parse_item(chunk, day)
                if not event:
                    continue
                key = event.get("info_url") or f"{event['date']}:{event['artists'][0]['name']}"
                if key in seen:
                    continue
                seen.add(key)
                events.append(event)
    return events
