from scraper.venues.dice import _artists, _price


def test_dice_price_uses_lowest_ticket_price():
    assert _price({"ticket_types": [{"total_price": 2500}, {"total_price": 1800}]}) == "From $18"


def test_dice_artists_fall_back_to_event_name_when_artist_names_are_empty():
    artists = _artists({"name": "Fallback Show", "detailed_artists": [{"name": None}]})
    assert artists == [{"name": "Fallback Show", "genre": None, "spotify_url": None}]
