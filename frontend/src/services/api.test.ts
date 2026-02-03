import { describe, expect, it } from "vitest";
import { api } from "./api";

describe("api client", () => {
  it("uses default base URL when env is not set", () => {
    expect(api.defaults.baseURL).toBe("http://127.0.0.1:8000");
  });
});
