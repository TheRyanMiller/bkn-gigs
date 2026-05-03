from __future__ import annotations

from datetime import date, datetime

from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

UNION_HALL_URL = "https://unionhallny.com/"


def _event_date(item) -> str | None:
    time_node = item.select_one("time[datetime], [datetime]")
    if time_node:
        return event_date(time_node.get("datetime"))

    month_node = item.select_one(".eventColl-month")
    day_node = item.select_one(".eventColl-date")
    if not month_node or not day_node:
        return None
    month_text = clean_text(month_node.get_text(" ", strip=True))
    day_text = clean_text(day_node.get_text(" ", strip=True))
    if not month_text or not day_text:
        return None

    current = date.today()
    parsed = datetime.strptime(f"{month_text} {day_text} {current.year}", "%b %d %Y").date()
    if parsed < current:
        parsed = parsed.replace(year=parsed.year + 1)
    return parsed.isoformat()


def scrape_union_hall() -> list[dict]:
    session = make_session()
    soup = BeautifulSoup(get_text(UNION_HALL_URL, session=session), "html.parser")
    items = soup.select(".eventColl-item, .event-list-item, article")
    events: list[dict] = []
    seen: set[str] = set()
    for item in items:
        title_node = item.select_one(".eventColl-title a, .event-title a, h2 a, h3 a, a[href*='eventbrite']")
        date = _event_date(item)
        if not date or not title_node:
            continue
        title = clean_text(title_node.get_text(" ", strip=True))
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
            date=date,
            doors_time=None,
            show_time=None,
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
