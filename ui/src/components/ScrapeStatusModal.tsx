import { format } from "date-fns";
import { X } from "lucide-react";
import { ScrapeStatus } from "../types";

interface ScrapeStatusModalProps {
  status: ScrapeStatus;
  onClose: () => void;
}

const formatDate = (isoString: string | undefined) => {
  if (!isoString) return "Never";
  try {
    return format(new Date(isoString), "MMM d, yyyy 'at' h:mm a");
  } catch {
    return isoString;
  }
};

export default function ScrapeStatusModal({ status, onClose }: ScrapeStatusModalProps) {
  const statusLabel = status.all_success
    ? "All sources operational"
    : status.any_success
      ? "Some sources need attention"
      : "Sources unavailable";
  const statusColor = status.all_success
    ? "bg-green-500"
    : status.any_success
      ? "bg-amber-500"
      : "bg-red-500";

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 p-3 pt-12 backdrop-blur-sm sm:items-center sm:p-4"
      onClick={onClose}
    >
      <div
        className="max-h-[82vh] w-full max-w-md overflow-hidden rounded-xl border border-neutral-800 bg-neutral-900 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex h-12 items-center justify-between border-b border-neutral-800 px-4">
          <h2 className="text-sm font-semibold text-white">Scrape status</h2>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-md text-neutral-500 transition-colors hover:bg-neutral-800 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-500/70"
            aria-label="Close status"
          >
            <X size={16} />
          </button>
        </div>

        <div className="max-h-[calc(82vh-3rem)] overflow-y-auto p-3">
          <div className="mb-4 rounded-lg border border-neutral-800 bg-neutral-950/40 p-3">
            <div className="mb-1.5 flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${statusColor}`} />
              <span className="text-sm font-medium text-white">{statusLabel}</span>
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-500">
              <span>{status.total_events} events</span>
              <span>Updated {formatDate(status.last_run)}</span>
            </div>
          </div>

          <h3 className="mb-2 px-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-neutral-600">
            Venue sources
          </h3>
          <div className="space-y-1.5">
            {Object.entries(status.venues).map(([venueName, venueStatus]) => (
              <div
                key={venueName}
                className="rounded-lg border border-neutral-800/80 bg-neutral-950/25 px-3 py-2.5"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-2">
                    <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${venueStatus.success ? "bg-green-500" : "bg-red-500"}`} />
                    <span className="truncate text-sm font-medium text-neutral-200">{venueName}</span>
                  </div>
                  {venueStatus.success && (
                    <span className="shrink-0 text-xs tabular-nums text-neutral-500">
                      {venueStatus.event_count}
                    </span>
                  )}
                </div>
                {!venueStatus.success && (
                  <p className="mt-1.5 text-xs text-red-400">{venueStatus.error}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
