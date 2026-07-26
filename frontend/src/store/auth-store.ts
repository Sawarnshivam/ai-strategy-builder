/**
 * Authentication state: the JWT token and derived login status.
 *
 * The token is mirrored to localStorage so a refresh keeps the session, and
 * read back on init. api-client reads getToken() to attach the header.
 */

import { create } from "zustand";

const STORAGE_KEY = "asb-auth-token";

function readStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(STORAGE_KEY);
}

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  clearToken: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: readStoredToken(),
  setToken: (token) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, token);
    }
    set({ token });
  },
  clearToken: () => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(STORAGE_KEY);
    }
    set({ token: null });
  },
}));

/** Non-hook accessor so non-React modules (api-client) can read the token. */
export function getToken(): string | null {
  return useAuthStore.getState().token;
}