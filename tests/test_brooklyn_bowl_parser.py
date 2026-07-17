from scraper.venues.brooklyn_bowl import _parse_listing


def test_brooklyn_bowl_listing_extracts_event_details():
    html = """
    <article class="eventItem">
      <div class="venue">Brooklyn</div>
      <div class="date outside" aria-label="July 17 2026">Fri July 17th</div>
      <div class="pre-title-tagline">Brooklyn Bowl Presents</div>
      <h3 class="title"><a href="/brooklyn/events/detail/sample-band">Sample Band</a></h3>
      <div class="tagline">Opener</div>
      <div class="time">Doors: 6:00 PM / Show: 8:00 PM</div>
      <div class="buttons"><a href="https://tickets.example.com/sample-band">Get Tickets</a></div>
      <div class="thumb"><img src="/assets/sample-band.jpg"></div>
    </article>
    """

    events = _parse_listing(html)

    assert len(events) == 1
    event = events[0]
    assert event["venue"] == "Brooklyn Bowl"
    assert event["date"] == "2026-07-17"
    assert event["doors_time"] == "18:00"
    assert event["show_time"] == "20:00"
    assert [artist["name"] for artist in event["artists"]] == ["Sample Band", "Opener"]
    assert event["ticket_url"] == "https://tickets.example.com/sample-band"
    assert event["info_url"] == "https://www.brooklynbowl.com/brooklyn/events/detail/sample-band"
    assert event["image_url"] == "https://www.brooklynbowl.com/assets/sample-band.jpg"
    assert event["description"] == "Brooklyn Bowl Presents — Opener"


def test_brooklyn_bowl_listing_ignores_closures_and_other_locations():
    html = """
    <article class="eventItem">
      <div class="venue">Brooklyn</div>
      <div class="date outside" aria-label="July 18 2026"></div>
      <h3 class="title"><a href="/closed">Closed for a Private Event</a></h3>
    </article>
    <article class="eventItem">
      <div class="venue">Nashville</div>
      <div class="date outside" aria-label="July 19 2026"></div>
      <h3 class="title"><a href="/nashville-show">Nashville Show</a></h3>
    </article>
    """

    assert _parse_listing(html) == []
