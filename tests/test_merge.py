from scraper.pipeline.merge import merge_seen_cache, sort_events


def _event(name: str, date: str = "2026-06-01") -> dict:
    return {
        "venue": "Brooklyn Steel",
        "date": date,
        "doors_time": None,
        "show_time": "20:00",
        "artists": [{"name": name, "genre": None, "spotify_url": None}],
        "ticket_url": "https://example.com",
        "info_url": "https://example.com",
        "image_url": None,
        "description": None,
        "price": None,
        "category": "concerts",
    }


def test_merge_seen_cache_sets_stable_slug_and_new_flag():
    events, cache = merge_seen_cache([_event("A Band")], {}, scraped_at="2026-05-03T12:00:00-04:00")
    assert events[0]["slug"] == "2026-06-01-brooklyn-steel-20-00-a-band"
    assert events[0]["is_new"] is True

    events, cache = merge_seen_cache([_event("A Band")], cache, scraped_at="2026-05-04T12:00:00-04:00")
    assert events[0]["first_seen"] == "2026-05-03T12:00:00-04:00"
    assert events[0]["is_new"] is False


def test_sort_events_orders_by_date_time_venue():
    events = sort_events([_event("Later", "2026-06-02"), _event("Sooner", "2026-06-01")])
    assert [event["artists"][0]["name"] for event in events] == ["Sooner", "Later"]

