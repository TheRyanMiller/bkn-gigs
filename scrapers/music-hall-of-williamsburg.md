# Music Hall of Williamsburg

## Scraping approach

Music Hall of Williamsburg uses Bowery Presents venue pages. The scraper parses the initial venue page and then pages through `/info/events/get` with `venues=music-hall-of-williamsburg`.

## Category mappings

Concerts are the default. The shared text classifier can override for comedy, theater, sports, or miscellaneous events if Bowery lists a mixed bill.

## Edge cases

The visible page only contains an initial batch of events, so the AJAX pagination endpoint is required for completeness.

## Opinionated decisions

AXS ticket links are preferred for `ticket_url`, while Bowery event detail links are retained as `info_url`.
