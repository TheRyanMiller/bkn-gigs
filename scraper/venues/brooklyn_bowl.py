from __future__ import annotations

import re
from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

from scraper.http import get_text
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import normalize_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

BASE_URL = "https://www.brooklynbowl.com"
LIST_URL = f"{BASE_URL}/brooklyn/shows/all"


def _month_iter(start: date, count: int):
    year = start.year
    month = start.month
    for _ in range(count):
        yield year, month
        month += 1
        if month == 13:
            month = 1
            year += 1


def _time_from_label(value: str | None, label: str) -> str | None:
    match = re.search(rf"\b{label}\s*:\s*([^/|]+)", value or "", re.I)
    return normalize_time(match.group(1)) if match else None


def _is_excluded(title: str) -> bool:
    title_lower = title.lower()
    return (
        title_lower.startswith("closed")
        or "closed for a private event" in title_lower
        or "full venue closed" in title_lower
        or "gift card" in title_lower
    )


def _node_text(item: Tag, selector: str) -> str | None:
    node = item.select_one(selector)
    return clean_text(node.get_text(" ", strip=True)) if node else None


def _parse_listing(
    html: str,
    *,
    allowed_months: set[tuple[int, int]] | None = None,
) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict] = []
    seen: set[str] = set()

    for item in soup.select(".eventItem"):
        venue = _node_text(item, ".venue")
        if venue and venue.lower() != "brooklyn":
            continue

        title_node = item.select_one("h3.title a")
        title = clean_text(title_node.get_text(" ", strip=True)) if title_node else None
        if not title or _is_excluded(title):
            continue

        date_node = item.select_one(".date.outside[aria-label], .date[aria-label]")
        raw_date = clean_text(date_node.get("aria-label")) if date_node else None
        try:
            parsed_date = datetime.strptime(raw_date or "", "%B %d %Y").date()
        except ValueError:
            continue
        if allowed_months is not None and (parsed_date.year, parsed_date.month) not in allowed_months:
            continue

        pre_title = _node_text(item, ".pre-title-tagline")
        support = _node_text(item, ".tagline")
        description = " — ".join(part for part in (pre_title, support) if part)

        info_url = absolute_url(title_node.get("href"), BASE_URL)
        ticket_node = item.select_one(".buttons a[href]")
        ticket_url = absolute_url(ticket_node.get("href") if ticket_node else None, BASE_URL) or info_url

        image_node = item.select_one(".thumb img, img")
        image_url = absolute_url(
            (image_node.get("data-src") or image_node.get("src")) if image_node else None,
            BASE_URL,
        )
        time_text = _node_text(item, ".time")

        event = build_event(
            venue="Brooklyn Bowl",
            date=parsed_date.isoformat(),
            doors_time=_time_from_label(time_text, "Doors"),
            show_time=_time_from_label(time_text, "Show"),
            artists=make_artists([title, support]),
            ticket_url=ticket_url,
            info_url=info_url,
            image_url=image_url,
            description=description or None,
            price=None,
            category=detect_category_from_text(title, description, default="concerts"),
        )
        if not event:
            continue

        key = event.get("info_url") or f"{event['date']}:{event['artists'][0]['name']}"
        if key in seen:
            continue
        seen.add(key)
        events.append(event)

    return events


def scrape_brooklyn_bowl(*, months: int = 8) -> list[dict]:
    allowed_months = set(_month_iter(date.today(), months))
    return _parse_listing(get_text(LIST_URL), allowed_months=allowed_months)
