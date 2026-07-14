from scraper.venues.spacecrafted import _eventbrite_event


def test_eventbrite_event_transforms_union_hall_listing():
    event = _eventbrite_event(
        {
            "name": "Sample Comedy Show",
            "url": "https://www.eventbrite.com/e/sample-123",
            "start_date": "2026-07-15",
            "start_time": "19:30:00",
            "timezone": "America/New_York",
            "summary": "Stand-up comedy",
            "image": {"url": "https://example.com/show.jpg"},
            "ticket_availability": {"minimum_ticket_price": {"major_value": "15.92"}},
        }
    )

    assert event is not None
    assert event["venue"] == "Union Hall"
    assert event["date"] == "2026-07-15"
    assert event["show_time"] == "19:30"
    assert event["price"] == "From $15.92"
    assert event["category"] == "comedy"
