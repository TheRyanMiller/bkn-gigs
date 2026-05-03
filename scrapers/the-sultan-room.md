# The Sultan Room

## Scraping approach

The Sultan Room embeds a DICE partner calendar. The scraper queries DICE with venue filters for The Sultan Room, The Turk's Inn, and The Sultan Room Rooftop.

## Category mappings

Concerts are the default. DICE genre/type tags and event descriptions can override to comedy or misc.

## Edge cases

The venue calendar includes adjacent rooms and rooftop programming. The registry keeps those filters together because they are part of the same venue ecosystem.

## Opinionated decisions

DICE is used as the source of truth because it carries ticket status, pricing, image, and event URLs in one paginated API.
