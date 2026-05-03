# C'mon Everybody

## Scraping approach

C'mon Everybody embeds a DICE partner calendar. The scraper queries DICE with venue filters for both `C'mon Everybody` and `Cmon Everybody`.

## Category mappings

Concerts are the default, with DICE tags and event text used for comedy, theater, sports, or misc classification.

## Edge cases

The apostrophe is inconsistently represented across systems, so both venue spellings are queried.

## Opinionated decisions

DICE is preferred because it is the upstream calendar source visible from the venue page and includes paginated event data.
