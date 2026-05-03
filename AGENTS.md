# Agent Instructions for BKN Gigs

BKN Gigs is a planning scaffold for a future Brooklyn event aggregator. It is intentionally a sibling directory to ATL Gigs, not a copy of the ATL source tree.

Reference repository:

`/Users/wavey/code/atl-music`

Current repository:

`/Users/wavey/code/bkn-gigs`

Do not modify `../atl-music` unless the user explicitly asks. Use it as the implementation reference when creating the Brooklyn version.

## Current State

This repo should stay mostly empty until implementation begins. The intended tracked files right now are:

- `AGENTS.md`
- `PLAN.md`

Do not add scraper/frontend/source files until the user asks to begin implementation.

## Git Workflow

- Make a commit for each meaningful change.
- Use clean, imperative commit messages.
- Keep the repo lightweight while it is in planning mode.
- Do not copy the ATL project wholesale into this repo without explicit permission.
- When implementation starts, add files intentionally and in small phases.

## ATL Reference Paths

When recreating the app for Brooklyn, use these ATL files as references:

- `../atl-music/scrape.py` - scraper entrypoint and event pipeline flow.
- `../atl-music/scraper/registry.py` - scraper registration and fallback pattern.
- `../atl-music/scraper/tm.py` - Ticketmaster integration and enrichment.
- `../atl-music/scraper/venues/live_nation.py` - Live Nation GraphQL scraper pattern.
- `../atl-music/scraper/venues/aeg.py` - reusable venue event parsing pattern.
- `../atl-music/scraper/utils/` - date, category, event, and description helpers.
- `../atl-music/scraper/pipeline/` - validation, merge, R2, metrics, and IO behavior.
- `../atl-music/scrapers/*.md` - venue documentation examples.
- `../atl-music/atl-gigs/src/` - frontend components and filtering UX.
- `../atl-music/atl-gigs/api/` - Vercel OG endpoints.
- `../atl-music/.github/workflows/scrape.yml` - scheduled scrape automation.

## Future Event Schema

When implementation begins, every Brooklyn scraper should return events matching the ATL schema:

```python
{
    "venue": str,
    "date": str,
    "doors_time": str | None,
    "show_time": str | None,
    "artists": [
        {"name": str, "genre": str | None, "spotify_url": str | None}
    ],
    "ticket_url": str,
    "info_url": str | None,
    "image_url": str | None,
    "description": str | None,
    "price": str | None,
    "category": str,
}
```

Required fields:

- `venue`
- `date`
- `artists` with at least one item
- `ticket_url`
- `category`

Allowed categories:

- `concerts`
- `comedy`
- `broadway`
- `sports`
- `misc`

## Shared Data Store Plan

BKN Gigs should eventually use the same Cloudflare R2 store as ATL Gigs, but all app-specific files must be namespaced.

Brooklyn app data:

```text
apps/bkn-gigs/prod/public/events.json
apps/bkn-gigs/prod/public/scrape-status.json
apps/bkn-gigs/prod/state/seen-cache.json
apps/bkn-gigs/prod/state/scrape-log.txt
```

Shared enrichment caches:

```text
shared/artist-cache.json
shared/artist-spotify-cache.json
```

Isolation rules:

- Do not read or write flat root R2 keys such as `events.json` or `seen-cache.json`.
- Do not read or write ATL app keys such as `apps/atl-gigs/prod/public/events.json`.
- `artist-cache.json` and `artist-spotify-cache.json` may be shared because they are artist enrichment caches, not event history.

## Initial Brooklyn Venue Scope

Seed venues:

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

Later candidates:

- Kings Theatre
- Isola Brooklyn
- Public Records

Known exclusions for now:

- Brooklyn Made: official page says it is closed and shows are cancelled.
- Music Hall of Williamsburg is active during 2026 but should be monitored because public reporting says its current lease ends at the end of 2026.

## Implementation Guidance

When the user asks to build the app:

1. Recreate the project structure deliberately from ATL patterns.
2. Start with scraper source discovery and venue docs before code.
3. Prefer source-specific reusable scrapers over one-off HTML parsing.
4. Add frontend files only after the scraper/pipeline shape is clear.
5. Keep Brooklyn-specific naming, data paths, and venue docs from the beginning.
