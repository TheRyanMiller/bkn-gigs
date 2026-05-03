from __future__ import annotations

from typing import Any

from scraper.http import make_session, post_json
from scraper.utils.categories import detect_category_from_text
from scraper.utils.dates import event_date, normalize_time
from scraper.utils.events import build_event, make_artists

GRAPHQL_URL = "https://www.venuepilot.co/graphql"
QUERY = """
query PaginatedEvents($accountIds: [Int!], $startDate: String, $endDate: String, $search: String, $searchScope: String, $page: Int) {
  paginatedEvents(arguments: {accountIds: $accountIds, startDate: $startDate, endDate: $endDate, search: $search, searchScope: $searchScope, page: $page}) {
    collection {
      id
      name
      date
      doorTime
      startTime
      description
      websiteUrl
      ticketsUrl
      status
      announceImages { highlighted versions { thumb { src } cover { src } } }
      announceArtists { name spotify }
      artists { name }
      venue { name }
    }
    metadata { currentPage totalPages }
  }
}
"""


def _image_url(raw: dict[str, Any]) -> str | None:
    for image in raw.get("announceImages") or []:
        versions = image.get("versions") if isinstance(image, dict) else None
        if not isinstance(versions, dict):
            continue
        for key in ("cover", "thumb"):
            src = (versions.get(key) or {}).get("src")
            if src:
                return src
    return None


def _artists(raw: dict[str, Any]) -> list[dict[str, str | None]]:
    names: list[str | None] = []
    for key in ("announceArtists", "artists"):
        for artist in raw.get(key) or []:
            if isinstance(artist, dict):
                names.append(artist.get("name"))
    if not names:
        names.append(raw.get("name"))
    return make_artists(names)


def scrape_venuepilot_events(venue_name: str, account_id: int, *, start_date: str) -> list[dict]:
    session = make_session()
    events: list[dict] = []
    page = 1
    total_pages = 1
    while page <= total_pages:
        payload = post_json(
            GRAPHQL_URL,
            session=session,
            json={
                "operationName": "PaginatedEvents",
                "query": QUERY,
                "variables": {
                    "accountIds": [account_id],
                    "startDate": start_date,
                    "endDate": None,
                    "search": "",
                    "searchScope": "",
                    "page": page,
                },
            },
            headers={"Accept": "application/json"},
        )
        data = (((payload or {}).get("data") or {}).get("paginatedEvents") or {})
        raw_events = data.get("collection") or []
        metadata = data.get("metadata") or {}
        total_pages = int(metadata.get("totalPages") or page)

        for raw in raw_events:
            title = raw.get("name")
            venue = ((raw.get("venue") or {}).get("name")) or venue_name
            text = " ".join(str(part) for part in (title, raw.get("description")) if part)
            event = build_event(
                venue=venue_name if venue_name.lower() in venue.lower() else venue_name,
                date=event_date(raw.get("date")),
                doors_time=normalize_time(raw.get("doorTime")),
                show_time=normalize_time(raw.get("startTime")),
                artists=_artists(raw),
                ticket_url=raw.get("ticketsUrl") or raw.get("websiteUrl"),
                info_url=raw.get("websiteUrl") or raw.get("ticketsUrl"),
                image_url=_image_url(raw),
                description=raw.get("description"),
                price=None,
                category=detect_category_from_text(text, default="concerts"),
            )
            if event:
                events.append(event)

        page += 1
    return events

