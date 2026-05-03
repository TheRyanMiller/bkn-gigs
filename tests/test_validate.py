import pytest

from scraper.pipeline.validate import validate_event, validate_events


def valid_event():
    return {
        "venue": "Brooklyn Steel",
        "date": "2026-06-01",
        "doors_time": "19:00",
        "show_time": "20:00",
        "artists": [{"name": "Sample Band", "genre": None, "spotify_url": None}],
        "ticket_url": "https://example.com/tickets",
        "info_url": "https://example.com/info",
        "image_url": None,
        "description": None,
        "price": None,
        "category": "concerts",
    }


def test_valid_event_passes_schema():
    assert validate_event(valid_event()) == []


def test_missing_required_field_fails():
    event = valid_event()
    event["ticket_url"] = None
    assert "missing ticket_url" in validate_event(event)


def test_invalid_category_raises_for_event_list():
    event = valid_event()
    event["category"] = "food"
    with pytest.raises(ValueError):
        validate_events([event])

