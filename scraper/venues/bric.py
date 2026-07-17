from __future__ import annotations

import re
from datetime import date
from typing import Any

from bs4 import BeautifulSoup

from scraper.http import get_text
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import normalize_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import build_event, make_artists

SEASON_URL = "https://bricartsmedia.org/celebrate-brooklyn/"
VENUE_NAME = "Lena Horne Bandshell"


def _text(node) -> str | None:
    return clean_text(node.get_text(" ", strip=True)) if node else None


def _season_year(soup: BeautifulSoup) -> int | None:
    text = soup.get_text(" ", strip=True)
    match = re.search(r"\b(20\d{2})\s+season\b", text, re.I)
    if not match:
        match = re.search(
            r"June\s+\d+\s*[–—-]\s*September\s+\d+,\s*(20\d{2})",
            text,
            re.I,
        )
    return int(match.group(1)) if match else None


def _artist_names(title: str) -> list[str]:
    common = re.search(r"\bpresent:\s*(Common)\s+and Special Guests\b", title, re.I)
    if common:
        return [common.group(1)]

    value = title
    if "Community Joy Day with " in value:
        value = value.split("Community Joy Day with ", 1)[1]
    elif re.search(r"\bFeaturing\b", value, re.I):
        value = re.split(r"\bFeaturing\b", value, maxsplit=1, flags=re.I)[1]
    elif "globalFEST" in value and re.search(r"\bWith\b", value):
        value = re.split(r"\bWith\b", value, maxsplit=1)[1]

    value = re.sub(r"^BRIC Celebrate Brooklyn!\s+Opening Night:\s*", "", value, flags=re.I)
    value = re.sub(
        r"^(?:Benefit Show|Family Day|Juneteenth|Americana Night|Jazz at the Bandshell):\s*",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(r"\s+\|\s+The Flannel and The Fury(?:\s+\d{4})?$", "", value, flags=re.I)
    names = [
        part.strip()
        for part in re.split(r"\s+(?:\+|&|\|)\s+", value)
        if part.strip()
    ]
    return names or [title]


def _image_url(card) -> str | None:
    image = card.select_one("img")
    if not image:
        return None
    for attr in ("alt", "nitro-lazy-src", "data-src", "src"):
        value = image.get(attr)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
    return None


def _parse_season(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    year = _season_year(soup)
    if not year:
        return []

    events: list[dict[str, Any]] = []
    seen: set[str] = set()
    for card in soup.select(".m-card-event-c"):
        location = _text(card.select_one(".m-card-event-c__location .a-meta__text"))
        if location != VENUE_NAME:
            continue

        title = _text(card.select_one(".m-card-event-c__title"))
        raw_date = _text(card.select_one(".m-card-event-c__pretitle"))
        info_node = card.select_one("a[href*='/event/']")
        info_url = info_node.get("href") if info_node else None
        if not title or not raw_date or not info_url or info_url in seen:
            continue

        try:
            month, day = [int(part) for part in raw_date.split(".", 1)]
            event_day = date(year, month, day).isoformat()
        except (TypeError, ValueError):
            continue

        time_text = _text(card.select_one(".m-card-event-c__text"))
        cost = _text(card.select_one(".m-card-event-c__cost .a-meta__text"))
        artists = make_artists(_artist_names(title))
        event = build_event(
            venue=VENUE_NAME,
            date=event_day,
            doors_time=normalize_time(time_text),
            show_time=None,
            artists=artists,
            ticket_url=info_url,
            info_url=info_url,
            image_url=_image_url(card),
            description=None,
            price="Free" if (cost or "").lower() == "free" else None,
            category=detect_category_from_text(title, default="concerts"),
        )
        if event:
            events.append(event)
            seen.add(info_url)

    return events


def scrape_bric_celebrate_brooklyn() -> list[dict[str, Any]]:
    return _parse_season(get_text(SEASON_URL))
