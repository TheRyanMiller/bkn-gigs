# Baby's All Right

## Scraping approach

Baby's All Right redirects to a See Tickets white-label page at `wl.eventim.us/BabysAllRightBrooklyn`. The scraper requests that page and parses event cards when they are available in HTML.

## Category mappings

Music is the default category. Page text is still passed through category detection for comedy or other non-concert programming.

## Edge cases

See Tickets can block direct HTTP requests with anti-bot protection. When blocked, this scraper returns an empty list so the full Brooklyn scrape can keep running.

## Opinionated decisions

Do not scrape only homepage featured events. If the full See Tickets calendar is inaccessible, prefer an empty result plus status visibility over partial data.
