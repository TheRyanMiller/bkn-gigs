# Brooklyn Paramount

## Scraping approach

Brooklyn Paramount is scraped from the Live Nation content API with venue id `KovZpZA77ldA`.

## Category mappings

Live Nation segment and genre values are used first, then shared text detection.

## Edge cases

Large rooms can include sports, comedy, and theater-adjacent programming. The category pipeline does not assume every Paramount event is a concert.

## Opinionated decisions

The API is used instead of page scraping because it provides a venue-scoped paginated event feed with stable event URLs and images.
