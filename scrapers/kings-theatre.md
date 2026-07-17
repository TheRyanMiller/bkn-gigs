# Kings Theatre

## Scraping approach

Kings Theatre's official ATG page renders complete show cards on the server. The scraper selects cards labeled `Concert`, follows each official detail page, and reads its JSON-LD plus per-performance ticket links.

## Category mappings

Only shows explicitly labeled `Concert` by ATG are included and mapped to `concerts`.

## Edge cases

Multi-night runs expose one ticket link per performance and are expanded into separate events. When tickets have not been released, the scraper uses the JSON-LD start date and the official information page as the ticket destination. If a detail page temporarily fails, the listing date remains a valid fallback.

## Opinionated decisions

Following the detail pages costs a few extra requests but preserves performance times, including multi-night runs, which the overview cards do not expose.
