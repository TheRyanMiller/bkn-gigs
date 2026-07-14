from __future__ import annotations

from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text
from scraper.utils.events import absolute_url, build_event, make_artists

PUBLIC_BASE_URL = "https://www.bowerypresents.com"
SOURCE_BASE_URL = "https://origin.bowerypresents.com"


def _text(node) -> str | None:
    return clean_text(node.get_text(" ", strip=True)) if node else None


def _first_attr(node, *attrs: str) -> str | None:
    if not node:
        return None
    for attr in attrs:
        value = node.get(attr)
        if value:
            return str(value)
    return None


def _parse_items(html: str, venue_name: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".show-item, article.event, li.event, .event-listing")
    if not items:
        items = soup.select("[data-start], [itemtype*='MusicEvent']")

    events: list[dict] = []
    for item in items:
        title_node = item.select_one("[itemprop='name'], .show-title, .event-title, h3, h2")
        title = _text(title_node)
        if not title:
            continue

        start_node = item.select_one("[data-start], time[datetime], [itemprop='startDate']")
        start_value = _first_attr(start_node, "data-start", "datetime", "content")
        date = event_date(start_value)
        show_time = event_time(start_value)

        ticket_node = item.select_one("a[href*='axs.com'], a[href*='ticket'], a.button, a.btn")
        info_node = item.select_one("a[href*='/events/'], a[href*='/shows/']")
        ticket_url = absolute_url(_first_attr(ticket_node, "href"), PUBLIC_BASE_URL)
        info_url = absolute_url(_first_attr(info_node, "href"), PUBLIC_BASE_URL) or ticket_url

        support_text = _text(item.select_one(".supporting-acts, .support, .event-support"))
        support_names: list[str | None] = []
        if support_text:
            support_text = support_text.removeprefix("with ").removeprefix("With ")
            support_names = [part.strip() for part in support_text.replace(" + ", ",").split(",")]

        image_node = item.select_one("img")
        image_url = absolute_url(_first_attr(image_node, "data-src", "src"), SOURCE_BASE_URL)
        description = _text(item.select_one(".description, .event-description")) or support_text
        artists = make_artists([title, *support_names])
        category = detect_category_from_text(title, support_text, default="concerts")

        event = build_event(
            venue=venue_name,
            date=date,
            doors_time=None,
            show_time=show_time,
            artists=artists,
            ticket_url=ticket_url or info_url,
            info_url=info_url,
            image_url=image_url,
            description=description,
            price=None,
            category=category,
        )
        if event:
            events.append(event)
    return events


def scrape_bowery_venue(venue_name: str, venue_slug: str, *, max_pages: int = 12) -> list[dict]:
    session = make_session()
    page_url = f"{SOURCE_BASE_URL}/venues/{venue_slug}"
    events = _parse_items(get_text(page_url, session=session), venue_name)
    seen = {event.get("info_url") or event.get("ticket_url") for event in events}

    for page in range(1, max_pages + 1):
        url = f"{SOURCE_BASE_URL}/info/events/get"
        response = session.get(
            url,
            params={"scope": "announced", "page": page, "rows": 10, "venues": venue_slug},
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "text/html,*/*"},
            timeout=25,
        )
        response.raise_for_status()
        chunk = response.text
        if not chunk.strip():
            break
        parsed = _parse_items(chunk, venue_name)
        if not parsed:
            break
        new_count = 0
        for event in parsed:
            key = event.get("info_url") or event.get("ticket_url")
            if key in seen:
                continue
            events.append(event)
            seen.add(key)
            new_count += 1
        if new_count == 0:
            break

    return events
