from scraper.registry import get_scrapers


def test_registry_contains_active_brooklyn_venues():
    names = [scraper.name for scraper in get_scrapers()]
    assert names == [
        "Baby's All Right",
        "Music Hall of Williamsburg",
        "Brooklyn Steel",
        "Warsaw",
        "Elsewhere",
        "Brooklyn Bowl",
        "Union Pool",
        "Market Hotel",
        "The Sultan Room",
        "The Bell House",
        "Union Hall",
        "Brooklyn Paramount",
    ]
