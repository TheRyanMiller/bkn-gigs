import { Fragment, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { format } from "date-fns";
import {
  CalendarDays,
  Check,
  ChevronDown,
  ChevronUp,
  Clock,
  ExternalLink,
  Info,
  MapPin,
  Share2,
  Star,
  Ticket,
  X,
} from "lucide-react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpotify } from "@fortawesome/free-brands-svg-icons";
import { Event } from "../types";
import { useFavorites } from "../context/FavoritesContext";

interface EventModalProps {
  event: Event;
  onClose: () => void;
}

const DESCRIPTION_COLLAPSE_THRESHOLD = 420;

const formatTime = (time: string | null) => {
  if (!time) return null;
  const [hours, minutes] = time.split(":");
  const hour = Number.parseInt(hours, 10);
  const suffix = hour >= 12 ? "PM" : "AM";
  return `${hour % 12 || 12}:${minutes} ${suffix}`;
};

export default function EventModal({ event, onClose }: EventModalProps) {
  const [copied, setCopied] = useState(false);
  const [descriptionExpanded, setDescriptionExpanded] = useState(false);
  const { isFavorite, toggleFavorite } = useFavorites();

  const {
    venue,
    date,
    doors_time,
    show_time,
    artists,
    price,
    ticket_url,
    info_url,
    image_url,
    slug,
    stage,
    description,
  } = event;
  const favorited = isFavorite(slug);

  const eventDate = new Date(`${date}T12:00:00`);
  const formattedDate = format(eventDate, "EEEE, MMMM d, yyyy");
  const day = eventDate.getDate();
  const month = format(eventDate, "MMM").toUpperCase();

  const descriptionText = description?.trim() || "";
  const isLongDescription = descriptionText.length > DESCRIPTION_COLLAPSE_THRESHOLD;
  const descriptionParagraphs = descriptionText
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/e/${slug}`);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  return (
    <Transition.Root show as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-150"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-hidden">
          <div className="flex min-h-full items-start justify-center p-2 pt-3 text-center sm:items-center sm:p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-150"
              enterFrom="opacity-0 translate-y-2 sm:translate-y-0 sm:scale-[0.98]"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-100"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-2 sm:translate-y-0 sm:scale-[0.98]"
            >
              <Dialog.Panel className="relative max-h-[calc(100dvh-1.25rem)] w-full max-w-2xl transform overflow-hidden rounded-xl border border-neutral-800 bg-neutral-900 text-left shadow-2xl">
                <div className="absolute right-2.5 top-2.5 z-20 flex gap-1.5">
                  <button
                    type="button"
                    onClick={() => toggleFavorite(slug)}
                    className="flex h-9 w-9 items-center justify-center rounded-md border border-neutral-700/80 bg-neutral-950/90 text-neutral-400 backdrop-blur transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
                    aria-label={favorited ? "Remove from favorites" : "Add to favorites"}
                  >
                    <Star size={16} className={favorited ? "fill-yellow-400 text-yellow-400" : ""} />
                  </button>
                  <button
                    type="button"
                    onClick={onClose}
                    className="flex h-9 w-9 items-center justify-center rounded-md border border-neutral-700/80 bg-neutral-950/90 text-neutral-400 backdrop-blur transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
                    aria-label="Close event details"
                  >
                    <X size={17} />
                  </button>
                </div>

                <div className="flex max-h-[calc(100dvh-1.25rem)] flex-col sm:h-[34rem] sm:max-h-[calc(100vh-2rem)] sm:flex-row">
                  <div className="relative h-40 w-full shrink-0 bg-neutral-950 sm:h-full sm:w-60">
                    {image_url ? (
                      <img
                        src={image_url}
                        alt={artists[0]?.name || "Event image"}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center bg-neutral-950">
                        <Ticket size={40} className="text-neutral-700" />
                      </div>
                    )}
                    <div className="absolute left-3 top-3 flex h-12 w-12 flex-col items-center justify-center rounded-lg border border-neutral-700 bg-neutral-950/95">
                      <span className="text-[9px] font-semibold uppercase tracking-wider text-fuchsia-300">
                        {month}
                      </span>
                      <span className="text-lg font-semibold leading-none text-white">{day}</span>
                    </div>
                  </div>

                  <div className="flex min-h-0 flex-1 flex-col overflow-hidden p-4 sm:p-5">
                    <div
                      className="min-h-0 flex-1 overflow-y-auto pr-1 sm:pr-2"
                      data-testid="event-modal-scroll-area"
                    >
                      <Dialog.Title className="mb-1 text-xl font-semibold leading-tight text-white sm:pr-20 sm:text-2xl">
                        {artists[0]?.name}
                        {artists[0]?.spotify_url && (
                          <a
                            href={artists[0].spotify_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-2 inline text-neutral-500 transition-colors hover:text-fuchsia-300"
                            aria-label="Open Spotify artist"
                          >
                            <FontAwesomeIcon icon={faSpotify} className="inline-block h-4 w-4 -translate-y-0.5" />
                          </a>
                        )}
                      </Dialog.Title>

                      {artists.length > 1 && (
                        <p className="mb-4 text-sm text-neutral-400">
                          <span className="text-neutral-600">with</span>{" "}
                          {artists.slice(1).map((artist, index) => (
                            <span key={`${artist.name}-${index}`}>
                              {index > 0 && ", "}
                              {artist.name}
                              {artist.spotify_url && (
                                <a
                                  href={artist.spotify_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="ml-1 inline text-neutral-500 transition-colors hover:text-fuchsia-300"
                                  aria-label="Open Spotify artist"
                                >
                                  <FontAwesomeIcon icon={faSpotify} className="inline-block h-2.5 w-2.5 -translate-y-px" />
                                </a>
                              )}
                            </span>
                          ))}
                        </p>
                      )}

                      <div className="mb-4 space-y-2 text-sm text-neutral-300">
                        <div className="flex items-center gap-2">
                          <MapPin size={13} className="shrink-0 text-neutral-500" />
                          <span>{venue}{stage && ` · ${stage}`}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CalendarDays size={13} className="shrink-0 text-neutral-500" />
                          <span>{formattedDate}</span>
                        </div>
                        {(doors_time || show_time) && (
                          <div className="flex items-center gap-2">
                            <Clock size={13} className="shrink-0 text-neutral-500" />
                            <span>
                              {doors_time && `Doors ${formatTime(doors_time)}`}
                              {doors_time && show_time && " · "}
                              {show_time && `Show ${formatTime(show_time)}`}
                            </span>
                          </div>
                        )}
                        {price && (
                          <div className="flex items-center gap-2">
                            <Ticket size={13} className="shrink-0 text-neutral-500" />
                            <span>{price}</span>
                          </div>
                        )}
                      </div>

                      {descriptionText && (
                        <div className="border-t border-neutral-800 pt-4">
                          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-neutral-400">
                            <Info size={13} />
                            About
                          </div>
                          <div
                            className={`space-y-3 text-sm leading-6 text-neutral-300 ${
                              isLongDescription && !descriptionExpanded
                                ? "relative max-h-28 overflow-hidden after:pointer-events-none after:absolute after:inset-x-0 after:bottom-0 after:h-14 after:bg-gradient-to-t after:from-neutral-900 after:to-transparent sm:max-h-32"
                                : ""
                            }`}
                          >
                            {descriptionParagraphs.map((paragraph, index) => (
                              <p key={index}>{paragraph}</p>
                            ))}
                          </div>
                          {isLongDescription && (
                            <button
                              type="button"
                              onClick={() => setDescriptionExpanded((expanded) => !expanded)}
                              aria-expanded={descriptionExpanded}
                              className="mt-3 inline-flex items-center gap-1 rounded text-xs font-medium text-fuchsia-300 transition-colors hover:text-fuchsia-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
                            >
                              {descriptionExpanded ? (
                                <>Show less <ChevronUp size={13} /></>
                              ) : (
                                <>Show more <ChevronDown size={13} /></>
                              )}
                            </button>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="mt-3 flex shrink-0 gap-2 border-t border-neutral-800 pt-3">
                      <button
                        type="button"
                        onClick={handleShare}
                        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-neutral-700 bg-neutral-800 text-neutral-400 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
                        aria-label={copied ? "Event link copied" : "Copy event link"}
                      >
                        {copied ? <Check size={15} className="text-green-400" /> : <Share2 size={15} />}
                      </button>
                      <a
                        href={ticket_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex h-10 flex-1 items-center justify-center gap-1.5 rounded-md bg-fuchsia-600 px-4 text-sm font-semibold text-white transition-colors hover:bg-fuchsia-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300"
                      >
                        <Ticket size={14} />
                        Tickets
                      </a>
                      {info_url && info_url !== ticket_url && (
                        <a
                          href={info_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex h-10 items-center justify-center gap-1.5 rounded-md border border-neutral-700 bg-neutral-800 px-3 text-sm font-medium text-neutral-300 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
                        >
                          <ExternalLink size={14} />
                          <span className="hidden sm:inline">Info</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
