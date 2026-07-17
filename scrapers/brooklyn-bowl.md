# Brooklyn Bowl

## Scraping approach

Brooklyn Bowl events are parsed from the server-rendered `/brooklyn/shows/all` listing. This uses one normal page request instead of repeated calendar API calls, which are rejected on some hosted runners.

## Category mappings

Concerts are the default, with shared keyword detection applied to titles and support text.

## Edge cases

The listing includes closure notices and gift cards, which are excluded. Venue labels are checked so events from other Brooklyn Bowl locations cannot leak into the feed.

## Opinionated decisions

The external ticket button is preferred for `ticket_url`; the Brooklyn Bowl detail page is retained as `info_url` and used as the ticket fallback when necessary.
