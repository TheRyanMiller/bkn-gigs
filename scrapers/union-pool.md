# Union Pool

## Scraping approach

Union Pool uses an embedded DICE partner calendar. The scraper queries the DICE partner endpoint with the Union Pool promoter filter.

## Category mappings

Concerts are the default. DICE genre and type tags are used by shared category detection.

## Edge cases

DICE pagination uses `links.next`, so the scraper follows that URL instead of assuming fixed page counts.

## Opinionated decisions

The promoter filter is used because Union Pool's widget is configured around the promoter account rather than only a venue name.
