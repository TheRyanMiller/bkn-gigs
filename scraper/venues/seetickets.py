from __future__ import annotations

from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

SONGKICK_BASE_URL = "https://www.songkick.com"
BABYS_CALENDAR_URL = f"{SONGKICK_BASE_URL}/venues/2445014-babys-all-right/calendar"


def _parse_songkick_page(html: str) -> tuple[list[dict], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict] = []

    for item in soup.select("#event-listings li"):
        time_node = item.select_one("time[datetime]")
        info_node = item.select_one(".artists.summary a[href*='/concerts/']")
        if not time_node or not info_node:
            continue

        start = time_node.get("datetime")
        info_url = absolute_url(info_node.get("href"), SONGKICK_BASE_URL)
        artist_names = [clean_text(node.get_text(" ", strip=True)) for node in item.select(".artists.summary strong")]
        if not artist_names:
            artist_names = [clean_text(info_node.get_text(" ", strip=True))]

        image_node = item.select_one("img")
        image_url = absolute_url(image_node.get("src") if image_node else None, SONGKICK_BASE_URL)
        description = clean_text(item.select_one(".artists.summary").get_text(" ", strip=True))
        event = build_event(
            venue="Baby's All Right",
            date=event_date(start),
            doors_time=None,
            show_time=event_time(start),
            artists=make_artists(artist_names),
            ticket_url=info_url,
            info_url=info_url,
            image_url=image_url,
            description=description,
            price=None,
            category=detect_category_from_text(description, default="concerts"),
        )
        if event:
            events.append(event)

    next_node = soup.select_one("a.next_page[rel='next']") or soup.select_one("a[rel='next']")
    next_url = absolute_url(next_node.get("href"), SONGKICK_BASE_URL) if next_node else None
    return events, next_url


def scrape_babys_all_right(*, max_pages: int = 5) -> list[dict]:
    session = make_session()
    url: str | None = BABYS_CALENDAR_URL
    events: list[dict] = []
    seen: set[str] = set()

    for _ in range(max_pages):
        if not url:
            break
        page_events, url = _parse_songkick_page(get_text(url, session=session))
        for event in page_events:
            key = event["ticket_url"]
            if key not in seen:
                events.append(event)
                seen.add(key)

    return events
