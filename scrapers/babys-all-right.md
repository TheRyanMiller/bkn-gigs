# Baby's All Right

## Scraping approach

Baby's All Right's Eventim page blocks automated requests, so the scraper uses the complete paginated Baby's All Right calendar on Songkick. It parses machine-readable dates, artist lineups, listing links, and images.

## Category mappings

Music is the default category. Page text is still passed through category detection for comedy or other non-concert programming.

## Edge cases

Songkick listing links are used for both ticket and info URLs because the calendar does not expose the venue's final checkout URL directly.

## Opinionated decisions

Do not scrape only homepage featured events. The paginated venue calendar is used so the result covers the full published schedule.
