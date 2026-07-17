# Barclays Center

## Scraping approach

The scraper reads Barclays Center's official concert-only calendar at `https://www.barclayscenter.com/events/category/concerts`. Each event card includes a Unix timestamp with the local performance date and time, an official detail URL, an image, and a Ticketmaster purchase URL.

## Category mappings

Only the official `concerts` calendar is read, so every event is categorized as `concerts`. Sports, family shows, and other arena programming are intentionally excluded.

## Edge cases

Ticket links occasionally contain surrounding whitespace; URLs are cleaned before validation. Multi-night runs appear as separate cards with distinct timestamps and ticket URLs.

## Opinionated decisions

The venue's first-party calendar is preferred over a broad Ticketmaster search so unrelated arena programming does not add noise.
