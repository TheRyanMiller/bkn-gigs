from __future__ import annotations

import html
import re

from bs4 import BeautifulSoup


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    if "<" in value or ">" in value:
        soup = BeautifulSoup(value, "html.parser")
        text = soup.get_text(" ", strip=True)
    else:
        text = value
    text = html.unescape(re.sub(r"\s+", " ", text).strip())
    return text or None


def first_sentence(value: str | None, max_length: int = 280) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rsplit(" ", 1)[0].strip() + "..."
