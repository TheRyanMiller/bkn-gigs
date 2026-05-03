export interface Artist {
  name: string;
  genre?: string | null;
  spotify_url?: string | null;
}

export type EventCategory = "concerts" | "comedy" | "broadway" | "sports" | "misc";

export const CATEGORY_LABELS: Record<EventCategory, string> = {
  concerts: "Concerts",
  comedy: "Comedy",
  broadway: "Broadway",
  sports: "Sports",
  misc: "Other",
};

export const ALL_CATEGORIES: EventCategory[] = ["concerts", "comedy", "broadway", "sports", "misc"];

export interface Event {
  slug: string;
  venue: string;
  date: string;
  doors_time: string | null;
  show_time: string | null;
  artists: Artist[];
  price?: string | null;
  ticket_url: string;
  info_url?: string | null;
  image_url?: string | null;
  description?: string | null;
  category: EventCategory;
  stage?: string;
  first_seen?: string;
  is_new?: boolean;
  last_seen?: string;
}

export interface VenueStatus {
  last_run: string;
  success: boolean;
  event_count: number;
  error: string | null;
  error_trace?: string;
  last_success?: string;
  last_success_count?: number;
}

export interface ScrapeStatus {
  last_run: string;
  all_success: boolean;
  any_success: boolean;
  total_events: number;
  venues: Record<string, VenueStatus>;
}
