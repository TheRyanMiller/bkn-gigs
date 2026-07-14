import { useMemo } from "react";
import { Link } from "react-router-dom";
import { Loader2, Star } from "lucide-react";
import { Event } from "../types";
import EventCard from "../components/EventCard";
import { useFavorites } from "../context/FavoritesContext";

interface FavoritesProps {
  events: Event[];
  loading: boolean;
  onEventClick: (event: Event) => void;
}

const getTodayString = () =>
  new Date().toLocaleDateString("en-CA", { timeZone: "America/New_York" });

export default function Favorites({ events, loading, onEventClick }: FavoritesProps) {
  const { favorites, favoriteCount, clearFavorites } = useFavorites();

  const favoriteEvents = useMemo(() => {
    const today = getTodayString();
    return events
      .filter((event) => favorites.has(event.slug) && event.date >= today)
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [events, favorites]);

  return (
    <div className="mx-auto w-full max-w-6xl px-3 py-5 sm:px-4 sm:py-6">
      <div className="mb-4 flex items-center justify-between border-b border-neutral-900 pb-4">
        <div className="flex items-center gap-2.5">
          <Star size={17} className="fill-yellow-400 text-yellow-400" />
          <h1 className="text-lg font-semibold text-white">Favorites</h1>
          <span className="text-sm text-neutral-500">{favoriteCount}</span>
        </div>

        {favoriteCount > 0 && (
          <button
            type="button"
            onClick={clearFavorites}
            className="rounded-md px-2 py-1 text-xs text-neutral-500 transition-colors hover:bg-neutral-900 hover:text-red-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-2">
        {favoriteEvents.map((event) => (
          <EventCard
            key={event.slug}
            event={event}
            onClick={() => onEventClick(event)}
          />
        ))}

        {loading && (
          <div className="py-20 text-center">
            <Loader2 size={28} className="mx-auto animate-spin text-fuchsia-400" />
          </div>
        )}

        {!loading && favoriteEvents.length === 0 && (
          <div className="rounded-lg border border-dashed border-neutral-800 bg-neutral-900/30 py-14 text-center">
            <Star size={28} className="mx-auto mb-3 text-neutral-700" />
            <h3 className="text-base font-semibold text-white">No favorites yet</h3>
            <p className="mx-auto mt-1 max-w-sm text-sm text-neutral-500">
              Save events to keep a short list of gigs you want to see.
            </p>
            <Link
              to="/"
              className="mt-5 inline-flex h-9 items-center rounded-md bg-fuchsia-600 px-4 text-xs font-semibold text-white transition-colors hover:bg-fuchsia-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300"
            >
              Browse events
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
