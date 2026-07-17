from scraper.venues.bric import _parse_season


def test_bric_parser_keeps_only_lena_horne_bandshell_events():
    html = """
    <main>
      <p>Our 2026 season brings music to Brooklyn.</p>
      <div class="m-card-event-c">
        <div class="m-card-event-c__pretitle">08.28</div>
        <div class="m-card-event-c__text">Fri | 6:00 PM</div>
        <h4 class="m-card-event-c__title">
          BRIC Celebrate Brooklyn! and The Action Lab present:
          Common and Special Guests To Honor the Social Justice Legacy of Harry Belafonte
        </h4>
        <div class="m-card-event-c__location">
          <span class="a-meta__text">Lena Horne Bandshell</span>
        </div>
        <div class="m-card-event-c__cost">
          <span class="a-meta__text">FREE</span>
        </div>
        <a href="https://bricartsmedia.org/event/common/">
          <img alt="https://images.example.com/common.jpg">
        </a>
      </div>
      <div class="m-card-event-c">
        <div class="m-card-event-c__pretitle">07.25</div>
        <div class="m-card-event-c__text">Sat | 1:00 PM</div>
        <h4 class="m-card-event-c__title">A Brower Park Event</h4>
        <div class="m-card-event-c__location">
          <span class="a-meta__text">Brower Park</span>
        </div>
        <a href="https://bricartsmedia.org/event/brower-park/"></a>
      </div>
    </main>
    """

    events = _parse_season(html)

    assert len(events) == 1
    event = events[0]
    assert event["venue"] == "Lena Horne Bandshell"
    assert event["date"] == "2026-08-28"
    assert event["doors_time"] == "18:00"
    assert event["show_time"] is None
    assert [artist["name"] for artist in event["artists"]] == ["Common"]
    assert event["ticket_url"] == "https://bricartsmedia.org/event/common/"
    assert event["image_url"] == "https://images.example.com/common.jpg"
    assert event["price"] == "Free"
