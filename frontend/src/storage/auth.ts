import { safeJsonParse } from "../utils/parse";

export interface AuthProfile {
  username: string;
  role: string;
}

const STORAGE_KEY = "budget-auth-profile";

export const saveAuthProfile = (profile: AuthProfile) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
};

export const getAuthProfile = (): AuthProfile | null => {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  return safeJsonParse(raw, null);
};

export const clearAuthProfile = () => {
  localStorage.removeItem(STORAGE_KEY);
};
