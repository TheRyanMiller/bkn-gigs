# BRIC Celebrate Brooklyn!

## Scraping approach

The scraper reads the official BRIC Celebrate Brooklyn! season page at `https://bricartsmedia.org/celebrate-brooklyn/`. It parses the published season year and event cards, retaining only shows whose listed location is `Lena Horne Bandshell`.

## Category mappings

Shows default to `concerts`, with the shared text detector available for clearly labeled alternate event types.

## Edge cases

The schedule card time is the published entry or doors time, so it is stored as `doors_time`. Free events are labeled `Free`; benefit shows link to their official BRIC detail pages. Off-site BRIC events, such as Brower Park programming, are excluded. The seasonal venue may validly have no future events between published seasons.

## Opinionated decisions

The single season page is preferred over requesting every WordPress event page. This keeps the scraper fast while preserving the official schedule, images, costs, and event destinations.
