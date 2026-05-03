from __future__ import annotations

import re

from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time, normalize_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

LITTLEFIELD_URL = "https://littlefieldnyc.com/all-shows/"


def _label_time(text: str, label: str) -> str | None:
    match = re.search(rf"{label}\s*:\s*([0-9]{{1,2}}(?::[0-9]{{2}})?\s*[ap]\.?m\.?)", text, re.I)
    return normalize_time(match.group(1)) if match else None


def scrape_littlefield() -> list[dict]:
    session = make_session()
    soup = BeautifulSoup(get_text(LITTLEFIELD_URL, session=session), "html.parser")
    items = soup.select("article.wfea-venue__event, article, .wfea_event, .event, li")
    events: list[dict] = []
    seen: set[str] = set()
    for item in items:
        time_node = item.select_one("time[datetime]")
        title_node = item.select_one("h2 a, h3 a, .entry-title a")
        ticket_node = item.select_one("a[href*='wfea_eb_id'], a[href*='eventbrite']")
        if not time_node or not title_node:
            continue
        image_node = item.select_one("img")
        title = (
            clean_text(title_node.get_text(" ", strip=True))
            or clean_text(title_node.get("title"))
            or clean_text(image_node.get("alt") if image_node else None)
        )
        start = time_node.get("datetime")
        ticket_url = absolute_url((ticket_node or title_node).get("href"), "https://littlefieldnyc.com")
        if not title or not ticket_url or ticket_url in seen:
            continue
        seen.add(ticket_url)
        text = clean_text(item.get_text(" ", strip=True)) or ""
        image_url = absolute_url((image_node.get("data-src") or image_node.get("src")) if image_node else None, "https://littlefieldnyc.com")
        event = build_event(
            venue="Littlefield",
            date=event_date(start),
            doors_time=_label_time(text, "doors"),
            show_time=_label_time(text, "show") or event_time(start),
            artists=make_artists([title]),
            ticket_url=ticket_url,
            info_url=ticket_url,
            image_url=image_url,
            description=text,
            price=None,
            category=detect_category_from_text(title, text, default="comedy"),
        )
        if event:
            events.append(event)
    return events
