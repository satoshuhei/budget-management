import { safeJsonParse } from "./parse";
import { api } from "../services/api";

export interface ClientErrorLog {
  id: string;
  message: string;
  stack?: string;
  context?: string;
  info?: Record<string, unknown>;
  createdAt: string;
}

const STORAGE_KEY = "client-error-logs";
const MAX_LOGS = 50;

const toError = (err: unknown) => {
  if (err instanceof Error) return err;
  if (typeof err === "string") return new Error(err);
  return new Error("Unknown error");
};

export const getClientErrorLogs = (): ClientErrorLog[] => {
  const raw = localStorage.getItem(STORAGE_KEY);
  return safeJsonParse<ClientErrorLog[]>(raw, []);
};

export const clearClientErrorLogs = () => {
  localStorage.removeItem(STORAGE_KEY);
};

export const logClientError = (err: unknown, context?: string, info?: Record<string, unknown>) => {
  const error = toError(err);
  const log: ClientErrorLog = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    message: error.message,
    stack: error.stack,
    context,
    info,
    createdAt: new Date().toISOString()
  };
  const logs = getClientErrorLogs();
  logs.unshift(log);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(logs.slice(0, MAX_LOGS)));

  void api.post("/api/client-logs", {
    message: log.message,
    stack: log.stack,
    context: log.context,
    info: log.info,
    createdAt: log.createdAt
  }).catch(() => undefined);
};

export const registerGlobalErrorHandlers = () => {
  window.addEventListener("error", (event) => {
    logClientError(event.error ?? event.message, "window.error", {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    });
  });

  window.addEventListener("unhandledrejection", (event) => {
    logClientError(event.reason, "unhandledrejection");
  });
};
