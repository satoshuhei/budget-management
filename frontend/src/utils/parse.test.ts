import { describe, expect, it } from "vitest";
import { safeJsonParse } from "./parse";

describe("safeJsonParse", () => {
  it("parses valid json", () => {
    expect(safeJsonParse("{\"a\":1}", {} as { a: number })).toEqual({ a: 1 });
  });

  it("returns fallback on invalid json", () => {
    expect(safeJsonParse("{bad}", { ok: true })).toEqual({ ok: true });
  });

  it("returns fallback on empty", () => {
    expect(safeJsonParse(null, { ok: true })).toEqual({ ok: true });
  });

  it("parses array json", () => {
    expect(safeJsonParse("[1,2,3]", [] as number[])).toEqual([1, 2, 3]);
  });
});
