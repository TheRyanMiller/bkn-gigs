import { BrowserRouter as Router, Routes, Route, useSearchParams } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import Home from "./pages/Home";
import Favorites from "./pages/Favorites";
import Header from "./components/Header";
import EventModal from "./components/EventModal";
import ScrapeStatusModal from "./components/ScrapeStatusModal";
import { FavoritesProvider } from "./context/FavoritesContext";
import { loadEvents, loadStatus } from "./data";
import { Event, ScrapeStatus } from "./types";

function AppContent() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [scrapeStatus, setScrapeStatus] = useState<ScrapeStatus | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  // Handle event selection with URL update
  const handleEventSelect = useCallback((event: Event | null) => {
    setSelectedEvent(event);
    if (event) {
      setSearchParams({ event: event.slug });
    } else {
      setSearchParams({});
    }
  }, [setSearchParams]);

  // Handle modal close
  const handleModalClose = useCallback(() => {
    setSelectedEvent(null);
    setSearchParams({});
  }, [setSearchParams]);

  useEffect(() => {
    let alive = true;

    loadStatus()
      .then((statusData) => {
        if (!alive) {
          return [];
        }
        setScrapeStatus(statusData);
        return loadEvents(statusData?.last_run);
      })
      .then((nextEvents) => {
        if (!alive) {
          return;
        }
        setEvents(nextEvents);
        setLoading(false);

        // Check for event slug in URL and open modal
        const eventSlug = new URL(window.location.href).searchParams.get("event");
        if (eventSlug) {
          const event = nextEvents.find((e) => e.slug === eventSlug);
          if (event) {
            setSelectedEvent(event);
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setEvents([]);
        setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div className="bg-neutral-950 text-neutral-200 font-sans selection:bg-teal-500/30 selection:text-teal-200">
      <Header
        status={scrapeStatus}
        onStatusClick={() => setShowStatusModal(true)}
      />

      {/* Main Content */}
      <main className="pt-[2px]">
        <Routes>
          <Route
            path="/"
            element={<Home events={events} loading={loading} onEventClick={handleEventSelect} />}
          />
          <Route
            path="/favorites"
            element={<Favorites events={events} loading={loading} onEventClick={handleEventSelect} />}
          />
        </Routes>
      </main>

      {selectedEvent && (
        <EventModal
          event={selectedEvent}
          onClose={handleModalClose}
        />
      )}

      {showStatusModal && scrapeStatus && (
        <ScrapeStatusModal
          status={scrapeStatus}
          onClose={() => setShowStatusModal(false)}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <FavoritesProvider>
      <Router>
        <AppContent />
      </Router>
    </FavoritesProvider>
  );
}

export default App;
