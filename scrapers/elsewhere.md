# Elsewhere

## Scraping approach

Elsewhere is a Next.js site. The scraper reads `__NEXT_DATA__` from `/events` and paginates `?page=N` while the initial event payload reports another page.

## Category mappings

Concerts are the default for live and club programming. Event type, title, description, and genres are classified for comedy or miscellaneous events.

## Edge cases

The site exposes rich room and ticket metadata, but the public SSR payload is the stable source currently used by the scraper.

## Opinionated decisions

The scraper keeps `ticket_url` from Elsewhere's event payload and builds `info_url` from the event slug when available.
