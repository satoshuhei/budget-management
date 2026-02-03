import { describe, expect, it, beforeEach } from "vitest";
import { clearClientErrorLogs, getClientErrorLogs, logClientError } from "./errorLogger";

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

describe("errorLogger", () => {
  it("stores logs in localStorage", () => {
    logClientError(new Error("boom"), "test");
    const logs = getClientErrorLogs();
    expect(logs).toHaveLength(1);
    expect(logs[0].message).toBe("boom");
    expect(logs[0].context).toBe("test");
  });

  it("clears logs", () => {
    logClientError("oops");
    clearClientErrorLogs();
    expect(getClientErrorLogs()).toHaveLength(0);
  });
});
