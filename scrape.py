from __future__ import annotations

import logging
from typing import Any

from scraper import spotify_enrichment
from scraper.pipeline.io import append_log, load_events, load_seen_cache, trim_log, write_outputs
from scraper.pipeline.merge import merge_seen_cache, sort_events
from scraper.pipeline.validate import validate_events
from scraper.registry import get_scrapers
from scraper.utils.dates import now_iso, today_local

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("scrape")


def run() -> dict[str, Any]:
    scraped_at = now_iso()
    today = today_local().isoformat()
    all_events: list[dict[str, Any]] = []
    venue_status: list[dict[str, Any]] = []
    previous_events = load_events()
    seen_cache = load_seen_cache()

    log.info("Starting Brooklyn scrape at %s", scraped_at)
    append_log(f"{scraped_at} start bkn-gigs scrape")

    for scraper in get_scrapers():
        try:
            events = scraper.fetch()
            future_events = [event for event in events if event.get("date", "") >= today]
            if not future_events and not scraper.allow_empty:
                raise ValueError(f"{scraper.name} returned no future events")
            validate_events(future_events)
            all_events.extend(future_events)
            venue_status.append(
                {
                    "venue": scraper.name,
                    "status": "ok",
                    "count": len(future_events),
                    "message": None,
                    "scraped_at": now_iso(),
                }
            )
            log.info("%s: %s events", scraper.name, len(future_events))
        except Exception as exc:  # noqa: BLE001 - scraper errors should not stop other venues.
            venue_status.append(
                {
                    "venue": scraper.name,
                    "status": "error",
                    "count": 0,
                    "message": str(exc),
                    "scraped_at": now_iso(),
                }
            )
            log.exception("%s failed", scraper.name)

    events, seen_cache = merge_seen_cache(sort_events(all_events), seen_cache, scraped_at=scraped_at)
    events = spotify_enrichment.enrich_events_with_spotify(
        events,
        run_timestamp=scraped_at,
        log_func=log.info,
    )
    events = sort_events(events)
    validate_events(events)

    status = {
        "app": "bkn-gigs",
        "scraped_at": scraped_at,
        "total_events": len(events),
        "previous_total_events": len(previous_events),
        "venues": venue_status,
    }
    write_outputs(events=events, status=status, seen_cache=seen_cache)
    append_log(f"{now_iso()} finish bkn-gigs scrape: {len(events)} events")
    trim_log()
    log.info("Finished Brooklyn scrape with %s events", len(events))
    return status


if __name__ == "__main__":
    run()
