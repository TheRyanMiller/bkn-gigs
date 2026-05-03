# Littlefield

## Scraping approach

Littlefield's all-shows page renders WordPress/Eventbrite widget event cards. The scraper parses the page HTML for titles, dates, door/show labels, images, and event URLs.

## Category mappings

Comedy is the default, with text detection for concerts and other event types.

## Edge cases

The page often exposes a Littlefield event URL that opens or routes to Eventbrite rather than a direct Eventbrite URL. That URL is still a stable ticket path.

## Opinionated decisions

The all-shows page is preferred over smaller homepage listings because it provides the complete public calendar.
