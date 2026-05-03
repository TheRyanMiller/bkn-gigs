# BKN Gigs Plan

This repository is intentionally a lightweight planning scaffold at:

`/Users/wavey/code/bkn-gigs`

It is a sibling of the existing ATL project:

`/Users/wavey/code/atl-music`

The goal is to recreate the ATL Gigs concept for Brooklyn venues, not to keep a full copied ATL codebase here before implementation begins.

## Current Status

- Keep this repo mostly empty for now.
- Tracked planning files should be limited to `AGENTS.md` and `PLAN.md`.
- Use `../atl-music` as the reference implementation when the rebuild starts.
- Do not copy ATL source wholesale into this repo unless explicitly requested.

## Product Goal

Build a Brooklyn event aggregator focused on:

- Live music, especially indie rock and adjacent touring acts.
- Comedy, including stand-up, sketch, alt comedy, and local showcases.
- A similar user experience to ATL Gigs: searchable/filterable event listings, event detail modals, favorites, shareable event links, and scraper status visibility.

## Shared Data Store Layout

BKN Gigs should use the same Cloudflare R2 store as ATL Gigs, but app-specific data must be isolated by namespace.

```text
apps/
  bkn-gigs/
    prod/
      public/
        events.json
        scrape-status.json
      state/
        seen-cache.json
        scrape-log.txt
shared/
  artist-cache.json
  artist-spotify-cache.json
```

Rules:

- Brooklyn public data lives under `apps/bkn-gigs/prod/public/`.
- Brooklyn scrape state lives under `apps/bkn-gigs/prod/state/`.
- Never use shared flat keys like `events.json`, `seen-cache.json`, or `scrape-status.json`.
- Never read ATL app event data from BKN.
- Artist enrichment caches can be shared under `shared/` because they are not venue/event history.

Planned environment defaults:

```text
APP_SLUG=bkn-gigs
APP_ENV=prod
R2_KEY_PREFIX=apps/bkn-gigs/prod
R2_PUBLIC_PREFIX=apps/bkn-gigs/prod/public
R2_STATE_PREFIX=apps/bkn-gigs/prod/state
R2_SHARED_PREFIX=shared
R2_SHARE_ARTIST_CACHES=true
```

## Initial Venue List

Primary seed venues:

| Venue | Why Include | Expected Source |
|---|---|---|
| Baby's All Right | Small Williamsburg indie room | See Tickets calendar |
| Music Hall of Williamsburg | Core Bowery indie venue, active through 2026 | Bowery/AXS |
| Brooklyn Steel | Larger indie/alt touring room | Bowery/AXS |
| Warsaw | Greenpoint punk/indie/rock | Live Nation/Ticketmaster |
| Elsewhere | Bushwick multi-room live/club venue | Venue site/API |
| Brooklyn Bowl | Live music plus broader event programming | Website/Ticketmaster |
| Union Pool | Small indie/local rock room | DICE |
| Market Hotel | Bushwick DIY/indie/nightlife | Venue calendar |
| The Sultan Room | Intimate Bushwick live music room | Venue calendar/ticket links |
| The Bell House | Comedy-forward plus music | Live Nation/Ticketmaster |
| Union Hall | Park Slope comedy and music | Eventbrite/Union Hall |
| Littlefield | Gowanus comedy, music, podcasts, art | Venue calendar |
| C'mon Everybody | Bed-Stuy music/live arts/queer nightlife | Venue events |
| Brooklyn Comedy Collective | High-volume local comedy | Eventbrite |
| Brooklyn Paramount | Larger concerts with indie/alt crossover | Live Nation/Ticketmaster |

Later candidates:

- Kings Theatre for larger concerts and comedy.
- Isola Brooklyn for comedy/music if event source proves stable.
- Public Records for experimental/electronic programming.

Do not seed Brooklyn Made now. Its official page says it is closed and shows are cancelled.

## Phase 1: Source Discovery

For each venue:

- Check upstream ticketing first: Ticketmaster, Live Nation, AXS, Eventbrite, DICE, See Tickets.
- Inspect network requests for JSON or GraphQL APIs.
- Compare API event count against the visible calendar.
- Avoid JSON-LD unless it represents the full event list.
- Record source notes before writing scraper code.

Reference from ATL:

- `../atl-music/scrapers/live-nation.md`
- `../atl-music/scrapers/terminal-west.md`
- `../atl-music/scrapers/fox-theatre.md`

## Phase 2: Recreate Core Scraper App

Create only the files needed for the Brooklyn scraper:

- Python package structure under `scraper/`.
- `scrape.py` entrypoint.
- Validation, merge, R2, and utility modules based on ATL behavior.
- Brooklyn-specific venue registry.
- Venue docs under `scrapers/`.

Reference from ATL:

- `../atl-music/scrape.py`
- `../atl-music/scraper/pipeline/`
- `../atl-music/scraper/utils/`
- `../atl-music/scraper/registry.py`

## Phase 3: Implement Venue Scrapers

Implement source groups before one-off scrapers:

1. Bowery/AXS: Brooklyn Steel and Music Hall of Williamsburg.
2. Ticketmaster/Live Nation: The Bell House, Warsaw, Brooklyn Paramount, possibly Brooklyn Bowl.
3. Eventbrite: Union Hall and Brooklyn Comedy Collective if practical.
4. See Tickets: Baby's All Right.
5. DICE: Union Pool if a stable source exists.
6. Venue-specific sources: Elsewhere, Littlefield, Market Hotel, The Sultan Room, C'mon Everybody.

Each scraper must have `scrapers/{venue-slug}.md` documentation.

## Phase 4: Recreate Frontend

After scraper output is stable, recreate the frontend deliberately:

- Use ATL Gigs frontend behavior as a reference.
- Use Brooklyn naming and metadata from the start.
- Read data from `apps/bkn-gigs/prod/public/events.json`.
- Keep filters, event modals, favorites, status modal, and share links unless a Brooklyn-specific change is needed.

Reference from ATL:

- `../atl-music/atl-gigs/src/`
- `../atl-music/atl-gigs/api/`
- `../atl-music/atl-gigs/vercel.json`

## Phase 5: Automation And Launch

- Add GitHub Actions scrape workflow after scraper paths exist.
- Configure Cloudflare R2 secrets and app-scoped paths.
- Configure Vercel project and site URL.
- Run scraper tests, full scrape, frontend tests, and production build.
- Confirm Brooklyn data does not merge with ATL data.

## Open Decisions

- Final frontend folder name: likely `bkn-gigs/`, but decide when implementation begins.
- Final public domain and Vercel project name.
- Whether ATL should also migrate from flat R2 root keys to `apps/atl-gigs/prod/`.
