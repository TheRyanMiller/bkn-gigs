from __future__ import annotations

import re

from scraper.config import CATEGORIES

COMEDY_RE = re.compile(r"\b(comedy|comedian|stand[- ]?up|improv|sketch|clown|humor|funny|laugh)\b", re.I)
BROADWAY_RE = re.compile(r"\b(theater|theatre|musical|play|opera|cabaret|stage)\b", re.I)
SPORTS_RE = re.compile(r"\b(sports?|boxing|wrestling|basketball|football|soccer|hockey|baseball|fight|ufc)\b", re.I)
CONCERT_RE = re.compile(
    r"\b(concert|live music|band|dj|dance party|album|tour|rock|indie|punk|metal|jazz|folk|rap|hip[- ]?hop|electronic|singer)\b",
    re.I,
)


def normalize_category(value: str | None, default: str = "misc") -> str:
    if not value:
        return default if default in CATEGORIES else "misc"
    normalized = value.strip().lower().replace("&", "and")
    mapping = {
        "music": "concerts",
        "concert": "concerts",
        "concerts": "concerts",
        "comedy": "comedy",
        "theatre": "broadway",
        "theater": "broadway",
        "broadway": "broadway",
        "sports": "sports",
        "sport": "sports",
        "misc": "misc",
        "other": "misc",
    }
    return mapping.get(normalized, default if default in CATEGORIES else "misc")


def detect_category_from_text(*parts: str | None, default: str = "misc") -> str:
    text = " ".join(part for part in parts if part).strip()
    if not text:
        return normalize_category(default, "misc")
    if COMEDY_RE.search(text):
        return "comedy"
    if BROADWAY_RE.search(text):
        return "broadway"
    if SPORTS_RE.search(text):
        return "sports"
    if CONCERT_RE.search(text):
        return "concerts"
    return normalize_category(default, "misc")


def category_from_ticketing(segment: str | None, genre: str | None, text: str | None = None, default: str = "misc") -> str:
    segment_category = normalize_category(segment, "")
    if segment_category in {"concerts", "comedy", "broadway", "sports"}:
        return segment_category
    return detect_category_from_text(genre, text, default=default)

