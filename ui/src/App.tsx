import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useState, useEffect, useCallback, useMemo } from "react";
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
  const [loading, setLoading] = useState(true);
  const [scrapeStatus, setScrapeStatus] = useState<ScrapeStatus | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();

  const selectedEvent = useMemo(() => {
    const eventSlug = searchParams.get("event");
    return eventSlug ? events.find((event) => event.slug === eventSlug) || null : null;
  }, [events, searchParams]);

  // Handle event selection with URL update
  const handleEventSelect = useCallback((event: Event) => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set("event", event.slug);
    navigate(
      { pathname: location.pathname, search: `?${nextParams.toString()}` },
      { state: { eventModal: true } }
    );
  }, [location.pathname, navigate, searchParams]);

  // Handle modal close
  const handleModalClose = useCallback(() => {
    if (location.state?.eventModal) {
      navigate(-1);
      return;
    }

    const nextParams = new URLSearchParams(searchParams);
    nextParams.delete("event");
    const nextSearch = nextParams.toString();
    navigate(
      { pathname: location.pathname, search: nextSearch ? `?${nextSearch}` : "" },
      { replace: true }
    );
  }, [location.pathname, location.state, navigate, searchParams]);

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
    <div className="bg-neutral-950 text-neutral-200 font-sans selection:bg-fuchsia-500/30 selection:text-fuchsia-200">
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
