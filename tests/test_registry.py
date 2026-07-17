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
        "Barclays Center",
        "Kings Theatre",
        "Under the K Bridge",
        "Lena Horne Bandshell",
    ]


def test_outdoor_seasonal_venues_allow_empty_results():
    scrapers = {scraper.name: scraper for scraper in get_scrapers()}
    assert scrapers["Under the K Bridge"].allow_empty is True
    assert scrapers["Lena Horne Bandshell"].allow_empty is True
