import { useEffect, useMemo, useRef, useState, type ElementType } from "react";
import { format } from "date-fns";
import { Calendar, Check, ChevronDown, MapPin, Search, Sparkles, Tag, X } from "lucide-react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFaceLaughSquint,
  faFootball,
  faGuitar,
  faMasksTheater,
  faStar,
} from "@fortawesome/free-solid-svg-icons";
import { EventCategory, CATEGORY_LABELS } from "../types";

const categoryIcons = {
  concerts: faGuitar,
  comedy: faFaceLaughSquint,
  broadway: faMasksTheater,
  sports: faFootball,
  misc: faStar,
};

interface DateRange {
  start: string | null;
  end: string | null;
}

interface FilterBarProps {
  venues: string[];
  selectedVenues: string[];
  onVenueToggle: (venue: string) => void;
  categories: EventCategory[];
  selectedCategories: EventCategory[];
  onCategoryToggle: (category: EventCategory) => void;
  onSearchChange: (query: string) => void;
  onDateRangeChange: (range: DateRange) => void;
  showOnlyNew: boolean;
  onShowOnlyNewToggle: () => void;
  resultCount: number;
  totalCount: number;
}

interface FilterControlProps {
  label: string;
  icon: ElementType;
  active?: boolean;
  expanded?: boolean;
  onToggle: () => void;
  onClear?: () => void;
}

const controlBase =
  "h-9 border text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70";

function FilterControl({
  label,
  icon: Icon,
  active = false,
  expanded = false,
  onToggle,
  onClear,
}: FilterControlProps) {
  return (
    <div
      className={`flex h-9 shrink-0 items-stretch overflow-hidden rounded-md border transition-colors ${
        active
          ? "border-fuchsia-500/40 bg-fuchsia-500/10 text-fuchsia-200"
          : "border-neutral-800 bg-neutral-900 text-neutral-400 hover:border-neutral-700 hover:text-white"
      }`}
    >
      <button
        type="button"
        onClick={onToggle}
        className="flex min-w-0 items-center gap-1.5 px-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-fuchsia-500/70"
        aria-expanded={expanded}
      >
        <Icon size={13} className="shrink-0" />
        <span className="max-w-32 truncate text-xs font-medium">{label}</span>
        <ChevronDown size={12} className={`shrink-0 opacity-50 transition-transform ${expanded ? "rotate-180" : ""}`} />
      </button>
      {active && onClear && (
        <button
          type="button"
          onClick={onClear}
          className="flex w-7 items-center justify-center border-l border-fuchsia-500/20 text-fuchsia-300 transition-colors hover:bg-fuchsia-500/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-fuchsia-500/70"
          aria-label={`Clear ${label} filter`}
        >
          <X size={11} />
        </button>
      )}
    </div>
  );
}

const formatFilterDate = (value: string) => format(new Date(`${value}T12:00:00`), "MMM d");

