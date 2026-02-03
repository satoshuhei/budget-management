import { describe, expect, it } from "vitest";
import { buildSummaryCards } from "./dashboard";

describe("buildSummaryCards", () => {
  it("returns five cards with JPY formatted values", () => {
    const cards = buildSummaryCards({ budget_total: "1200000", plan_total: "450000" });
    expect(cards).toHaveLength(5);
    expect(cards[0].value).toBe("￥1,200,000");
    expect(cards[1].value).toBe("￥450,000");
  });

  it("handles missing summary", () => {
    const cards = buildSummaryCards(null);
    expect(cards[0].value).toBe("-");
  });
});
