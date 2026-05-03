export type Category = "concerts" | "comedy" | "broadway" | "sports" | "misc";

export interface Artist {
  name: string;
  genre: string | null;
  spotify_url: string | null;
}

export interface GigEvent {
  venue: string;
  date: string;
  doors_time: string | null;
  show_time: string | null;
  artists: Artist[];
  ticket_url: string;
  info_url: string | null;
  image_url: string | null;
  description: string | null;
  price: string | null;
  category: Category;
  slug?: string;
  first_seen?: string;
  last_seen?: string;
  is_new?: boolean;
}

export interface VenueStatus {
  venue: string;
  status: "ok" | "error";
  count: number;
  message: string | null;
  scraped_at: string;
}

export interface ScrapeStatus {
  app: string;
  scraped_at: string;
  total_events: number;
  previous_total_events?: number;
  venues: VenueStatus[];
}
