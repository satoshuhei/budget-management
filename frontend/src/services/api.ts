import axios from "axios";
import { getAuthProfile } from "../storage/auth";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
});

api.interceptors.request.use((config) => {
  const profile = getAuthProfile();
  if (profile) {
    config.headers["X-User"] = profile.username;
    config.headers["X-Role"] = profile.role;
  }
  return config;
});
