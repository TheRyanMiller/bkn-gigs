# Brooklyn Bowl

## Scraping approach

Brooklyn Bowl calendar data is loaded from `/events/calendar/{year}/{month}` with the `selectedVenue=brooklyn` context. The JSON response contains rendered HTML event snippets.

## Category mappings

Concerts are the default, with shared keyword detection applied to titles and support text.

## Edge cases

The calendar response can include other Brooklyn Bowl locations. The scraper filters snippets for the Brooklyn venue marker.

## Opinionated decisions

Detail URLs are used as both `ticket_url` and `info_url` because the calendar HTML does not consistently expose a separate ticketing URL.
