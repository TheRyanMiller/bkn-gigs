from __future__ import annotations

import logging
from typing import Any

import requests

from scraper.config import USER_AGENT

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 25


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return session


def get_text(
    url: str,
    *,
    session: requests.Session | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    client = session or make_session()
    response = client.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def get_json(
    url: str,
    *,
    session: requests.Session | None = None,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | list[tuple[str, Any]] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    client = session or make_session()
    response = client.get(url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def post_json(
    url: str,
    *,
    json: dict[str, Any],
    session: requests.Session | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    client = session or make_session()
    response = client.post(url, json=json, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()

