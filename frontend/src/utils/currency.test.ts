import { describe, expect, it } from "vitest";
import { formatJPY } from "./currency";

describe("formatJPY", () => {
  it("formats numeric values in JPY", () => {
    expect(formatJPY(1200)).toBe("￥1,200");
    expect(formatJPY("3500000")).toBe("￥3,500,000");
  });

  it("formats zero and negative values", () => {
    expect(formatJPY(0)).toBe("￥0");
    expect(formatJPY(-5000)).toBe("-￥5,000");
  });

  it("rounds down decimals", () => {
    expect(formatJPY(1234.56)).toBe("￥1,235");
    expect(formatJPY("9876.4")).toBe("￥9,876");
  });

  it("returns dash for empty or invalid values", () => {
    expect(formatJPY("")).toBe("-");
    expect(formatJPY(null)).toBe("-");
    expect(formatJPY(undefined)).toBe("-");
    expect(formatJPY("abc")).toBe("-");
  });
});
