from scraper.venues.bowery import _parse_items


def test_bowery_parser_extracts_event_item():
    html = """
    <div class="show-item">
      <time data-start="2026-06-01T00:00:00Z"></time>
      <h3 class="show-title">Sample Band</h3>
      <div class="supporting-acts">with Opener</div>
      <a href="/events/sample-band">Info</a>
      <a class="button event ticket primary" href="https://www.axs.com/events/1">Tickets</a>
      <img src="/media/image.jpg" />
    </div>
    """
    events = _parse_items(html, "Brooklyn Steel")
    assert len(events) == 1
    assert events[0]["venue"] == "Brooklyn Steel"
    assert events[0]["artists"][0]["name"] == "Sample Band"
    assert events[0]["artists"][1]["name"] == "Opener"
    assert events[0]["info_url"] == "https://www.bowerypresents.com/events/sample-band"
    assert events[0]["image_url"] == "https://origin.bowerypresents.com/media/image.jpg"
    assert events[0]["category"] == "concerts"
