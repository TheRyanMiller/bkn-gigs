from scraper.venues.atg import _parse_detail, _parse_show_cards


def test_atg_listing_keeps_only_concert_cards():
    html = """
    <div data-testid="showCard">
      <img src="https://images.example.com/thundercat.jpg">
      <h2>Thundercat: Distracted AF Tour</h2>
      <p>Concert</p>
      <p>with TiaCorine</p>
      <p>Kings Theatre</p>
      <p>Fri, Oct 23, 2026</p>
      <a href="/events/thundercat/kings-theatre-brooklyn/">
        More information about Thundercat: Distracted AF Tour
        <span>More info</span>
      </a>
    </div>
    <div data-testid="showCard">
      <h2>A Comedy Show</h2>
      <p>Comedy</p>
      <p>Kings Theatre</p>
      <p>Sat, Oct 24, 2026</p>
      <a href="/events/comedy/kings-theatre-brooklyn/">
        More information about A Comedy Show
      </a>
    </div>
    """

    shows = _parse_show_cards(html)

    assert shows == [
        {
            "title": "Thundercat: Distracted AF Tour",
            "support": "with TiaCorine",
            "date": "2026-10-23",
            "info_url": "https://us.atgtickets.com/events/thundercat/kings-theatre-brooklyn/",
            "image_url": "https://images.example.com/thundercat.jpg",
        }
    ]


def test_atg_detail_expands_each_ticketed_performance():
    show = {
        "title": "Jill Scott – To Whom This May Concern Tour",
        "support": "with J Bambii",
        "date": "2026-07-19",
        "info_url": "https://us.atgtickets.com/events/jill-scott/kings-theatre-brooklyn/",
        "image_url": "https://images.example.com/card.jpg",
    }
    html = """
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "TheaterEvent",
        "name": "Jill Scott – To Whom This May Concern Tour",
        "description": "Jill Scott performs live in Brooklyn.",
        "startDate": "2026-07-18T23:00:00.000Z",
        "image": ["https://images.example.com/hero.jpg"]
      }
    </script>
    <a href="/events/jill-scott/kings-theatre-brooklyn/tickets/one/">
      Buy tickets for Sat, Jul 18, 2026 at 7:00 PM ET
    </a>
    <a href="/events/jill-scott/kings-theatre-brooklyn/tickets/two/">
      Buy tickets for Sun, Jul 19, 2026 at 7:00 PM ET
    </a>
    """

    events = _parse_detail(html, show)

    assert [(event["date"], event["show_time"]) for event in events] == [
        ("2026-07-18", "19:00"),
        ("2026-07-19", "19:00"),
    ]
    assert [artist["name"] for artist in events[0]["artists"]] == ["Jill Scott", "J Bambii"]
    assert events[0]["image_url"] == "https://images.example.com/hero.jpg"
    assert events[0]["description"] == "Jill Scott performs live in Brooklyn."


def test_atg_detail_falls_back_to_schema_when_tickets_are_unreleased():
    show = {
        "title": "Thundercat: Distracted AF Tour",
        "support": "with TiaCorine",
        "date": "2026-10-23",
        "info_url": "https://us.atgtickets.com/events/thundercat/kings-theatre-brooklyn/",
        "image_url": None,
    }
    html = """
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "TheaterEvent",
        "name": "Thundercat: Distracted AF Tour",
        "startDate": "2026-10-24T00:00:00.000Z"
      }
    </script>
    """

    events = _parse_detail(html, show)

    assert len(events) == 1
    assert events[0]["date"] == "2026-10-23"
    assert events[0]["show_time"] == "20:00"
    assert [artist["name"] for artist in events[0]["artists"]] == ["Thundercat", "TiaCorine"]
    assert events[0]["ticket_url"] == show["info_url"]
