from scraper.venues.aeg import transform_aeg_event


def test_aeg_transform_extracts_under_k_event():
    raw = {
        "eventId": "123",
        "active": True,
        "publishStatus": 1,
        "private": False,
        "eventDateTimeISO": "2026-08-22T19:00:00-04:00",
        "eventDateTimeZone": "America/New_York",
        "doorDateTime": "2026-08-22T18:00:00",
        "title": {
            "headlinersText": "Sample Headliner",
            "supportingText": "First Opener, Second Opener",
        },
        "ticketing": {"url": "https://www.axs.com/events/123/sample"},
        "ticketPriceLow": "$25",
        "ticketPriceHigh": "$40",
        "description": "<p>A concise event description.</p>",
        "media": {
            "wide": {
                "width": 678,
                "height": 399,
                "file_name": "https://images.example.com/wide.jpg",
            },
            "square": {
                "width": 800,
                "height": 800,
                "file_name": "https://images.example.com/square.jpg",
            },
        },
    }

    event = transform_aeg_event(
        raw,
        "Under the K Bridge",
        info_url_template="https://venue.example.com/detail?id={event_id}",
    )

    assert event is not None
    assert event["date"] == "2026-08-22"
    assert event["doors_time"] == "18:00"
    assert event["show_time"] == "19:00"
    assert [artist["name"] for artist in event["artists"]] == [
        "Sample Headliner",
        "First Opener",
        "Second Opener",
    ]
    assert event["ticket_url"] == "https://www.axs.com/events/123/sample"
    assert event["info_url"] == "https://venue.example.com/detail?id=123"
    assert event["image_url"] == "https://images.example.com/wide.jpg"
    assert event["price"] == "$25 - $40"
    assert event["description"] == "A concise event description."
