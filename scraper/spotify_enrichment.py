from __future__ import annotations

import re
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any, Callable

import requests

from scraper import config
from scraper.pipeline import r2

_CACHE_NAME = "artist-spotify-cache.json"
_SEARCH_SOURCE = "spotify-search-v1"
_artist_cache: dict[str, Any] | None = None
_spotify_token: str | None = None
_spotify_token_expires_at = 0.0


def normalize_artist_name(name: str | None) -> str:
    if not name:
        return ""
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"^(?:rescheduled|postponed|cancelled|canceled)\s*:\s*", "", normalized)
    normalized = re.sub(r"\([^)]*\)", " ", normalized)
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_spotify_url(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"(?:open\.spotify\.com/artist/|spotify:artist:)([A-Za-z0-9]+)", url)
    return f"https://open.spotify.com/artist/{match.group(1)}" if match else None


def _cache() -> dict[str, Any]:
    global _artist_cache
    if _artist_cache is None:
        loaded = r2.download_json(r2.shared_key(_CACHE_NAME), {"by_name": {}})
        _artist_cache = loaded if isinstance(loaded, dict) else {"by_name": {}}
        if not isinstance(_artist_cache.get("by_name"), dict):
            _artist_cache["by_name"] = {}
    return _artist_cache


def _save_cache() -> None:
    if _artist_cache is not None:
        r2.upload_json(r2.shared_key(_CACHE_NAME), _artist_cache)


def _get_token() -> str | None:
    global _spotify_token, _spotify_token_expires_at
    if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
        return None
    if _spotify_token and time.time() < _spotify_token_expires_at - 60:
        return _spotify_token

    response = requests.post(
        config.SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET),
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    _spotify_token = payload.get("access_token")
    _spotify_token_expires_at = time.time() + int(payload.get("expires_in", 3600))
    return _spotify_token


def _genres_overlap(genre_hint: str | None, candidate_genres: list[str]) -> bool:
    if not genre_hint or not candidate_genres:
        return False
    hints = set(re.split(r"[\s/,-]+", genre_hint.lower()))
    return any(hints & set(re.split(r"[\s/,-]+", genre.lower())) for genre in candidate_genres)


def _pick_candidate(
    artist_name: str,
    candidates: list[dict[str, Any]],
    genre_hint: str | None = None,
) -> dict[str, Any] | None:
    target = normalize_artist_name(artist_name)
    exact = [candidate for candidate in candidates if normalize_artist_name(candidate.get("name")) == target]
    if len(exact) == 1:
        return exact[0]
    if not exact:
        return None

    genre_matches = [
        candidate
        for candidate in exact
        if _genres_overlap(genre_hint, candidate.get("genres") or [])
    ]
    if len(genre_matches) == 1:
        return genre_matches[0]
    if genre_matches:
        exact = genre_matches

    ranked = sorted(exact, key=lambda candidate: candidate.get("popularity", 0), reverse=True)
    if len(ranked) == 1 or ranked[0].get("popularity", 0) - ranked[1].get("popularity", 0) >= 20:
        return ranked[0]
    return None


def _search_artist(artist_name: str, genre_hint: str | None = None) -> tuple[str | None, str]:
    global _spotify_token
    try:
        token = _get_token()
        if not token:
            return None, "no-token"
        response = requests.get(
            config.SPOTIFY_SEARCH_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={"q": f'artist:"{artist_name}"', "type": "artist", "market": "US", "limit": 10},
            timeout=10,
        )
        if response.status_code == 401:
            _spotify_token = None
            token = _get_token()
            if not token:
                return None, "no-token"
            response = requests.get(
                config.SPOTIFY_SEARCH_URL,
                headers={"Authorization": f"Bearer {token}"},
                params={"q": f'artist:"{artist_name}"', "type": "artist", "market": "US", "limit": 10},
                timeout=10,
            )
        response.raise_for_status()
    except requests.RequestException as exc:
        status = getattr(exc.response, "status_code", None)
        return None, f"error-{status or 'request'}"
    except (TypeError, ValueError):
        return None, "error-response"

    candidates = (response.json().get("artists") or {}).get("items") or []
    candidate = _pick_candidate(artist_name, candidates, genre_hint)
    if not candidate:
        return None, "no-exact-match"
    return normalize_spotify_url((candidate.get("external_urls") or {}).get("spotify")), "exact"


def enrich_events_with_spotify(
    events: list[dict[str, Any]],
    *,
    run_timestamp: str | None = None,
    search_limit: int | None = None,
    log_func: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    log = log_func or (lambda _message: None)
    cache = _cache()
    entries: dict[str, dict[str, Any]] = cache["by_name"]
    timestamp = run_timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    limit = config.SPOTIFY_SEARCH_LIMIT if search_limit is None else max(search_limit, 0)

    grouped: dict[str, list[dict[str, Any]]] = {}
    display_names: dict[str, str] = {}
    genre_hints: dict[str, str | None] = {}
    cache_changed = False
    for event in events:
        for artist in event.get("artists") or []:
            normalized = normalize_artist_name(artist.get("name"))
            if not normalized or normalized in {"tba", "tbd", "unknown", "special guest"}:
                continue
            existing_url = normalize_spotify_url(artist.get("spotify_url"))
            if existing_url:
                artist["spotify_url"] = existing_url
                cache_entry = {
                    "spotify_url": existing_url,
                    "source": "event",
                    "updated_at": timestamp,
                }
                if entries.get(normalized) != cache_entry:
                    entries[normalized] = cache_entry
                    cache_changed = True
                continue
            grouped.setdefault(normalized, []).append(artist)
            display_names.setdefault(normalized, artist.get("name") or normalized)
            genre_hints.setdefault(normalized, artist.get("genre"))

    cache_hits = 0
    searches = 0
    matches = 0
    for normalized, artists in grouped.items():
        entry = entries.get(normalized)
        cached_url = normalize_spotify_url(entry.get("spotify_url")) if entry else None
        if cached_url:
            for artist in artists:
                artist["spotify_url"] = cached_url
            cache_hits += len(artists)
            continue
        if entry or searches >= limit or not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
            continue

        url, reason = _search_artist(display_names[normalized], genre_hints[normalized])
        searches += 1
        if reason == "error-429":
            break
        if not reason.startswith("error-") and reason != "no-token":
            entries[normalized] = {
                "spotify_url": url,
                "source": f"{_SEARCH_SOURCE}:{reason}",
                "updated_at": timestamp,
            }
            cache_changed = True
        if url:
            for artist in artists:
                artist["spotify_url"] = url
            matches += len(artists)

    if cache_changed:
        _save_cache()
    log(f"Spotify links: cache_hits={cache_hits} searches={searches} matches={matches}")
    return events
