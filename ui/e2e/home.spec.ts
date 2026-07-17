import { test, expect, type Locator } from "@playwright/test";

const getTodayET = () =>
  new Date().toLocaleDateString("en-CA", { timeZone: "America/New_York" });

const longDescription = "A detailed artist biography for this show. ".repeat(30);
const testImage =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 9'%3E%3Crect width='16' height='9' fill='%23a21caf'/%3E%3C/svg%3E";

const expectWithinVisibleArea = async (element: Locator, container: Locator) => {
  const elementBox = await element.boundingBox();
  const containerBox = await container.boundingBox();

  expect(elementBox).not.toBeNull();
  expect(containerBox).not.toBeNull();
  expect(elementBox!.y).toBeGreaterThanOrEqual(containerBox!.y);
  expect(elementBox!.y + elementBox!.height).toBeLessThanOrEqual(
    containerBox!.y + containerBox!.height + 1
  );
};

test.beforeEach(async ({ page }) => {
  const now = new Date().toISOString();
  const today = getTodayET();

  const events = [
    {
      slug: `${today}-brooklyn-steel-sample-band`,
      venue: "Brooklyn Steel",
      date: today,
      doors_time: "19:00",
      show_time: "20:00",
      artists: [
        { name: "Sample Band", spotify_url: "https://open.spotify.com/artist/AAA" },
        { name: "Opening Act", spotify_url: "https://open.spotify.com/artist/BBB" },
      ],
      price: "$20",
      ticket_url: "https://example.com/tickets",
      info_url: "https://example.com/info",
      image_url: testImage,
      description: longDescription,
      category: "concerts",
      first_seen: now,
      last_seen: now,
      is_new: true,
    },
    ...Array.from({ length: 30 }, (_, index) => ({
      slug: `${today}-union-pool-filler-band-${index + 1}`,
      venue: "Union Pool",
      date: today,
      doors_time: "19:00",
      show_time: "20:00",
      artists: [{ name: `Filler Band ${index + 1}`, spotify_url: null }],
      price: "$15",
      ticket_url: "https://example.com/tickets",
      info_url: "https://example.com/info",
      image_url: testImage,
      description: null,
      category: "concerts",
      first_seen: now,
      last_seen: now,
      is_new: false,
    })),
  ];

  const status = {
    app: "bkn-gigs",
    scraped_at: now,
    total_events: events.length,
    previous_total_events: 0,
    venues: [
      {
        venue: "Brooklyn Steel",
        status: "ok",
        count: events.length,
        message: null,
        scraped_at: now,
      },
    ],
  };

  await page.route("**/scrape-status.json*", (route) =>
    route.fulfill({ json: status })
  );
  await page.route("**/events.json*", (route) =>
    route.fulfill({ json: events })
  );
});

test("loads events and opens modal", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByText("Sample Band")).toBeVisible();
  await expect(page.getByLabel("Open Spotify artist").first()).toBeVisible();

  await page.getByText("Sample Band").click();
  await expect(page).toHaveURL(/\\?event=/);
  await expect(page.getByText("A detailed artist biography for this show.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Tickets" })).toBeVisible();
});

test("back closes the modal, preserves list position, and forward reopens it", async ({ page }) => {
  await page.goto("/");

  const list = page.getByTestId("events-list");
  await list.evaluate((element) => element.scrollTo({ top: 1300 }));
  await expect(page.getByText("Filler Band 6")).toBeVisible();

  await page.getByText("Filler Band 6").click();
  await expect(page.getByTestId("event-modal-scroll-area")).toBeVisible();
  await expect(page).toHaveURL(/\?event=/);
  const scrollAtOpen = await list.evaluate((element) => element.scrollTop);

  await page.goBack();
  await expect(page.getByTestId("event-modal-scroll-area")).toHaveCount(0);
  await expect(page).not.toHaveURL(/\?event=/);
  await expect(page.getByText("Filler Band 6")).toBeVisible();
  await expect.poll(() => list.evaluate((element) => element.scrollTop)).toBe(scrollAtOpen);

  await page.goForward();
  await expect(page.getByTestId("event-modal-scroll-area")).toBeVisible();
  await expect(page).toHaveURL(/\?event=/);
});

test("closing a directly linked event returns to the list", async ({ page }) => {
  const eventSlug = `${getTodayET()}-brooklyn-steel-sample-band`;
  await page.goto(`/?event=${eventSlug}`);

  await expect(page.getByTestId("event-modal-scroll-area")).toBeVisible();
  await page.keyboard.press("Escape");

  await expect(page.getByTestId("event-modal-scroll-area")).toHaveCount(0);
  await expect(page).not.toHaveURL(/\?event=/);
  await expect(page.getByText("Sample Band")).toBeVisible();
});

test("expanding long descriptions does not resize modal image", async ({ page }) => {
  await page.setViewportSize({ width: 1024, height: 768 });
  await page.goto("/");

  await page.getByText("Sample Band").click();
  const modalImage = page.getByRole("img", { name: "Sample Band" }).last();
  const scrollArea = page.getByTestId("event-modal-scroll-area");
  const showMore = page.getByRole("button", { name: "Show more" });
  await expect(showMore).toBeVisible();
  await expectWithinVisibleArea(showMore, scrollArea);

  const before = await modalImage.boundingBox();
  await showMore.click();
  const after = await modalImage.boundingBox();

  expect(before?.height).toBeGreaterThan(0);
  expect(after?.height).toBe(before?.height);
});

test("long description expansion is reachable on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await page.getByText("Sample Band").click();
  const scrollArea = page.getByTestId("event-modal-scroll-area");
  const showMore = page.getByRole("button", { name: "Show more" });
  await expect(scrollArea).toBeVisible();

  await expect(showMore).toBeVisible();
  await expectWithinVisibleArea(showMore, scrollArea);

  await showMore.click();
  const showLess = page.getByRole("button", { name: "Show less" });
  await expect(showLess).toBeVisible();
});
