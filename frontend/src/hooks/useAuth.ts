import { useEffect, useState } from "react";
import { api } from "../services/api";
import { AuthProfile, clearAuthProfile, getAuthProfile, saveAuthProfile } from "../storage/auth";

interface LoginResponse {
  username: string;
  role: string;
}

export const useAuth = () => {
  const [profile, setProfile] = useState<AuthProfile | null>(getAuthProfile());
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const stored = getAuthProfile();
    if (!stored) {
      setProfile(null);
      setChecking(false);
      return;
    }
    api
      .get<LoginResponse>("/api/auth/me")
      .then((res) => {
        const nextProfile = { username: res.data.username, role: res.data.role } as AuthProfile;
        saveAuthProfile(nextProfile);
        setProfile(nextProfile);
      })
      .catch(() => {
        clearAuthProfile();
        setProfile(null);
      })
      .finally(() => setChecking(false));
  }, []);

  const login = async (username: string, password: string) => {
    const response = await api.post<LoginResponse>("/api/auth/login", { username, password });
    const nextProfile = { username: response.data.username, role: response.data.role };
    saveAuthProfile(nextProfile);
    setProfile(nextProfile);
  };

  const logout = () => {
    clearAuthProfile();
    setProfile(null);
    window.location.href = "/login";
  };

  return {
    profile,
    isAuthenticated: Boolean(profile),
    isChecking: checking,
    login,
    logout
  };
};
