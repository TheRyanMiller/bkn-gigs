# The Bell House

## Scraping approach

The Bell House is scraped from the Live Nation content API with venue id `KovZ917ARvk`.

## Category mappings

Live Nation segment and genre data are used first. Comedy-forward Bell House events are usually classified by structured segment or title text.

## Edge cases

Door times are not guaranteed to be first-class fields, so the scraper also checks `important_info`.

## Opinionated decisions

Live Nation API data is preferred over venue HTML because it gives consistent event URLs, local dates, images, and artist lists.
