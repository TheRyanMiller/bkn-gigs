# Union Hall

## Scraping approach

Union Hall publishes its full schedule through its official Eventbrite organizer profile. The scraper paginates the profile's JSON event feed and reads dates, times, titles, prices, links, and images.

## Category mappings

Comedy is the default because Union Hall's calendar is comedy-forward. Shared detection can classify music or miscellaneous events.

## Edge cases

Cancelled and online-only listings are skipped. Eventbrite links are used for both ticket and info URLs.

## Opinionated decisions

The organizer feed is used because Union Hall's website currently serves a TLS certificate chain that Python clients cannot validate reliably.
