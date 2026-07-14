from scraper.venues.seetickets import _parse_songkick_page


def test_songkick_parser_extracts_babys_event_and_next_page():
    html = """
    <div id="event-listings">
      <ul>
        <li class="with-date"><time datetime="2026-07-14T19:30:00-0400"></time></li>
        <li>
          <time datetime="2026-07-14T19:30:00-0400"></time>
          <p class="artists summary">
            <a href="/concerts/123-sample-show"><strong>Sample Band</strong><strong>Opener</strong></a>
          </p>
          <img src="//images.example.com/show.jpg" />
        </li>
      </ul>
      <a class="next_page" rel="next" href="/venues/2445014-babys-all-right/calendar?page=2">Next</a>
    </div>
    """

    events, next_url = _parse_songkick_page(html)

    assert len(events) == 1
    assert events[0]["venue"] == "Baby's All Right"
    assert events[0]["show_time"] == "19:30"
    assert [artist["name"] for artist in events[0]["artists"]] == ["Sample Band", "Opener"]
    assert events[0]["ticket_url"] == "https://www.songkick.com/concerts/123-sample-show"
    assert next_url == "https://www.songkick.com/venues/2445014-babys-all-right/calendar?page=2"
