import { memo } from "react";
import { format } from "date-fns";
import { Clock, MapPin, Star, Ticket } from "lucide-react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpotify } from "@fortawesome/free-brands-svg-icons";
import { Event, CATEGORY_LABELS } from "../types";
import { useFavorites } from "../context/FavoritesContext";

interface EventCardProps {
  event: Event;
  onClick: () => void;
}

const formatTime = (time: string | null) => {
  if (!time) return null;
  const [hours, minutes] = time.split(":");
  const hour = Number.parseInt(hours, 10);
  const suffix = hour >= 12 ? "PM" : "AM";
  return `${hour % 12 || 12}:${minutes} ${suffix}`;
};

function EventCard({ event, onClick }: EventCardProps) {
  const {
    venue,
    date,
    doors_time,
    show_time,
    artists,
    price,
    image_url,
    ticket_url,
    slug,
    category,
    is_new,
    stage,
  } = event;
  const { isFavorite, toggleFavorite } = useFavorites();
  const favorited = isFavorite(slug);

  const eventDate = new Date(`${date}T12:00:00`);
  const dateLabel = format(eventDate, "EEE · MMM d").toUpperCase();
  const mainArtist = artists[0]?.name || "TBA";
  const supportArtists = artists.slice(1).map((artist) => artist.name).join(", ");
  const primaryTime = show_time ? formatTime(show_time) : formatTime(doors_time);
  const timeLabel = primaryTime && !show_time ? `Doors ${primaryTime}` : primaryTime;

  const handleFavorite = (event: React.MouseEvent) => {
    event.stopPropagation();
    toggleFavorite(slug);
  };

  return (
    <article
      className="group relative flex h-[120px] overflow-hidden rounded-lg border border-neutral-800/90 bg-neutral-900/50 transition-colors hover:border-neutral-700 hover:bg-neutral-900"
    >
      <button
        type="button"
        onClick={onClick}
        className="absolute inset-0 z-10 cursor-pointer rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-fuchsia-500/70"
        aria-label={`View ${mainArtist} at ${venue}`}
      />
      <div className="relative w-20 shrink-0 overflow-hidden bg-neutral-900 sm:w-28">
        {image_url ? (
          <img
            src={image_url}
            alt=""
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-neutral-900">
            <Ticket size={24} className="text-neutral-700" />
          </div>
        )}
      </div>

      <div className="flex min-w-0 flex-1 items-center gap-2 px-3 py-2.5 sm:gap-4 sm:px-4">
        <div className="min-w-0 flex-1">
          <div className="mb-0.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-neutral-500">
            <time dateTime={date}>{dateLabel}</time>
            <span className="hidden text-neutral-700 sm:inline">/</span>
            <span className="hidden sm:inline">{CATEGORY_LABELS[category]}</span>
            {is_new && (
              <span className="inline-flex items-center gap-1 text-fuchsia-300">
                <span className="h-1 w-1 rounded-full bg-fuchsia-400" />
                New
              </span>
            )}
          </div>

          <h3 className="line-clamp-2 text-[15px] font-semibold leading-5 text-neutral-50 transition-colors group-hover:text-white sm:line-clamp-1 sm:text-lg sm:leading-6">
            {mainArtist}
            {artists[0]?.spotify_url && (
              <a
                href={artists[0].spotify_url}
                target="_blank"
                rel="noopener noreferrer"
                className="relative z-20 ml-1.5 inline text-neutral-500 transition-colors hover:text-fuchsia-300"
                aria-label="Open Spotify artist"
              >
                <FontAwesomeIcon icon={faSpotify} className="inline-block h-3 w-3 -translate-y-px" />
              </a>
            )}
          </h3>

          {supportArtists && (
            <p className="mt-0.5 truncate text-xs text-neutral-500">
              <span className="text-neutral-600">with</span> {supportArtists}
            </p>
          )}

          <div className="mt-1.5 flex min-w-0 items-center gap-2 text-xs text-neutral-400 sm:gap-3">
            <span className="flex min-w-0 items-center gap-1.5">
              <MapPin size={12} className="shrink-0 text-neutral-600" />
              <span className="truncate">{venue}{stage && ` · ${stage}`}</span>
            </span>
            {timeLabel && (
              <span className="flex shrink-0 items-center gap-1.5">
                <Clock size={12} className="text-neutral-600" />
                {timeLabel}
              </span>
            )}
            {price && (
              <span className="hidden shrink-0 text-neutral-500 md:inline">
                {price === "See website" ? "Price on site" : price}
              </span>
            )}
          </div>
        </div>

        <div className="relative z-20 flex shrink-0 flex-col gap-1.5 sm:flex-row sm:items-center sm:gap-2">
          <button
            type="button"
            onClick={handleFavorite}
            className="flex h-9 w-9 items-center justify-center rounded-md border border-neutral-800 bg-neutral-900 text-neutral-500 transition-colors hover:border-neutral-700 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
            aria-label={favorited ? `Remove ${mainArtist} from favorites` : `Add ${mainArtist} to favorites`}
          >
            <Star
              size={15}
              className={favorited ? "fill-yellow-400 text-yellow-400" : ""}
            />
          </button>

          <a
            href={ticket_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex h-9 w-9 items-center justify-center rounded-md bg-fuchsia-600 text-white transition-colors hover:bg-fuchsia-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300 sm:w-auto sm:px-3.5"
            onClick={(event) => event.stopPropagation()}
            aria-label={`Get tickets for ${mainArtist}`}
          >
            <Ticket size={14} />
            <span className="ml-1.5 hidden text-xs font-semibold sm:inline">Tickets</span>
          </a>
        </div>
      </div>
    </article>
  );
}

export default memo(EventCard);
