import { fireEvent, render, screen } from "@testing-library/react";
import EventModal from "./EventModal";
import { FavoritesProvider } from "../context/FavoritesContext";
import { Event } from "../types";

const baseEvent: Event = {
  slug: "2026-02-10-brooklyn-steel-sample-band",
  venue: "Brooklyn Steel",
  date: "2026-02-10",
  doors_time: "19:00",
  show_time: "20:00",
  artists: [
    { name: "Sample Band", spotify_url: "https://open.spotify.com/artist/AAA" },
    { name: "Opening Act", spotify_url: "https://open.spotify.com/artist/BBB" },
  ],
  price: "$20",
  ticket_url: "https://example.com/tickets",
  category: "concerts",
};

const renderWithProviders = (event: Event, onClose = vi.fn()) => {
  render(
    <FavoritesProvider>
      <EventModal event={event} onClose={onClose} />
    </FavoritesProvider>
  );
  return onClose;
};


test("shows Spotify icons in modal when spotify_url is present", () => {
  renderWithProviders(baseEvent);
  const icons = screen.getAllByLabelText("Open Spotify artist");
  expect(icons.length).toBe(2);
});

test("hides Spotify icons in modal when spotify_url is missing", () => {
  const event = { ...baseEvent, artists: [{ name: "No Link" }] };
  renderWithProviders(event);
  expect(screen.queryByLabelText("Open Spotify artist")).toBeNull();
});

test("shows event description in modal when present", () => {
  const event = {
    ...baseEvent,
    description: "A detailed artist biography for this show.",
  };

  renderWithProviders(event);

  expect(screen.getByText("About")).toBeInTheDocument();
  expect(screen.getByText("A detailed artist biography for this show.")).toBeInTheDocument();
});

test("hides event description section when absent", () => {
  renderWithProviders(baseEvent);
  expect(screen.queryByText("About")).toBeNull();
});

test("provides an explicit close action", () => {
  const onClose = renderWithProviders(baseEvent);
  fireEvent.click(screen.getByRole("button", { name: "Close event details" }));
  expect(onClose).toHaveBeenCalledOnce();
});

test("shows a show time when doors time is unavailable", () => {
  renderWithProviders({ ...baseEvent, doors_time: null });
  expect(screen.getByText("Show 8:00 PM")).toBeInTheDocument();
});
