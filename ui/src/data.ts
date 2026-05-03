import type { GigEvent, ScrapeStatus } from "./types";

const R2_PUBLIC_URL = (import.meta.env.VITE_R2_PUBLIC_URL || "https://pub-756023fa49674586a44105ba7bf52137.r2.dev").replace(/\/$/, "");
const R2_PUBLIC_PREFIX = (import.meta.env.VITE_R2_PUBLIC_PREFIX || "apps/bkn-gigs/prod/public").replace(/^\/|\/$/g, "");

export function publicDataUrl(file: string) {
  return `${R2_PUBLIC_URL}/${R2_PUBLIC_PREFIX}/${file}`;
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

export async function loadEvents(): Promise<GigEvent[]> {
  const events = await fetchJson<GigEvent[]>([publicDataUrl("events.json"), "/events/events.json"], []);
  return events.filter((event) => event.venue && event.date && event.artists?.length && event.ticket_url);
}

export async function loadStatus(): Promise<ScrapeStatus | null> {
  return fetchJson<ScrapeStatus | null>([publicDataUrl("scrape-status.json"), "/events/scrape-status.json"], null);
}
