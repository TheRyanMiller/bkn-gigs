# Market Hotel

## Scraping approach

Market Hotel uses VenuePilot. The scraper calls VenuePilot GraphQL `paginatedEvents` for account id `100`, starting at the current local date.

## Category mappings

Concerts are the default. Event name and description text are classified for comedy, theater, sports, or misc when applicable.

## Edge cases

VenuePilot separates door time, start time, ticket URL, and website URL. The scraper preserves those distinct fields when present.

## Opinionated decisions

The GraphQL endpoint is preferred over static page parsing because it includes pagination metadata and normalized artist/image fields.
