# Agent Instructions for BKN Gigs

BKN Gigs is a Brooklyn event aggregator forked from ATL Gigs. The source reference repository is:

`/Users/wavey/code/atl-music`

Use that repo as the canonical reference for architecture, scraper patterns, validation, pipeline behavior, and frontend conventions. Do not modify `../atl-music` unless the user explicitly asks; compare against it when porting or checking existing behavior.

## Project Overview

This repository has the same starting architecture as ATL Gigs:

1. **Python scraper** (`scrape.py`, logic in `scraper/`): Fetches events from venue websites and ticketing APIs.
2. **React frontend** (`atl-gigs/` for now): Displays events with filtering.

Events flow:

`Venue APIs/Websites -> scraper/ -> scrape.py -> events.json -> React app -> Vercel`

The frontend directory is still named `atl-gigs/` in the initial copy. Rename or reorganize it only as part of an explicit Brooklynization pass.

## Git Workflow

- Make a commit for each meaningful change.
- Use clean, imperative commit messages, for example `Bootstrap Brooklyn gigs repository` or `Add Brooklyn Steel scraper`.
- Do not commit secrets, local generated event JSON, virtualenvs, `node_modules`, build output, or caches.
- Preserve user changes in a dirty worktree. Never revert unrelated edits unless explicitly asked.

## Reference Paths From ATL Gigs

When implementing Brooklyn changes, start with these files in `../atl-music`:

- `scraper/registry.py` - scraper registration and Ticketmaster fallback pattern.
- `scraper/tm.py` - Ticketmaster venue and artist classification integration.
- `scraper/venues/live_nation.py` - Live Nation GraphQL scraper pattern.
- `scraper/venues/aeg.py` - Bowery/AEG-style event page scraping pattern.
- `scraper/utils/categories.py` - category detection helpers.
- `scraper/pipeline/validate.py` - event schema validation.
- `scrapers/*.md` - documentation style for venue scrapers.
- `atl-gigs/src/types.ts` and `atl-gigs/api/og.ts` - frontend category and OG metadata behavior.

## Event Schema

Every scraper must return events matching this structure:

```python
{
    "venue": str,
    "date": str,               # "YYYY-MM-DD"
    "doors_time": str | None,  # "HH:MM" 24-hour
    "show_time": str | None,   # "HH:MM" 24-hour
    "artists": [
        {"name": str, "genre": str | None, "spotify_url": str | None}
    ],
    "ticket_url": str,
    "info_url": str | None,
    "image_url": str | None,
    "description": str | None,
    "price": str | None,
    "category": str,           # concerts, comedy, broadway, sports, misc
}
```

Required fields:

- `venue`
- `date`
- `artists` with at least one performer/title
- `ticket_url`
- `category`

## Categories

Use the existing category set unless the user explicitly asks to add more:

- `concerts` - Music performances. This is the default for music-first Brooklyn venues.
- `comedy` - Stand-up, improv, sketch, comedy showcases, comedy podcasts.
- `broadway` - Theater, musicals, plays.
- `sports` - Sporting events.
- `misc` - Everything else.

When venue pages are mixed, prefer structured ticketing classifications first. If unavailable, use `detect_category_from_text()` and ticket URL hints from `scraper/utils/categories.py`.

## Initial Brooklyn Venue Scope

The starting Brooklyn venue list is:

- Baby's All Right
- Music Hall of Williamsburg
- Brooklyn Steel
- Warsaw
- Elsewhere
- Brooklyn Bowl
- Union Pool
- Market Hotel
- The Sultan Room
- The Bell House
- Union Hall
- Littlefield
- C'mon Everybody
- Brooklyn Comedy Collective
- Brooklyn Paramount

Known alternates for later:

- Kings Theatre
- Isola Brooklyn
- Public Records

Known exclusions for now:

- Brooklyn Made: official page says it is closed and shows are cancelled.
- Music Hall of Williamsburg is active during 2026 but should be monitored because public reporting says its current lease ends at the end of 2026.

## Scraper Source Strategy

Before writing a scraper, inspect the venue source in this order:

1. **Upstream ticketing API**: Ticketmaster, Live Nation, AXS, Eventbrite, DICE, See Tickets.
2. **Venue JSON or GraphQL API**: Network tab, `/api`, `wp-json`, embedded app data.
3. **Venue HTML**: Use only when structured sources are unavailable.

Likely starting mappings:

- Ticketmaster/Live Nation: The Bell House, Warsaw, Brooklyn Paramount, possibly Brooklyn Bowl.
- Bowery/AXS: Brooklyn Steel, Music Hall of Williamsburg.
- See Tickets: Baby's All Right.
- DICE: Union Pool and possibly other small rooms.
- Eventbrite: Union Hall, Brooklyn Comedy Collective, Isola Brooklyn if added.
- Venue-owned site/API: Elsewhere, Littlefield, Market Hotel, The Sultan Room, C'mon Everybody.

Always verify source completeness against the venue calendar. Homepages and JSON-LD often include only featured shows.

## Adding Or Modifying Scrapers

For every scraper change:

1. Inspect existing docs in `scrapers/` for similar venues.
2. Prefer reusable source-specific scrapers over one-off HTML parsing.
3. Normalize dates and times with helpers in `scraper/utils/`.
4. Return valid event dictionaries matching the schema.
5. Register the scraper in `scraper/registry.py`, or add the venue to the relevant source registry.
6. Add or update `scrapers/{venue-slug}.md`.
7. Run a focused scraper check, then `python scrape.py` when practical.

Minimum venue documentation sections:

- Scraping approach
- Category mappings
- Edge cases
- Opinionated decisions

## Verification

Useful commands:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python scrape.py
pytest

cd atl-gigs
npm install
npm run lint
npm test
npm run build
```

If a command cannot be run because credentials are missing, say so clearly and run the best available subset.
