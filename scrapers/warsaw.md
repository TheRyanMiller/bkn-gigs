# Warsaw

## Scraping approach

Warsaw is scraped from the Live Nation content API with venue id `KovZpZAdJtAA`.

## Category mappings

Structured Live Nation segment and genre values are used first. If those are inconclusive, the event name and description go through shared category detection.

## Edge cases

Door times may appear only in `important_info`; the scraper extracts them with a conservative door-time pattern.

## Opinionated decisions

The Live Nation content API is used instead of page HTML because it returns normalized event URLs, local start dates, images, genres, and artists.
