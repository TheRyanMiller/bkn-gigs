import { Github, Music, Star } from "lucide-react";
import { Link } from "react-router-dom";
import { ScrapeStatus } from "../types";
import { useFavorites } from "../context/FavoritesContext";

interface HeaderProps {
  status: ScrapeStatus | null;
  onStatusClick: () => void;
}

const utilityClass =
  "flex h-9 items-center justify-center gap-1.5 rounded-md px-2 text-neutral-400 transition-colors hover:bg-neutral-900 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70 sm:px-2.5";

export default function Header({ status, onStatusClick }: HeaderProps) {
  const isHealthy = status?.all_success ?? true;
  const { favoriteCount } = useFavorites();

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-900 bg-neutral-950/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-3 sm:px-4 md:h-16">
        <Link
          to="/"
          className="group flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-md border border-fuchsia-500/20 bg-fuchsia-500/10">
            <Music size={16} className="text-fuchsia-400" />
          </div>
          <span className="font-montserrat text-lg font-bold tracking-tight text-white">
            BKN<span className="text-fuchsia-400">Gigs</span>
          </span>
        </Link>

        <nav className="flex items-center gap-0.5 sm:gap-1" aria-label="Primary navigation">
          <Link to="/favorites" className={utilityClass} aria-label={`${favoriteCount} favorites`}>
            <Star
              size={15}
              className={favoriteCount > 0 ? "fill-yellow-400 text-yellow-400" : ""}
            />
            <span className="hidden text-xs sm:inline">Favorites</span>
            {favoriteCount > 0 && (
              <span className="min-w-4 rounded bg-neutral-800 px-1 text-center text-[10px] font-semibold text-neutral-300">
                {favoriteCount > 99 ? "99+" : favoriteCount}
              </span>
            )}
          </Link>

          <button
            type="button"
            onClick={onStatusClick}
            className={utilityClass}
            aria-label={status ? `${status.total_events} events; open scrape status` : "Loading event status"}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${isHealthy ? "bg-green-500" : "bg-red-500"}`} />
            <span className="hidden text-xs sm:inline">
              {status ? `${status.total_events} events` : "Loading"}
            </span>
          </button>

          <a
            href="https://github.com/TheRyanMiller/bkn-gigs"
            target="_blank"
            rel="noopener noreferrer"
            className={`${utilityClass} w-9 px-0 sm:px-0`}
            aria-label="View source on GitHub"
          >
            <Github size={15} />
          </a>
        </nav>
      </div>
    </header>
  );
}
