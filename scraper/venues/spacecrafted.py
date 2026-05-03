from __future__ import annotations

from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

UNION_HALL_URL = "https://unionhallny.com/"


def scrape_union_hall() -> list[dict]:
    session = make_session()
    soup = BeautifulSoup(get_text(UNION_HALL_URL, session=session), "html.parser")
    items = soup.select(".eventColl-item, .event-list-item, article")
    events: list[dict] = []
    seen: set[str] = set()
    for item in items:
        time_node = item.select_one("time[datetime]")
        title_node = item.select_one(".eventColl-title a, .event-title a, h2 a, h3 a, a[href*='eventbrite']")
        if not time_node or not title_node:
            continue
        title = clean_text(title_node.get_text(" ", strip=True))
        start = time_node.get("datetime")
        buy_node = item.select_one("a[href*='eventbrite'], a[href*='tickets']")
        ticket_url = absolute_url((buy_node or title_node).get("href"), UNION_HALL_URL)
        if not title or not ticket_url or ticket_url in seen:
            continue
        seen.add(ticket_url)
        image_node = item.select_one("img")
        image_url = absolute_url((image_node.get("data-src") or image_node.get("src")) if image_node else None, UNION_HALL_URL)
        text = clean_text(item.get_text(" ", strip=True)) or title
        event = build_event(
            venue="Union Hall",
            date=event_date(start),
            doors_time=None,
            show_time=event_time(start),
            artists=make_artists([title]),
            ticket_url=ticket_url,
            info_url=absolute_url(title_node.get("href"), UNION_HALL_URL),
            image_url=image_url,
            description=text,
            price=None,
            category=detect_category_from_text(title, text, default="comedy"),
        )
        if event:
            events.append(event)
    return events

