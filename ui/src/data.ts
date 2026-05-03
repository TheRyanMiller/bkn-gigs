import type { Event, ScrapeStatus, VenueStatus } from "./types";

const R2_PUBLIC_URL = (
  import.meta.env.VITE_R2_PUBLIC_URL || "https://pub-756023fa49674586a44105ba7bf52137.r2.dev"
).replace(/\/$/, "");
const R2_PUBLIC_PREFIX = (import.meta.env.VITE_R2_PUBLIC_PREFIX || "apps/bkn-gigs/prod/public").replace(
  /^\/|\/$/g,
  ""
);

type BrooklynVenueStatus = {
  venue: string;
  status: "ok" | "error";
  count: number;
  message: string | null;
  scraped_at: string;
};

type BrooklynScrapeStatus = {
  app?: string;
  scraped_at?: string;
  total_events?: number;
  previous_total_events?: number;
  venues?: BrooklynVenueStatus[];
};

export function publicDataUrl(file: string, cacheKey?: string) {
  const url = `${R2_PUBLIC_URL}/${R2_PUBLIC_PREFIX}/${file}`;
  return cacheKey ? `${url}?v=${encodeURIComponent(cacheKey)}` : url;
}

async function fetchJson<T>(urls: string[], fallback: T): Promise<T> {
  for (const url of urls) {
    try {
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) {
        continue;
      }
      return (await response.json()) as T;
    } catch {
      continue;
    }
  }
  return fallback;
}

function eventSlug(event: Partial<Event>, index: number) {
  if (event.slug) {
    return event.slug;
  }
  const artist = event.artists?.[0]?.name || "event";
  return `${event.date || "date"}-${event.venue || "venue"}-${artist}-${index}`
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function normalizeEvent(event: Partial<Event>, index: number): Event | null {
  if (!event.venue || !event.date || !event.artists?.length || !event.ticket_url || !event.category) {
    return null;
  }
  return {
    ...event,
    slug: eventSlug(event, index),
    venue: event.venue,
    date: event.date,
    doors_time: event.doors_time ?? null,
    show_time: event.show_time ?? null,
    artists: event.artists,
    ticket_url: event.ticket_url,
    category: event.category,
  };
}

function normalizeStatus(raw: BrooklynScrapeStatus | ScrapeStatus | null): ScrapeStatus | null {
  if (!raw) {
    return null;
  }
  if ("all_success" in raw && "any_success" in raw && !Array.isArray(raw.venues)) {
    return raw as ScrapeStatus;
  }

  const brooklynStatus = raw as BrooklynScrapeStatus;
  const scrapedAt = brooklynStatus.scraped_at || new Date().toISOString();
  const venueRows = Array.isArray(brooklynStatus.venues) ? brooklynStatus.venues : [];
  const venues = venueRows.reduce<Record<string, VenueStatus>>((next, venue) => {
    const success = venue.status === "ok";
    next[venue.venue] = {
      last_run: venue.scraped_at,
      success,
      event_count: venue.count,
      error: success ? null : venue.message,
      last_success: success ? venue.scraped_at : undefined,
      last_success_count: success ? venue.count : undefined,
    };
    return next;
  }, {});

  const statuses = Object.values(venues);
  return {
    last_run: scrapedAt,
    all_success: statuses.length > 0 ? statuses.every((venue) => venue.success) : true,
    any_success: statuses.some((venue) => venue.success),
    total_events: brooklynStatus.total_events || 0,
    venues,
  };
}

export async function loadStatus(): Promise<ScrapeStatus | null> {
  const status = await fetchJson<BrooklynScrapeStatus | ScrapeStatus | null>(
    [publicDataUrl("scrape-status.json", Date.now().toString()), "/events/scrape-status.json"],
    null
  );
  return normalizeStatus(status);
}

export async function loadEvents(cacheKey?: string): Promise<Event[]> {
  const events = await fetchJson<Array<Partial<Event>>>(
    [publicDataUrl("events.json", cacheKey), "/events/events.json"],
    []
  );
  return events.map(normalizeEvent).filter((event): event is Event => Boolean(event));
}
