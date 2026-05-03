# Union Hall

## Scraping approach

Union Hall's Spacecrafted page renders a large event collection in HTML. The scraper parses collection items, Eventbrite links, dates, titles, and images.

## Category mappings

Comedy is the default because Union Hall's calendar is comedy-forward. Shared detection can classify music or miscellaneous events.

## Edge cases

Many links point directly to Eventbrite. The scraper keeps those as ticket URLs and preserves the Union Hall event link as info when available.

## Opinionated decisions

HTML parsing is used here because the rendered collection contains enough event data and avoids relying on homepage feature blocks.
