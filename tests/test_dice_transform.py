from scraper.venues.dice import _price


def test_dice_price_uses_lowest_ticket_price():
    assert _price({"ticket_types": [{"total_price": 2500}, {"total_price": 1800}]}) == "From $18"

