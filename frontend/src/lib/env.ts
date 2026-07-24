/**
 * Validated public environment configuration.
 *
 * Reading env vars through this module (rather than process.env inline) means a
 * missing variable fails loudly at import time instead of producing a fetch to
 * "undefined/strategies" at runtime.
 */

function required(name: string, value: string | undefined): string {
  if (!value) {
    throw new Error(
      `Missing environment variable ${name}. Copy .env.local.example to .env.local.`,
    );
  }
  return value;
}

export const env = {
  apiBaseUrl: required(
    "NEXT_PUBLIC_API_BASE_URL",
    process.env.NEXT_PUBLIC_API_BASE_URL,
  ),
} as const;