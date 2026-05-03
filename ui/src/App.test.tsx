import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { GigEvent, ScrapeStatus } from "./types";

const events: GigEvent[] = [
  {
    venue: "Brooklyn Steel",
    date: "2026-06-01",
    doors_time: "19:00",
    show_time: "20:00",
    artists: [{ name: "Sample Band", genre: null, spotify_url: null }],
    ticket_url: "https://example.com/tickets",
    info_url: "https://example.com/info",
    image_url: null,
    description: "Indie rock show",
    price: "$20",
    category: "concerts",
    slug: "sample-band",
  },
  {
    venue: "The Bell House",
    date: "2026-06-02",
    doors_time: null,
    show_time: "21:00",
    artists: [{ name: "Sample Comic", genre: null, spotify_url: null }],
    ticket_url: "https://example.com/comedy",
    info_url: null,
    image_url: null,
    description: "Stand-up comedy",
    price: null,
    category: "comedy",
    slug: "sample-comic",
  },
];

const status: ScrapeStatus = {
  app: "bkn-gigs",
  scraped_at: "2026-05-03T12:00:00-04:00",
  total_events: 2,
  previous_total_events: 0,
  venues: [{ venue: "Brooklyn Steel", status: "ok", count: 1, message: null, scraped_at: "2026-05-03T12:00:00-04:00" }],
};

beforeEach(() => {
  let store: Record<string, string> = {};
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  });
  window.history.replaceState({}, "", "/");
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const body = url.includes("scrape-status") ? status : events;
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }),
  );
});

describe("App", () => {
  it("renders fetched events and filters by category", async () => {
    render(<App />);
    expect(await screen.findByText("Sample Band")).toBeInTheDocument();
    expect(screen.getByText("Sample Comic")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Comedy" }));
    await waitFor(() => expect(screen.queryByText("Sample Band")).not.toBeInTheDocument());
    expect(screen.getByText("Sample Comic")).toBeInTheDocument();
  });

  it("opens an event modal from a shareable event button", async () => {
    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: "Sample Band" }));
    expect(screen.getByRole("dialog", { name: "Sample Band" })).toBeInTheDocument();
    expect(window.location.search).toContain("event=sample-band");
  });
});
