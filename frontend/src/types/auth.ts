/** Types for the auth endpoints (app/schemas/auth.py). */

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Credentials {
  email: string;
  password: string;
}