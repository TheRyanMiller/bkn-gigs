from scraper.pipeline import r2


def test_public_and_state_keys_are_namespaced():
    assert r2.public_key("events.json") == "apps/bkn-gigs/prod/public/events.json"
    assert r2.public_key("scrape-status.json") == "apps/bkn-gigs/prod/public/scrape-status.json"
    assert r2.state_key("seen-cache.json") == "apps/bkn-gigs/prod/state/seen-cache.json"
    assert r2.state_key("scrape-log.txt") == "apps/bkn-gigs/prod/state/scrape-log.txt"


def test_shared_artist_cache_keys_are_under_shared_prefix():
    assert r2.shared_key("artist-cache.json") == "shared/artist-cache.json"
    assert r2.shared_key("artist-spotify-cache.json") == "shared/artist-spotify-cache.json"

