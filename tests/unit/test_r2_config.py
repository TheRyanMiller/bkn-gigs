from scraper import config


def test_default_r2_keys_are_bkn_namespaced():
    assert config.APP_SLUG == "bkn-gigs"
    assert config.APP_ENV == "prod"
    assert config.R2_EVENTS_KEY == "apps/bkn-gigs/prod/public/events.json"
    assert config.R2_STATUS_KEY == "apps/bkn-gigs/prod/public/scrape-status.json"
    assert config.R2_SEEN_CACHE_KEY == "apps/bkn-gigs/prod/state/seen-cache.json"
    assert config.R2_LOG_KEY == "apps/bkn-gigs/prod/state/scrape-log.txt"
    assert config.R2_ARTIST_CACHE_KEY == "shared/artist-cache.json"
    assert config.R2_SPOTIFY_CACHE_KEY == "shared/artist-spotify-cache.json"
