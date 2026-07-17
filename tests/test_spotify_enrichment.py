from scraper import spotify_enrichment


def _event(name: str) -> dict:
    return {
        "artists": [{"name": name, "genre": None, "spotify_url": None}],
    }


def test_enrichment_applies_shared_cache_hit(monkeypatch):
    spotify_enrichment._artist_cache = None
    monkeypatch.setattr(
        spotify_enrichment.r2,
        "download_json",
        lambda *_args: {
            "by_name": {
                "sample band": {
                    "spotify_url": "https://open.spotify.com/artist/ABC123",
                }
            }
        },
    )
    monkeypatch.setattr(spotify_enrichment.config, "SPOTIFY_CLIENT_ID", None)
    monkeypatch.setattr(spotify_enrichment.config, "SPOTIFY_CLIENT_SECRET", None)

    events = spotify_enrichment.enrich_events_with_spotify([_event("Sample Band")])

    assert events[0]["artists"][0]["spotify_url"] == "https://open.spotify.com/artist/ABC123"


def test_candidate_picker_requires_unambiguous_exact_match():
    candidates = [
        {"name": "Sample Band", "popularity": 50},
        {"name": "Sample Band", "popularity": 45},
        {"name": "Different Band", "popularity": 100},
    ]

    assert spotify_enrichment._pick_candidate("Sample Band", candidates) is None

    candidates[0]["popularity"] = 80
    assert spotify_enrichment._pick_candidate("Sample Band", candidates) == candidates[0]


def test_enrichment_searches_and_saves_shared_cache(monkeypatch):
    spotify_enrichment._artist_cache = None
    uploads = []
    monkeypatch.setattr(spotify_enrichment.r2, "download_json", lambda *_args: {"by_name": {}})
    monkeypatch.setattr(spotify_enrichment.r2, "upload_json", lambda key, data: uploads.append((key, data)))
    monkeypatch.setattr(spotify_enrichment.config, "SPOTIFY_CLIENT_ID", "client")
    monkeypatch.setattr(spotify_enrichment.config, "SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(
        spotify_enrichment,
        "_search_artist",
        lambda *_args: ("https://open.spotify.com/artist/ABC123", "exact"),
    )

    events = spotify_enrichment.enrich_events_with_spotify([_event("Sample Band")], search_limit=1)

    assert events[0]["artists"][0]["spotify_url"] == "https://open.spotify.com/artist/ABC123"
    assert uploads[0][0] == "shared/artist-spotify-cache.json"
    assert uploads[0][1]["by_name"]["sample band"]["spotify_url"].endswith("/ABC123")
