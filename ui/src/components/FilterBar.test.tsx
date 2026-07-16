import { fireEvent, render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import FilterBar from "./FilterBar";

const renderFilterBar = (overrides: Partial<ComponentProps<typeof FilterBar>> = {}) => {
  const props: ComponentProps<typeof FilterBar> = {
    venues: ["Brooklyn Steel", "Union Hall"],
    selectedVenues: [],
    onVenueToggle: vi.fn(),
    categories: ["concerts", "comedy"],
    selectedCategories: [],
    onCategoryToggle: vi.fn(),
    onSearchChange: vi.fn(),
    onDateRangeChange: vi.fn(),
    showOnlyNew: false,
    onShowOnlyNewToggle: vi.fn(),
    resultCount: 2,
    totalCount: 10,
    ...overrides,
  };
  render(<FilterBar {...props} />);
  return props;
};

test("shows the filtered result count", () => {
  renderFilterBar();
  expect(screen.getByText("2 of 10")).toBeInTheDocument();
});

test("toggles the new-only filter", () => {
  const props = renderFilterBar();
  fireEvent.click(screen.getByRole("button", { name: "New" }));
  expect(props.onShowOnlyNewToggle).toHaveBeenCalledOnce();
});

test("opens category choices and selects a category", () => {
  const props = renderFilterBar();
  fireEvent.click(screen.getByRole("button", { name: /Categories/ }));
  const concertOptions = screen.getAllByRole("button", { name: "Concerts" });
  expect(concertOptions[0].querySelector('[data-icon="guitar"]')).not.toBeNull();
  fireEvent.click(concertOptions[0]);
  expect(props.onCategoryToggle).toHaveBeenCalledWith("concerts");
});
