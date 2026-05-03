import { useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  Clock3,
  ExternalLink,
  Heart,
  Info,
  ListFilter,
  MapPin,
  Search,
  Share2,
  Ticket,
  X,
} from "lucide-react";
import { loadEvents, loadStatus } from "./data";
import type { Category, GigEvent, ScrapeStatus } from "./types";

type CategoryFilter = Category | "all";

const CATEGORY_OPTIONS: Array<{ id: CategoryFilter; label: string }> = [
  { id: "all", label: "All" },
  { id: "concerts", label: "Concerts" },
  { id: "comedy", label: "Comedy" },
  { id: "broadway", label: "Theater" },
  { id: "sports", label: "Sports" },
  { id: "misc", label: "Misc" },
];

function eventKey(event: GigEvent) {
  return event.slug || `${event.date}-${event.venue}-${event.artists[0]?.name || "event"}`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(new Date(`${value}T12:00:00`));
}

function formatTime(value: string | null) {
  if (!value) {
    return null;
  }
  const [hour, minute] = value.split(":").map(Number);
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(2026, 0, 1, hour, minute));
}

function artistLine(event: GigEvent) {
  return event.artists.map((artist) => artist.name).join(" + ");
}

function shareUrl(event: GigEvent) {
  const url = new URL(window.location.href);
  url.searchParams.set("event", eventKey(event));
  return url.toString();
}

function EventCard({
  event,
  favorite,
  onOpen,
  onFavorite,
  onShare,
}: {
  event: GigEvent;
  favorite: boolean;
  onOpen: (event: GigEvent) => void;
  onFavorite: (event: GigEvent) => void;
  onShare: (event: GigEvent) => void;
}) {
  const time = formatTime(event.show_time) || formatTime(event.doors_time);
  return (
    <article className="event-card">
      <div className="event-date" aria-label={event.date}>
        <span>{formatDate(event.date).split(" ")[0]}</span>
        <strong>{formatDate(event.date).replace(/^\w+ /, "")}</strong>
      </div>
      <div className="event-main">
        <button className="event-title" type="button" onClick={() => onOpen(event)}>
          {artistLine(event)}
        </button>
        <div className="event-meta">
          <span>
            <MapPin size={15} aria-hidden="true" />
            {event.venue}
          </span>
          {time ? (
            <span>
              <Clock3 size={15} aria-hidden="true" />
              {time}
            </span>
          ) : null}
          {event.price ? <span>{event.price}</span> : null}
        </div>
      </div>
      <div className="event-actions">
        {event.is_new ? <span className="new-badge">New</span> : null}
        <button className="icon-button" type="button" aria-label={`Favorite ${artistLine(event)}`} aria-pressed={favorite} onClick={() => onFavorite(event)}>
          <Heart size={18} fill={favorite ? "currentColor" : "none"} aria-hidden="true" />
        </button>
        <button className="icon-button" type="button" aria-label={`Share ${artistLine(event)}`} onClick={() => onShare(event)}>
          <Share2 size={18} aria-hidden="true" />
        </button>
      </div>
    </article>
  );
}

