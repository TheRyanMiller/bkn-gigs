from __future__ import annotations

import os
from pathlib import Path

APP_SLUG = os.getenv("APP_SLUG", "bkn-gigs")
APP_ENV = os.getenv("APP_ENV", "prod")

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "ui"
EVENTS_DIR = FRONTEND_DIR / "public" / "events"

EVENTS_PATH = EVENTS_DIR / "events.json"
STATUS_PATH = EVENTS_DIR / "scrape-status.json"
SEEN_CACHE_PATH = EVENTS_DIR / "seen-cache.json"
SCRAPE_LOG_PATH = EVENTS_DIR / "scrape-log.txt"

R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "atl-gigs-data")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL") or os.getenv("AWS_ENDPOINT_URL_S3")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
R2_PUBLIC_URL = os.getenv(
    "R2_PUBLIC_URL",
    "https://pub-756023fa49674586a44105ba7bf52137.r2.dev",
).rstrip("/")

R2_KEY_PREFIX = os.getenv("R2_KEY_PREFIX", f"apps/{APP_SLUG}/{APP_ENV}").strip("/")
R2_PUBLIC_PREFIX = os.getenv("R2_PUBLIC_PREFIX", f"{R2_KEY_PREFIX}/public").strip("/")
R2_STATE_PREFIX = os.getenv("R2_STATE_PREFIX", f"{R2_KEY_PREFIX}/state").strip("/")
R2_SHARED_PREFIX = os.getenv("R2_SHARED_PREFIX", "shared").strip("/")
R2_SHARE_ARTIST_CACHES = os.getenv("R2_SHARE_ARTIST_CACHES", "true").lower() in {
    "1",
    "true",
    "yes",
}

LOCAL_TIMEZONE = os.getenv("LOCAL_TIMEZONE", "America/New_York")
USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
)

CATEGORIES = {"concerts", "comedy", "broadway", "sports", "misc"}

