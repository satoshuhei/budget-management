import { describe, expect, it } from "vitest";
import {
  buildPlanColumns,
  isValidAmountInput,
  isValidPlannedMonth,
  normalizeAmountInput,
  normalizePlannedMonth
} from "./plans";

describe("plans helpers", () => {
  it("includes plan ID column", () => {
    const columns = buildPlanColumns([], []);
    expect(columns[0].field).toBe("id");
    expect(columns[0].headerName).toBe("計画ID");
  });

  it("normalizes planned month inputs", () => {
    expect(normalizePlannedMonth("2026/2")).toBe("2026-02");
    expect(normalizePlannedMonth("2026-12")).toBe("2026-12");
    expect(normalizePlannedMonth("2026-02-01")).toBe("2026-02");
  });

  it("validates planned month formats", () => {
    expect(isValidPlannedMonth("2026/2")).toBe(true);
    expect(isValidPlannedMonth("2026-02")).toBe(true);
    expect(isValidPlannedMonth("2026-2")) .toBe(true);
    expect(isValidPlannedMonth("2026-02-01")) .toBe(true);
    expect(isValidPlannedMonth("2026")) .toBe(false);
  });

  it("normalizes and validates amount inputs", () => {
    expect(normalizeAmountInput("1,200")) .toBe("1200");
    expect(normalizeAmountInput("￥1,200円")) .toBe("1200");
    expect(isValidAmountInput("1,200")).toBe(true);
    expect(isValidAmountInput("￥1,200円")).toBe(true);
    expect(isValidAmountInput("abc")).toBe(false);
  });
});