function EventModal({ event, favorite, onClose, onFavorite, onShare }: {
  event: GigEvent;
  favorite: boolean;
  onClose: () => void;
  onFavorite: (event: GigEvent) => void;
  onShare: (event: GigEvent) => void;
}) {
  const showTime = formatTime(event.show_time);
  const doorsTime = formatTime(event.doors_time);
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="event-modal-title" onMouseDown={(error) => error.stopPropagation()}>
        <button className="icon-button modal-close" type="button" aria-label="Close event details" onClick={onClose}>
          <X size={20} aria-hidden="true" />
        </button>
        {event.image_url ? <img className="modal-image" src={event.image_url} alt="" /> : null}
        <div className="modal-body">
          <p className="eyebrow">{event.category}</p>
          <h2 id="event-modal-title">{artistLine(event)}</h2>
          <div className="detail-grid">
            <span>
              <CalendarDays size={16} aria-hidden="true" />
              {formatDate(event.date)}
            </span>
            <span>
              <MapPin size={16} aria-hidden="true" />
              {event.venue}
            </span>
            {doorsTime ? (
              <span>
                <Clock3 size={16} aria-hidden="true" />
                Doors {doorsTime}
              </span>
            ) : null}
            {showTime ? (
              <span>
                <Clock3 size={16} aria-hidden="true" />
                Show {showTime}
              </span>
            ) : null}
          </div>
          {event.description ? <p className="description">{event.description}</p> : null}
          <div className="modal-actions">
            <a className="primary-link" href={event.ticket_url} target="_blank" rel="noreferrer">
              <Ticket size={17} aria-hidden="true" />
              Tickets
            </a>
            {event.info_url ? (
              <a className="secondary-link" href={event.info_url} target="_blank" rel="noreferrer">
                <ExternalLink size={17} aria-hidden="true" />
                Info
              </a>
            ) : null}
            <button className="secondary-link" type="button" onClick={() => onFavorite(event)} aria-pressed={favorite}>
              <Heart size={17} fill={favorite ? "currentColor" : "none"} aria-hidden="true" />
              Favorite
            </button>
            <button className="secondary-link" type="button" onClick={() => onShare(event)}>
              <Share2 size={17} aria-hidden="true" />
              Share
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

function StatusModal({ status, onClose }: { status: ScrapeStatus | null; onClose: () => void }) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal compact-modal" role="dialog" aria-modal="true" aria-labelledby="status-title" onMouseDown={(error) => error.stopPropagation()}>
        <button className="icon-button modal-close" type="button" aria-label="Close scraper status" onClick={onClose}>
          <X size={20} aria-hidden="true" />
        </button>
        <div className="modal-body">
          <p className="eyebrow">scraper</p>
          <h2 id="status-title">Status</h2>
          {status ? (
            <>
              <div className="status-summary">
                <strong>{status.total_events}</strong>
                <span>events scraped {new Date(status.scraped_at).toLocaleString()}</span>
              </div>
              <div className="status-list">
                {status.venues.map((venue) => (
                  <div className="status-row" key={venue.venue}>
                    <span className={`status-dot ${venue.status}`} aria-hidden="true" />
                    <strong>{venue.venue}</strong>
                    <span>{venue.status === "ok" ? `${venue.count} events` : venue.message || "error"}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="description">Status data is not available.</p>
          )}
        </div>
      </section>
    </div>
  );
}

export default function App() {
  const [events, setEvents] = useState<GigEvent[]>([]);
  const [status, setStatus] = useState<ScrapeStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<CategoryFilter>("all");
  const [venue, setVenue] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [statusOpen, setStatusOpen] = useState(false);
  const [favorites, setFavorites] = useState<Set<string>>(() => {
    try {
      return new Set(JSON.parse(localStorage.getItem("bkn-gigs:favorites") || "[]"));
    } catch {
      return new Set();
    }
  });

  useEffect(() => {
    let alive = true;
    Promise.all([loadEvents(), loadStatus()]).then(([nextEvents, nextStatus]) => {
      if (!alive) {
        return;
      }
      setEvents(nextEvents);
      setStatus(nextStatus);
      setLoading(false);
      const initial = new URL(window.location.href).searchParams.get("event");
      if (initial) {
        setSelectedSlug(initial);
      }
    });
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    localStorage.setItem("bkn-gigs:favorites", JSON.stringify(Array.from(favorites)));
  }, [favorites]);

  const venues = useMemo(() => Array.from(new Set(events.map((event) => event.venue))).sort(), [events]);

  const filteredEvents = useMemo(() => {
    const q = query.trim().toLowerCase();
    return events.filter((event) => {
      const key = eventKey(event);
      const haystack = [artistLine(event), event.venue, event.description, event.category].filter(Boolean).join(" ").toLowerCase();
      return (
        (!q || haystack.includes(q)) &&
        (category === "all" || event.category === category) &&
        (venue === "all" || event.venue === venue) &&
        (!dateFilter || event.date === dateFilter) &&
        (!favoritesOnly || favorites.has(key))
      );
    });
  }, [category, dateFilter, events, favorites, favoritesOnly, query, venue]);

  const selectedEvent = selectedSlug ? events.find((event) => eventKey(event) === selectedSlug) || null : null;

  function openEvent(event: GigEvent) {
    const key = eventKey(event);
    setSelectedSlug(key);
    const url = new URL(window.location.href);
    url.searchParams.set("event", key);
    window.history.pushState({}, "", url);
  }

  function closeEvent() {
    setSelectedSlug(null);
    const url = new URL(window.location.href);
    url.searchParams.delete("event");
    window.history.pushState({}, "", url);
  }

  function toggleFavorite(event: GigEvent) {
    const key = eventKey(event);
    setFavorites((current) => {
      const next = new Set(current);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  }

  async function shareEvent(event: GigEvent) {
    const text = `${artistLine(event)} at ${event.venue}`;
    const url = shareUrl(event);
    if (navigator.share) {
      await navigator.share({ title: text, url });
    } else {
      await navigator.clipboard?.writeText(url);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Brooklyn</p>
          <h1>BKN Gigs</h1>
        </div>
        <button className="status-button" type="button" onClick={() => setStatusOpen(true)}>
          <Info size={18} aria-hidden="true" />
          Status
        </button>
      </header>

      <section className="toolbar" aria-label="Event filters">
        <label className="search-box">
          <Search size={18} aria-hidden="true" />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search artists, venues, keywords" />
        </label>
        <label className="select-box">
          <MapPin size={18} aria-hidden="true" />
          <select value={venue} onChange={(event) => setVenue(event.target.value)} aria-label="Venue">
            <option value="all">All venues</option>
            {venues.map((name) => (
              <option value={name} key={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="date-box">
          <CalendarDays size={18} aria-hidden="true" />
          <input type="date" value={dateFilter} onChange={(event) => setDateFilter(event.target.value)} aria-label="Date" />
        </label>
        <button className="toggle-button" type="button" aria-pressed={favoritesOnly} onClick={() => setFavoritesOnly((value) => !value)}>
          <Heart size={18} fill={favoritesOnly ? "currentColor" : "none"} aria-hidden="true" />
          Favorites
        </button>
      </section>

      <section className="category-row" aria-label="Categories">
        <ListFilter size={18} aria-hidden="true" />
        {CATEGORY_OPTIONS.map((option) => (
          <button className={category === option.id ? "chip active" : "chip"} key={option.id} type="button" onClick={() => setCategory(option.id)}>
            {option.label}
          </button>
        ))}
      </section>

      <section className="results-heading" aria-live="polite">
        <h2>{loading ? "Loading events" : `${filteredEvents.length} events`}</h2>
        {status?.scraped_at ? <span>Updated {new Date(status.scraped_at).toLocaleString()}</span> : null}
      </section>

      <section className="event-list" aria-label="Events">
        {!loading && filteredEvents.length === 0 ? <p className="empty-state">No events found.</p> : null}
        {filteredEvents.map((event) => (
          <EventCard
            event={event}
            favorite={favorites.has(eventKey(event))}
            key={eventKey(event)}
            onOpen={openEvent}
            onFavorite={toggleFavorite}
            onShare={shareEvent}
          />
        ))}
      </section>

      {selectedEvent ? (
        <EventModal event={selectedEvent} favorite={favorites.has(eventKey(selectedEvent))} onClose={closeEvent} onFavorite={toggleFavorite} onShare={shareEvent} />
      ) : null}
      {statusOpen ? <StatusModal status={status} onClose={() => setStatusOpen(false)} /> : null}
    </main>
  );
}
