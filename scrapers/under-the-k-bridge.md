# Under the K Bridge

## Scraping approach

The venue publishes an official AEG event feed at `https://aegwebprod.blob.core.windows.net/json/events/360/events.json`. The shared AEG transformer reads event dates, doors and show times, headliners, support, AXS links, images, descriptions, and available price ranges.

## Category mappings

The official concert series is mapped to `concerts`.

## Edge cases

Private, inactive, and unpublished records are ignored. AEG uses `$0` when prices are unavailable, so those placeholders are omitted. The venue is seasonal and may validly return no future events.

## Opinionated decisions

The structured AEG feed is preferred over scraping AXS pages or the visual calendar.
