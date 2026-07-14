import scrape
from scraper.registry import VenueScraper


def test_run_marks_empty_scraper_as_error(monkeypatch):
    monkeypatch.setattr(scrape, "get_scrapers", lambda: [VenueScraper("Empty Venue", lambda: [])])
    monkeypatch.setattr(scrape, "load_events", lambda: [])
    monkeypatch.setattr(scrape, "load_seen_cache", lambda: {})
    monkeypatch.setattr(scrape, "write_outputs", lambda **kwargs: None)
    monkeypatch.setattr(scrape, "append_log", lambda message: None)
    monkeypatch.setattr(scrape, "trim_log", lambda: None)

    status = scrape.run()

    assert status["venues"][0]["status"] == "error"
    assert status["venues"][0]["message"] == "Empty Venue returned no future events"