export default function FilterBar({
  venues,
  selectedVenues,
  onVenueToggle,
  categories,
  selectedCategories,
  onCategoryToggle,
  onSearchChange,
  onDateRangeChange,
  showOnlyNew,
  onShowOnlyNewToggle,
  resultCount,
  totalCount,
}: FilterBarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [venueDropdownOpen, setVenueDropdownOpen] = useState(false);
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const [dateDropdownOpen, setDateDropdownOpen] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const rootRef = useRef<HTMLDivElement>(null);

  const threeMonthsAgo = useMemo(() => {
    const date = new Date();
    date.setMonth(date.getMonth() - 3);
    return format(date, "yyyy-MM-dd");
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => onSearchChange(searchQuery), 300);
    return () => window.clearTimeout(timer);
  }, [searchQuery, onSearchChange]);

  useEffect(() => {
    onDateRangeChange({ start: startDate || null, end: endDate || null });
  }, [startDate, endDate, onDateRangeChange]);

  useEffect(() => {
    const handleOutsideClick = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setVenueDropdownOpen(false);
        setCategoryDropdownOpen(false);
        setDateDropdownOpen(false);
      }
    };
    document.addEventListener("pointerdown", handleOutsideClick);
    return () => document.removeEventListener("pointerdown", handleOutsideClick);
  }, []);

  const closeOtherPanels = (panel: "category" | "venue" | "date") => {
    if (panel !== "category") setCategoryDropdownOpen(false);
    if (panel !== "venue") setVenueDropdownOpen(false);
    if (panel !== "date") setDateDropdownOpen(false);
  };

  const clearCategories = () => selectedCategories.forEach(onCategoryToggle);
  const clearVenues = () => selectedVenues.forEach(onVenueToggle);
  const clearDates = () => {
    setStartDate("");
    setEndDate("");
  };

  const categoryLabel =
    selectedCategories.length === 0
      ? "Categories"
      : selectedCategories.length === 1
        ? CATEGORY_LABELS[selectedCategories[0]]
        : `${selectedCategories.length} categories`;
  const venueLabel =
    selectedVenues.length === 0
      ? "Venues"
      : selectedVenues.length === 1
        ? selectedVenues[0]
        : `${selectedVenues.length} venues`;
  const dateLabel = startDate && endDate
    ? startDate === endDate
      ? formatFilterDate(startDate)
      : `${formatFilterDate(startDate)}–${formatFilterDate(endDate)}`
    : startDate
      ? `From ${formatFilterDate(startDate)}`
      : endDate
        ? `Until ${formatFilterDate(endDate)}`
        : "Any date";
  const resultLabel = resultCount === totalCount ? `${totalCount} events` : `${resultCount} of ${totalCount}`;

  return (
    <div ref={rootRef} className="relative">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-center">
        <div className="group relative min-w-0 flex-1 lg:max-w-md">
          <Search
            size={15}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-600 transition-colors group-focus-within:text-fuchsia-400"
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search artists or venues"
            className="h-10 w-full rounded-md border border-neutral-800 bg-neutral-900 pl-9 pr-9 text-sm text-white placeholder:text-neutral-600 focus:border-fuchsia-500/50 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/20"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-1.5 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded text-neutral-500 transition-colors hover:bg-neutral-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
              aria-label="Clear search"
            >
              <X size={13} />
            </button>
          )}
        </div>

        <div className="scrollbar-hide flex min-w-0 items-center gap-1.5 overflow-x-auto pb-0.5 lg:ml-auto lg:overflow-visible lg:pb-0">
          <span className="mr-1 shrink-0 text-xs tabular-nums text-neutral-500" aria-live="polite">
            {resultLabel}
          </span>

          <button
            type="button"
            onClick={onShowOnlyNewToggle}
            className={`${controlBase} flex shrink-0 items-center gap-1.5 rounded-md px-2.5 ${
              showOnlyNew
                ? "border-fuchsia-500/40 bg-fuchsia-500/10 text-fuchsia-200"
                : "border-neutral-800 bg-neutral-900 text-neutral-400 hover:border-neutral-700 hover:text-white"
            }`}
            aria-pressed={showOnlyNew}
          >
            <Sparkles size={13} />
            New
          </button>

          <div className="relative shrink-0">
            <FilterControl
              label={categoryLabel}
              icon={Tag}
              active={selectedCategories.length > 0}
              expanded={categoryDropdownOpen}
              onToggle={() => {
                closeOtherPanels("category");
                setCategoryDropdownOpen((open) => !open);
              }}
              onClear={clearCategories}
            />
            {categoryDropdownOpen && (
              <div className="absolute right-0 top-full z-50 mt-2 hidden w-max max-w-[calc(100vw-2rem)] rounded-lg border border-neutral-800 bg-neutral-900 p-2 shadow-2xl md:block">
                <div className="flex gap-1.5">
                  {categories.map((category) => (
                    <button
                      type="button"
                      key={category}
                      onClick={() => onCategoryToggle(category)}
                      className={`flex h-8 items-center gap-1.5 rounded-md border px-2.5 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70 ${
                        selectedCategories.includes(category)
                          ? "border-fuchsia-500/40 bg-fuchsia-500/10 text-fuchsia-200"
                          : "border-neutral-700 bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-white"
                      }`}
                    >
                      <FontAwesomeIcon icon={categoryIcons[category]} className="h-3 w-3" />
                      {CATEGORY_LABELS[category]}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="relative shrink-0">
            <FilterControl
              label={venueLabel}
              icon={MapPin}
              active={selectedVenues.length > 0}
              expanded={venueDropdownOpen}
              onToggle={() => {
                closeOtherPanels("venue");
                setVenueDropdownOpen((open) => !open);
              }}
              onClear={clearVenues}
            />
            {venueDropdownOpen && (
              <div className="absolute right-0 top-full z-50 mt-2 hidden max-h-72 w-64 overflow-y-auto rounded-lg border border-neutral-800 bg-neutral-900 p-2 shadow-2xl md:block">
                <div className="space-y-1">
                  {venues.map((venue) => {
                    const selected = selectedVenues.includes(venue);
                    return (
                      <button
                        type="button"
                        key={venue}
                        onClick={() => onVenueToggle(venue)}
                        className={`flex min-h-8 w-full items-center gap-2 rounded-md px-2.5 text-left text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70 ${
                          selected
                            ? "bg-fuchsia-500/10 text-fuchsia-200"
                            : "text-neutral-400 hover:bg-neutral-800 hover:text-white"
                        }`}
                      >
                        <Check size={12} className={`shrink-0 ${selected ? "opacity-100" : "opacity-0"}`} />
                        {venue}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="relative shrink-0">
            <FilterControl
              label={dateLabel}
              icon={Calendar}
              active={Boolean(startDate || endDate)}
              expanded={dateDropdownOpen}
              onToggle={() => {
                closeOtherPanels("date");
                setDateDropdownOpen((open) => !open);
              }}
              onClear={clearDates}
            />
            {dateDropdownOpen && (
              <div className="absolute right-0 top-full z-50 mt-2 hidden w-64 rounded-lg border border-neutral-800 bg-neutral-900 p-3 shadow-2xl md:block">
                <div className="space-y-3">
                  <label className="flex flex-col gap-1 text-xs font-medium text-neutral-500">
                    From
                    <input
                      type="date"
                      value={startDate}
                      min={threeMonthsAgo}
                      onChange={(event) => setStartDate(event.target.value)}
                      style={{ colorScheme: "dark" }}
                      className="h-9 rounded-md border border-neutral-700 bg-neutral-950 px-2.5 text-sm font-normal text-white focus:border-fuchsia-500/50 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/20"
                    />
                  </label>
                  <label className="flex flex-col gap-1 text-xs font-medium text-neutral-500">
                    To
                    <input
                      type="date"
                      value={endDate}
                      min={startDate || threeMonthsAgo}
                      onChange={(event) => setEndDate(event.target.value)}
                      style={{ colorScheme: "dark" }}
                      className="h-9 rounded-md border border-neutral-700 bg-neutral-950 px-2.5 text-sm font-normal text-white focus:border-fuchsia-500/50 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/20"
                    />
                  </label>
                  {(startDate || endDate) && (
                    <button
                      type="button"
                      onClick={clearDates}
                      className="h-8 w-full rounded-md text-xs font-medium text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
                    >
                      Clear dates
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {categoryDropdownOpen && (
        <div className="mt-2 flex flex-wrap gap-1.5 rounded-lg border border-neutral-800 bg-neutral-900 p-2.5 shadow-2xl md:hidden">
          {categories.map((category) => {
            const selected = selectedCategories.includes(category);
            return (
              <button
                type="button"
                key={category}
                onClick={() => onCategoryToggle(category)}
                className={`flex h-8 items-center gap-1.5 rounded-md border px-2.5 text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70 ${
                  selected
                    ? "border-fuchsia-500/40 bg-fuchsia-500/10 text-fuchsia-200"
                    : "border-neutral-800 bg-neutral-950/50 text-neutral-400 hover:border-neutral-700 hover:text-white"
                }`}
              >
                <FontAwesomeIcon icon={categoryIcons[category]} className="h-3 w-3" />
                {CATEGORY_LABELS[category]}
              </button>
            );
          })}
        </div>
      )}

      {venueDropdownOpen && (
        <div className="mt-2 max-h-52 overflow-y-auto rounded-lg border border-neutral-800 bg-neutral-900 p-2.5 shadow-2xl md:hidden">
          <div className="grid gap-1 sm:grid-cols-2 lg:grid-cols-3">
            {venues.map((venue) => {
              const selected = selectedVenues.includes(venue);
              return (
                <button
                  type="button"
                  key={venue}
                  onClick={() => onVenueToggle(venue)}
                  className={`flex min-h-8 items-center gap-2 rounded-md px-2.5 text-left text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70 ${
                    selected
                      ? "bg-fuchsia-500/10 text-fuchsia-200"
                      : "text-neutral-400 hover:bg-neutral-800 hover:text-white"
                  }`}
                >
                  <Check size={12} className={`shrink-0 ${selected ? "opacity-100" : "opacity-0"}`} />
                  {venue}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {dateDropdownOpen && (
        <div className="mt-2 rounded-lg border border-neutral-800 bg-neutral-900 p-3 shadow-2xl md:hidden">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <label className="flex flex-1 flex-col gap-1 text-xs font-medium text-neutral-500">
              From
              <input
                type="date"
                value={startDate}
                min={threeMonthsAgo}
                onChange={(event) => setStartDate(event.target.value)}
                style={{ colorScheme: "dark" }}
                className="h-9 rounded-md border border-neutral-700 bg-neutral-950 px-2.5 text-sm font-normal text-white focus:border-fuchsia-500/50 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/20"
              />
            </label>
            <label className="flex flex-1 flex-col gap-1 text-xs font-medium text-neutral-500">
              To
              <input
                type="date"
                value={endDate}
                min={startDate || threeMonthsAgo}
                onChange={(event) => setEndDate(event.target.value)}
                style={{ colorScheme: "dark" }}
                className="h-9 rounded-md border border-neutral-700 bg-neutral-950 px-2.5 text-sm font-normal text-white focus:border-fuchsia-500/50 focus:outline-none focus:ring-2 focus:ring-fuchsia-500/20"
              />
            </label>
            {(startDate || endDate) && (
              <button
                type="button"
                onClick={clearDates}
                className="h-9 rounded-md px-3 text-xs font-medium text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
              >
                Clear dates
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
