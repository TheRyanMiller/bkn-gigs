from scraper.venues.barclays import _parse_listing


def test_barclays_parser_uses_timestamp_for_show_time():
    html = """
    <div id="eventsList">
      <div class="entry featured clearfix" data-timestamp="1784593800">
        <div class="thumb grid-only"><img src="/assets/show.jpg"></div>
        <div class="info clearfix">
          <h3>Sample Arena Artist</h3>
          <h4>World Tour</h4>
        </div>
        <div class="info info-absolute grid-only">
          <div class="info-body">A one-night concert in Brooklyn.</div>
        </div>
        <div class="buttons event_buttons list-only">
          <a class="tickets" href=" https://tickets.example.com/show ">Buy Tickets</a>
          <a class="more" href="/events/detail/show">Info</a>
        </div>
      </div>
    </div>
    """

    events = _parse_listing(html)

    assert len(events) == 1
    event = events[0]
    assert event["venue"] == "Barclays Center"
    assert event["date"] == "2026-07-20"
    assert event["show_time"] == "20:30"
    assert event["artists"][0]["name"] == "Sample Arena Artist"
    assert event["ticket_url"] == "https://tickets.example.com/show"
    assert event["info_url"] == "https://www.barclayscenter.com/events/detail/show"
    assert event["image_url"] == "https://www.barclayscenter.com/assets/show.jpg"
    assert event["description"] == "A one-night concert in Brooklyn."
