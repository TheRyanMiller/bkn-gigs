from __future__ import annotations

import re
import unicodedata
from typing import Any

from scraper.utils.categories import normalize_category
from scraper.utils.descriptions import clean_text


def slugify(value: str, max_length: int = 90) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized[:max_length].strip("-") or "event"


def absolute_url(url: str | None, base: str) -> str | None:
    if not url:
        return None
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith("//"):
        return "https:" + url
    return base.rstrip("/") + "/" + url.lstrip("/")


def make_artist(name: str | None, *, genre: str | None = None, spotify_url: str | None = None) -> dict[str, str | None] | None:
    cleaned = clean_text(name)
    if not cleaned:
        return None
    return {"name": cleaned, "genre": clean_text(genre), "spotify_url": spotify_url or None}


def make_artists(names: list[str | None] | tuple[str | None, ...], *, genre: str | None = None) -> list[dict[str, str | None]]:
    artists: list[dict[str, str | None]] = []
    seen: set[str] = set()
    for name in names:
        artist = make_artist(name, genre=genre)
        if not artist:
            continue
        key = artist["name"].lower()
        if key not in seen:
            artists.append(artist)
            seen.add(key)
    return artists


def normalize_price(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return f"${value:.2f}".replace(".00", "")
    text = clean_text(str(value))
    return text or None


def build_event(
    *,
    venue: str,
    date: str | None,
    artists: list[dict[str, str | None]],
    ticket_url: str | None,
    category: str,
    doors_time: str | None = None,
    show_time: str | None = None,
    info_url: str | None = None,
    image_url: str | None = None,
    description: str | None = None,
    price: str | None = None,
) -> dict[str, Any] | None:
    if not date or not ticket_url or not artists:
        return None
    return {
        "venue": clean_text(venue) or venue,
        "date": date,
        "doors_time": doors_time,
        "show_time": show_time,
        "artists": artists,
        "ticket_url": ticket_url,
        "info_url": info_url or ticket_url,
        "image_url": image_url,
        "description": clean_text(description),
        "price": normalize_price(price),
        "category": normalize_category(category, "misc"),
    }


def event_identity(event: dict[str, Any]) -> str:
    lead = event.get("artists", [{}])[0].get("name", "event")
    show_time = event.get("show_time") or event.get("doors_time") or ""
    return f"{event.get('date','')}-{event.get('venue','')}-{show_time}-{lead}"

