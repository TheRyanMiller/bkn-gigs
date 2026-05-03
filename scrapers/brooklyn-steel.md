# Brooklyn Steel

## Scraping approach

Brooklyn Steel uses the same Bowery Presents source as Music Hall of Williamsburg. The scraper parses the venue HTML and paginates `/info/events/get` with `venues=brooklyn-steel`.

## Category mappings

Concerts are the default. Category detection is applied to event title and support text.

## Edge cases

Bowery event times are embedded as machine-readable timestamps and can be UTC. The scraper converts timestamps into New York local date and time.

## Opinionated decisions

The Bowery source is preferred over generic search or JSON-LD because it exposes the event list and AXS purchase URLs directly.
