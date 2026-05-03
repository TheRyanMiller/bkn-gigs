from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

log = logging.getLogger(__name__)

BABYS_URL = "https://wl.eventim.us/BabysAllRightBrooklyn"


def scrape_babys_all_right() -> list[dict]:
    session = make_session()
    try:
        html = get_text(BABYS_URL, session=session, headers={"Accept": "text/html"})
    except requests.HTTPError as exc:
        log.warning("Baby's All Right See Tickets page blocked or unavailable: %s", exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("[data-event-id], .event, article, li")
    events: list[dict] = []
    seen: set[str] = set()
    for item in items:
        title_node = item.select_one("h2, h3, .event-title, a[href*='event']")
        time_node = item.select_one("time[datetime], [datetime], [data-start-date]")
        ticket_node = item.select_one("a[href*='eventim'], a[href*='ticket'], a[href]")
        title = clean_text(title_node.get_text(" ", strip=True)) if title_node else None
        start = (time_node.get("datetime") or time_node.get("data-start-date")) if time_node else None
        ticket_url = absolute_url(ticket_node.get("href") if ticket_node else None, BABYS_URL)
        if not title or not start or not ticket_url or ticket_url in seen:
            continue
        seen.add(ticket_url)
        text = clean_text(item.get_text(" ", strip=True)) or title
        image_node = item.select_one("img")
        image_url = absolute_url((image_node.get("data-src") or image_node.get("src")) if image_node else None, BABYS_URL)
        event = build_event(
            venue="Baby's All Right",
            date=event_date(start),
            doors_time=None,
            show_time=event_time(start),
            artists=make_artists([title]),
            ticket_url=ticket_url,
            info_url=ticket_url,
            image_url=image_url,
            description=text,
            price=None,
            category=detect_category_from_text(title, text, default="concerts"),
        )
        if event:
            events.append(event)
    return events

