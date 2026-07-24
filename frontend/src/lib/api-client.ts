/**
 * Thin typed wrapper around fetch for talking to the FastAPI backend.
 *
 * Centralising this gives one place to add auth headers, retries and tracing
 * later, and turns non-2xx responses into a typed error the UI can branch on.
 */

import { env } from "@/lib/env";

const DEFAULT_TIMEOUT_MS = 10_000;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  timeoutMs?: number;
}

/** Perform a JSON request against the API and parse the response. */
export async function apiRequest<T>(
  path: string,
  { body, timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...init }: RequestOptions = {},
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch {
    throw new ApiError(0, "Cannot reach the API. Is the backend running?");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : response.statusText;
    const code =
      payload && typeof payload === "object" && "code" in payload
        ? String((payload as { code: unknown }).code)
        : undefined;
    throw new ApiError(response.status, detail, code);
  }

  return payload as T;
}