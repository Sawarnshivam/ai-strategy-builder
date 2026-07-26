/** API calls for authentication. */

import { apiRequest } from "@/lib/api-client";
import type { Credentials, TokenResponse } from "@/types/auth";

/** Register a new account and receive a token. */
export function signup(credentials: Credentials): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/signup", {
    method: "POST",
    body: credentials,
  });
}

/** Log in and receive a token. */
export function login(credentials: Credentials): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: credentials,
  });
}