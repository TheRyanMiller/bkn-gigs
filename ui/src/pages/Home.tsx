import { useState, useMemo, useCallback, useEffect, useRef } from "react";
import { FixedSizeList as List } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import { Loader2, Music } from "lucide-react";
import { Event, EventCategory, ALL_CATEGORIES } from "../types";
import EventCard from "../components/EventCard";
import FilterBar from "../components/FilterBar";

interface HomeProps {
  events: Event[];
  loading: boolean;
  onEventClick: (event: Event) => void;
}

interface DateRange {
  start: string | null;
  end: string | null;
}

const CARD_HEIGHT = 120;
const ROW_HEIGHT = 128;

const getTodayString = () =>
  new Date().toLocaleDateString("en-CA", { timeZone: "America/New_York" });

export default function Home({ events, loading, onEventClick }: HomeProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedVenues, setSelectedVenues] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<EventCategory[]>([]);
  const [dateRange, setDateRange] = useState<DateRange>({ start: null, end: null });
  const [showOnlyNew, setShowOnlyNew] = useState(false);
  const listRef = useRef<List>(null);

  const venues = useMemo(
    () => Array.from(new Set(events.map((event) => event.venue))).sort(),
    [events]
  );

  const categories = useMemo(() => {
    const eventCategories = new Set(events.map((event) => event.category));
    return ALL_CATEGORIES.filter((category) => eventCategories.has(category));
  }, [events]);

  const filteredEvents = useMemo(() => {
    const today = getTodayString();
    const now = new Date();
    const staleThresholdMs = 3 * 24 * 60 * 60 * 1000;

    return events.filter((event) => {
      if (event.last_seen && now.getTime() - new Date(event.last_seen).getTime() > staleThresholdMs) {
        return false;
      }
      if (!dateRange.start && event.date < today) return false;
      if (dateRange.start && event.date < dateRange.start) return false;
      if (dateRange.end && event.date > dateRange.end) return false;
      if (selectedCategories.length > 0 && !selectedCategories.includes(event.category)) return false;
      if (selectedVenues.length > 0 && !selectedVenues.includes(event.venue)) return false;
      if (showOnlyNew && !event.is_new) return false;

      if (searchQuery.length >= 3) {
        const query = searchQuery.toLowerCase();
        return (
          event.artists.some((artist) => artist.name.toLowerCase().includes(query)) ||
          event.venue.toLowerCase().includes(query)
        );
      }
      return true;
    });
  }, [events, searchQuery, selectedCategories, selectedVenues, dateRange, showOnlyNew]);

  useEffect(() => {
    listRef.current?.scrollTo(0);
  }, [searchQuery, selectedCategories, selectedVenues, dateRange, showOnlyNew]);

  const handleCategoryToggle = useCallback((category: EventCategory) => {
    setSelectedCategories((current) =>
      current.includes(category) ? current.filter((item) => item !== category) : [...current, category]
    );
  }, []);

  const handleVenueToggle = useCallback((venue: string) => {
    setSelectedVenues((current) =>
      current.includes(venue) ? current.filter((item) => item !== venue) : [...current, venue]
    );
  }, []);

  const Row = useCallback(
    ({ index, style }: { index: number; style: React.CSSProperties }) => {
      const event = filteredEvents[index];
      return (
        <div style={style}>
          <div
            className="mx-auto w-full max-w-6xl px-3 sm:px-4"
            style={{ height: ROW_HEIGHT, paddingBottom: ROW_HEIGHT - CARD_HEIGHT }}
          >
            <EventCard event={event} onClick={() => onEventClick(event)} />
          </div>
        </div>
      );
    },
    [filteredEvents, onEventClick]
  );

  return (
    <div className="flex h-[calc(100dvh-56px)] flex-col md:h-[calc(100dvh-64px)]">
      <div className="shrink-0 border-b border-neutral-900 bg-neutral-950 py-2">
        <div className="mx-auto w-full max-w-6xl px-3 sm:px-4">
          <FilterBar
            venues={venues}
            selectedVenues={selectedVenues}
            onVenueToggle={handleVenueToggle}
            categories={categories}
            selectedCategories={selectedCategories}
            onCategoryToggle={handleCategoryToggle}
            onSearchChange={setSearchQuery}
            onDateRangeChange={setDateRange}
            showOnlyNew={showOnlyNew}
            onShowOnlyNewToggle={() => setShowOnlyNew((current) => !current)}
            resultCount={filteredEvents.length}
            totalCount={events.length}
          />
        </div>
      </div>

      <div className="min-h-0 flex-1 py-2">
        {loading && (
          <div className="py-20 text-center">
            <Loader2 size={28} className="mx-auto animate-spin text-fuchsia-400" />
          </div>
        )}

        {!loading && filteredEvents.length === 0 && (
          <div className="mx-auto mt-6 w-full max-w-6xl px-3 sm:px-4">
            <div className="rounded-lg border border-dashed border-neutral-800 bg-neutral-900/30 py-14 text-center">
              <Music size={28} className="mx-auto mb-3 text-neutral-700" />
              <h3 className="text-base font-semibold text-white">No gigs found</h3>
              <p className="mt-1 text-sm text-neutral-500">Try adjusting your search or filters.</p>
            </div>
          </div>
        )}

        {!loading && filteredEvents.length > 0 && (
          <AutoSizer>
            {({ height, width }) => (
              <List
                ref={listRef}
                height={height}
                width={width}
                itemCount={filteredEvents.length}
                itemSize={ROW_HEIGHT}
                overscanCount={5}
              >
                {Row}
              </List>
            )}
          </AutoSizer>
        )}
      </div>
    </div>
  );
}
