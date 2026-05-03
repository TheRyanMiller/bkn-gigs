from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from scraper.utils.dates import today_local
from scraper.venues.bowery import scrape_bowery_venue
from scraper.venues.brooklyn_bowl import scrape_brooklyn_bowl
from scraper.venues.dice import scrape_dice_events
from scraper.venues.elsewhere import scrape_elsewhere
from scraper.venues.eventbrite_html import scrape_littlefield
from scraper.venues.live_nation_content import scrape_live_nation_venue
from scraper.venues.seetickets import scrape_babys_all_right
from scraper.venues.spacecrafted import scrape_union_hall
from scraper.venues.squarespace import scrape_brooklyn_comedy_collective
from scraper.venues.venuepilot import scrape_venuepilot_events


@dataclass(frozen=True)
class VenueScraper:
    name: str
    fetch: Callable[[], list[dict]]


def get_scrapers() -> list[VenueScraper]:
    today = today_local().isoformat()
    return [
        VenueScraper("Baby's All Right", scrape_babys_all_right),
        VenueScraper("Music Hall of Williamsburg", lambda: scrape_bowery_venue("Music Hall of Williamsburg", "music-hall-of-williamsburg")),
        VenueScraper("Brooklyn Steel", lambda: scrape_bowery_venue("Brooklyn Steel", "brooklyn-steel")),
        VenueScraper("Warsaw", lambda: scrape_live_nation_venue("Warsaw", "KovZpZAdJtAA")),
        VenueScraper("Elsewhere", scrape_elsewhere),
        VenueScraper("Brooklyn Bowl", scrape_brooklyn_bowl),
        VenueScraper(
            "Union Pool",
            lambda: scrape_dice_events(
                "Union Pool",
                api_key="7rU0bJyVtM5s3vDdYNiuQ4UtDo6pAnmH1QgXsI7E",
                promoter_filters=["Loop De Lou Production Corp dba Union Pool"],
                default_category="concerts",
            ),
        ),
        VenueScraper("Market Hotel", lambda: scrape_venuepilot_events("Market Hotel", 100, start_date=today)),
        VenueScraper(
            "The Sultan Room",
            lambda: scrape_dice_events(
                "The Sultan Room",
                api_key="j3UZPWFkiQ2UFTppf79rFatRpao3ol7l5PWjmTE9",
                venue_filters=["The Sultan Room", "The Turk's Inn", "The Sultan Room Rooftop"],
                default_category="concerts",
            ),
        ),
        VenueScraper("The Bell House", lambda: scrape_live_nation_venue("The Bell House", "KovZ917ARvk")),
        VenueScraper("Union Hall", scrape_union_hall),
        VenueScraper("Littlefield", scrape_littlefield),
        VenueScraper(
            "C'mon Everybody",
            lambda: scrape_dice_events(
                "C'mon Everybody",
                api_key="PyghT2k59li4oGXIef8t4Git2vRl58H7WAuUJGpd",
                venue_filters=["C'mon Everybody", "Cmon Everybody"],
                default_category="concerts",
            ),
        ),
        VenueScraper("Brooklyn Comedy Collective", scrape_brooklyn_comedy_collective),
        VenueScraper("Brooklyn Paramount", lambda: scrape_live_nation_venue("Brooklyn Paramount", "KovZpZA77ldA")),
    ]

