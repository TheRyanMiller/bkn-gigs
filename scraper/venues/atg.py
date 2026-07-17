from __future__ import annotations

import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from scraper.http import get_text, make_session
from scraper.utils.dates import event_date, event_time
from scraper.utils.descriptions import clean_text, first_sentence
from scraper.utils.events import absolute_url, build_event, make_artists

BASE_URL = "https://us.atgtickets.com"
KINGS_THEATRE_URL = f"{BASE_URL}/venues/kings-theatre-brooklyn/whats-on/"
DATE_RE = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}"
)
TICKET_LABEL_RE = re.compile(
    r"Buy tickets for (?P<date>.+?) at (?P<time>\d{1,2}:\d{2}\s*[AP]M)(?:\s+ET)?",
    re.I,
)


def _text(node) -> str | None:
    return clean_text(node.get_text(" ", strip=True)) if node else None


def _listing_date(paragraphs: list[str]) -> str | None:
    for value in paragraphs:
        matches = DATE_RE.findall(value)
        if matches:
            return event_date(matches[-1], "America/New_York")
    return None


def _parse_show_cards(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    shows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for card in soup.select("[data-testid='showCard']"):
        title = _text(card.select_one("h2"))
        paragraphs = [
            value
            for node in card.select("p")
            if (value := _text(node))
        ]
        genre = next((value for value in paragraphs if value.lower() == "concert"), None)
        if not title or not genre:
            continue

        support = next(
            (value for value in paragraphs if value.lower().startswith("with ")),
            None,
        )
        info_node = next(
            (
                link
                for link in card.select("a[href]")
                if "More information about" in link.get_text(" ", strip=True)
            ),
            None,
        ) or card.select_one("a[href*='/events/']")
        info_url = absolute_url(info_node.get("href") if info_node else None, BASE_URL)
        if not info_url or info_url in seen:
            continue

        image_node = card.select_one("img[src]")
        shows.append(
            {
                "title": title,
                "support": support,
                "date": _listing_date(paragraphs),
                "info_url": info_url,
                "image_url": image_node.get("src") if image_node else None,
            }
        )
        seen.add(info_url)

    return shows


def _event_schema(soup: BeautifulSoup) -> dict[str, Any]:
    for node in soup.select("script[type='application/ld+json']"):
        try:
            payload = json.loads(node.string or node.get_text())
        except (TypeError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        schema_type = payload.get("@type")
        types = schema_type if isinstance(schema_type, list) else [schema_type]
        if any(str(value or "").endswith("Event") for value in types):
            return payload
    return {}


def _lead_artist(title: str) -> str:
    patterns = (
        r"^Signals:\s+The\s+(.+?)\s+World Tour(?:\s+\d{4})?$",
        r"^(.+?)\s+Presents:\s+",
        r"^(.+?)\s*[-–—:]\s+.*\bTour\b",
    )
    for pattern in patterns:
        match = re.search(pattern, title, re.I)
        if match:
            return match.group(1).strip()
    return title


def _artists(title: str, support: str | None) -> list[dict[str, str | None]]:
    support_text = re.sub(r"^with\s+", "", support or "", flags=re.I)
    support_names = [
        part.strip()
        for part in re.split(r",\s*|\s+\+\s+", support_text)
        if part.strip()
    ]
    return make_artists([_lead_artist(title), *support_names])


def _schema_image(schema: dict[str, Any]) -> str | None:
    images = schema.get("image")
    if isinstance(images, str):
        return images
    if isinstance(images, list):
        return next((image for image in images if isinstance(image, str)), None)
    return None


def _offer_url(schema: dict[str, Any]) -> str | None:
    offers = schema.get("offers")
    if isinstance(offers, dict):
        return offers.get("url")
    if isinstance(offers, list):
        return next(
            (
                offer.get("url")
                for offer in offers
                if isinstance(offer, dict) and offer.get("url")
            ),
            None,
        )
    return None


def _ticket_performances(
    soup: BeautifulSoup,
) -> list[tuple[str, str, str]]:
    performances: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for link in soup.select("a[href*='/tickets/']"):
        ticket_url = absolute_url(link.get("href"), BASE_URL)
        label = _text(link)
        match = TICKET_LABEL_RE.search(label or "")
        if not ticket_url or not match or ticket_url in seen:
            continue
        start = f"{match.group('date')} {match.group('time')}"
        date = event_date(start, "America/New_York")
        show_time = event_time(start, "America/New_York")
        if date and show_time:
            performances.append((date, show_time, ticket_url))
            seen.add(ticket_url)
    return performances


def _parse_detail(html: str, show: dict[str, Any]) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    schema = _event_schema(soup)
    title = clean_text(schema.get("name")) or show["title"]
    artists = _artists(title, show.get("support"))
    info_url = show["info_url"]
    image_url = _schema_image(schema) or show.get("image_url")
    description = first_sentence(schema.get("description"), 320)
    events: list[dict[str, Any]] = []

    performances = _ticket_performances(soup)
    if performances:
        for date, show_time, ticket_url in performances:
            event = build_event(
                venue="Kings Theatre",
                date=date,
                doors_time=None,
                show_time=show_time,
                artists=artists,
                ticket_url=ticket_url,
                info_url=info_url,
                image_url=image_url,
                description=description,
                price=None,
                category="concerts",
            )
            if event:
                events.append(event)
        return events

    start = schema.get("startDate")
    event = build_event(
        venue="Kings Theatre",
        date=event_date(start) or show.get("date"),
        doors_time=None,
        show_time=event_time(start),
        artists=artists,
        ticket_url=_offer_url(schema) or info_url,
        info_url=info_url,
        image_url=image_url,
        description=description,
        price=None,
        category="concerts",
    )
    return [event] if event else []


def scrape_kings_theatre() -> list[dict[str, Any]]:
    session = make_session()
    shows = _parse_show_cards(get_text(KINGS_THEATRE_URL, session=session))
    events: list[dict[str, Any]] = []
    for show in shows:
        try:
            detail = get_text(show["info_url"], session=session)
        except requests.RequestException:
            detail = ""
        events.extend(_parse_detail(detail, show))
    return events
