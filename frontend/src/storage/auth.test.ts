import { describe, expect, it, beforeEach } from "vitest";
import { clearAuthProfile, getAuthProfile, saveAuthProfile } from "./auth";

beforeEach(() => {
  const store = new Map<string, string>();
  const mockStorage = {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, value);
    },
    removeItem: (key: string) => {
      store.delete(key);
    },
    clear: () => {
      store.clear();
    }
  };
  Object.defineProperty(globalThis, "localStorage", {
    value: mockStorage,
    configurable: true
  });
  globalThis.localStorage.clear();
});

describe("auth storage", () => {
  it("saves and loads profile", () => {
    saveAuthProfile({ username: "alice", role: "USER" });
    expect(getAuthProfile()).toEqual({ username: "alice", role: "USER" });
  });

  it("returns null on invalid json", () => {
    localStorage.setItem("budget-auth-profile", "{bad}");
    expect(getAuthProfile()).toBeNull();
  });

  it("clears profile", () => {
    saveAuthProfile({ username: "alice", role: "USER" });
    clearAuthProfile();
    expect(getAuthProfile()).toBeNull();
  });
});
