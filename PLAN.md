# BKN Gigs Plan

This repository is a sibling fork of ATL Gigs, copied from `/Users/wavey/code/atl-music` on May 3, 2026. Treat `../atl-music` as the implementation reference while this repo becomes Brooklyn-specific.

## Goals

- Build a Brooklyn event aggregator focused on live music, especially indie rock, and comedy.
- Preserve the proven ATL scraper pipeline, event schema, enrichment, and frontend filtering model.
- Replace Atlanta venue coverage with Brooklyn venue coverage.
- Keep scraper docs complete so future venue maintenance is straightforward.

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

## Phase 1: Bootstrap And Rename

- Initialize this sibling repo as a fresh git repository.
- Keep the initial copy close to `../atl-music` for easy diffing.
- Update project docs from ATL Gigs to BKN Gigs.
- Rename user-facing ATL branding in `README.md`, frontend metadata, headers, OG tags, generated image assets, and deployment config.
- Decide whether to rename the frontend folder from `atl-gigs/` to `bkn-gigs/`. The folder name can remain temporarily if renaming creates unnecessary churn.

Reference files:

- `../atl-music/README.md`
- `../atl-music/atl-gigs/src/App.tsx`
- `../atl-music/atl-gigs/src/types.ts`
- `../atl-music/atl-gigs/api/og.ts`

## Phase 2: Source Discovery

For each venue, document the best source before implementing code:

- Check upstream ticketing links first: Ticketmaster, Live Nation, AXS, Eventbrite, DICE, See Tickets.
- Inspect network requests for JSON/GraphQL APIs.
- Compare event count against visible calendar pages.
- Avoid JSON-LD unless it matches the full calendar.
- Record source notes in `scrapers/{venue-slug}.md`.

Reference files:

- `../atl-music/scrapers/live-nation.md`
- `../atl-music/scrapers/terminal-west.md`
- `../atl-music/scrapers/fox-theatre.md`

## Phase 3: Implement Shared Source Scrapers

Implement source groups before one-off venue scrapers:

1. Bowery/AXS scraper for Brooklyn Steel and Music Hall of Williamsburg.
2. Ticketmaster/Live Nation scraper entries for The Bell House, Warsaw, Brooklyn Paramount, and possibly Brooklyn Bowl.
3. Eventbrite scraper support for Union Hall and Brooklyn Comedy Collective if API or embedded JSON is practical.
4. See Tickets scraper support for Baby's All Right.
5. DICE scraper support for Union Pool if a stable public source is available.
6. Venue-specific scrapers for Elsewhere, Littlefield, Market Hotel, The Sultan Room, and C'mon Everybody.

Reference files:

- `../atl-music/scraper/tm.py`
- `../atl-music/scraper/venues/live_nation.py`
- `../atl-music/scraper/venues/aeg.py`
- `../atl-music/scraper/registry.py`

## Phase 4: Category And Enrichment Behavior

- Keep the existing category set: `concerts`, `comedy`, `broadway`, `sports`, `misc`.
- Default music-first rooms to `concerts`.
- Use Ticketmaster classifications when available.
- Use text detection for mixed calendars and comedy-heavy venues.
- Keep Spotify enrichment for music artists, but avoid doing Spotify lookups for obvious comedy event titles where possible.

Reference files:

- `../atl-music/scraper/utils/categories.py`
- `../atl-music/scraper/spotify_enrichment.py`
- `../atl-music/scraper/tm.py`

## Phase 5: Frontend Brooklynization

- Change site name, copy, metadata, OG tags, default images, and generated assets from ATL Gigs to BKN Gigs.
- Review filters and labels for Brooklyn usage.
- Keep the existing event modal, slug routes, first-seen tracking, and category UX unless there is a clear Brooklyn-specific need.
- Update Vercel and workflow configuration after deployment target is known.

Reference files:

- `../atl-music/atl-gigs/src/`
- `../atl-music/atl-gigs/api/`
- `../atl-music/.github/workflows/scrape.yml`

## Phase 6: Testing And Launch

- Add focused unit tests for reusable source parsers.
- Run individual scraper checks as each venue lands.
- Run `python scrape.py` with available API keys.
- Run frontend lint, tests, and production build.
- Confirm generated event JSON is valid and categories render correctly.
- Create a launch checklist for domain, Vercel project, secrets, GitHub Actions schedule, and cache/R2 behavior.

## Current Status

- Sibling working copy created at `/Users/wavey/code/bkn-gigs`.
- Local secrets, git metadata, virtualenvs, `node_modules`, build output, and caches were not copied.
- Initial Brooklyn-specific `AGENTS.md` and `PLAN.md` have been added.
