# Brooklyn Comedy Collective

## Scraping approach

Brooklyn Comedy Collective uses Squarespace. The scraper requests the collection JSON at `show-schedule?format=json-pretty` and extracts event metadata plus Eventbrite links from body HTML.

## Category mappings

Comedy is the default. Shared detection is still applied so classes, theater, or misc events can be classified separately when obvious.

## Edge cases

Eventbrite ticket URLs can appear inside rich body HTML instead of a top-level field. The scraper scans body markup for the first Eventbrite URL.

## Opinionated decisions

The Squarespace JSON collection is preferred over browser-rendered cards because it includes structured dates, page URLs, assets, and body content.
