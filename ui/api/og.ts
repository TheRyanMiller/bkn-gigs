export const config = {
  runtime: "edge",
};

const R2_PUBLIC_URL = "https://pub-756023fa49674586a44105ba7bf52137.r2.dev";
const R2_PUBLIC_PREFIX = "apps/bkn-gigs/prod/public";

function escapeXml(value: string) {
  return value.replace(/[<>&"']/g, (char) => {
    switch (char) {
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case "&":
        return "&amp;";
      case "\"":
        return "&quot;";
      default:
        return "&#39;";
    }
  });
}

async function eventTitle(slug: string | null) {
  if (!slug) {
    return "BKN Gigs";
  }
  try {
    const response = await fetch(`${R2_PUBLIC_URL}/${R2_PUBLIC_PREFIX}/events.json`, { cache: "no-store" });
    if (!response.ok) {
      return "BKN Gigs";
    }
    const events = (await response.json()) as Array<{ slug?: string; artists?: Array<{ name: string }>; venue?: string }>;
    const event = events.find((item) => item.slug === slug);
    if (!event) {
      return "BKN Gigs";
    }
    const artists = event.artists?.map((artist) => artist.name).join(" + ");
    return [artists, event.venue].filter(Boolean).join(" at ");
  } catch {
    return "BKN Gigs";
  }
}

export default async function handler(request: Request) {
  const url = new URL(request.url);
  const title = escapeXml(await eventTitle(url.searchParams.get("event")));
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#f6f1e9"/>
  <rect x="64" y="64" width="1072" height="502" rx="8" fill="#ffffff" stroke="#1d2026" stroke-opacity=".16"/>
  <text x="96" y="160" font-family="Inter, Arial, sans-serif" font-size="38" font-weight="800" fill="#a53f2b">Brooklyn</text>
  <text x="96" y="278" font-family="Inter, Arial, sans-serif" font-size="84" font-weight="900" fill="#12151a">BKN Gigs</text>
  <foreignObject x="96" y="330" width="1008" height="140">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Inter,Arial,sans-serif;font-size:44px;font-weight:800;line-height:1.12;color:#164f46;">${title}</div>
  </foreignObject>
</svg>`;
  return new Response(svg, {
    headers: {
      "Content-Type": "image/svg+xml",
      "Cache-Control": "public, max-age=300",
    },
  });
}
