import { fireEvent, render, screen } from "@testing-library/react";
import EventCard from "./EventCard";
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

const renderWithProviders = (event: Event, onClick = vi.fn()) => {
  render(
    <FavoritesProvider>
      <EventCard event={event} onClick={onClick} />
    </FavoritesProvider>
  );
  return onClick;
};

test("keeps the primary Spotify link in the compact row", () => {
  renderWithProviders(baseEvent);
  expect(screen.getAllByLabelText("Open Spotify artist")).toHaveLength(1);
});

test("hides the Spotify link when spotify_url is missing", () => {
  const event = { ...baseEvent, artists: [{ name: "No Link" }] };
  renderWithProviders(event);
  expect(screen.queryByLabelText("Open Spotify artist")).toBeNull();
});

test("shows show time before doors time", () => {
  renderWithProviders(baseEvent);
  expect(screen.getByText("8:00 PM")).toBeInTheDocument();
  expect(screen.queryByText("Doors 7:00 PM")).toBeNull();
});

test("falls back to a labeled doors time", () => {
  renderWithProviders({ ...baseEvent, show_time: null });
  expect(screen.getByText("Doors 7:00 PM")).toBeInTheDocument();
});

test("opens event details from the row button", () => {
  const onClick = renderWithProviders(baseEvent);
  const rowButton = screen.getByRole("button", { name: "View Sample Band at Brooklyn Steel" });
  rowButton.focus();
  expect(rowButton).toHaveFocus();
  fireEvent.click(rowButton);
  expect(onClick).toHaveBeenCalledOnce();
});

test("keeps nested actions separate from row selection", () => {
  const onClick = renderWithProviders(baseEvent);
  fireEvent.click(screen.getByRole("button", { name: "Add Sample Band to favorites" }));
  expect(onClick).not.toHaveBeenCalled();
});
