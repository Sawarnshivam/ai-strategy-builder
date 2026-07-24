"use client";

import { useEffect, useState } from "react";

import { apiRequest } from "@/lib/api-client";
import type { HealthResponse } from "@/types/health";

const POLL_INTERVAL_MS = 15_000;

type Connection =
  | { state: "checking" }
  | { state: "online"; latencyMs: number; environment: string }
  | { state: "offline" };

/** Probe the backend once and report the result, without touching React state. */
async function probe(): Promise<Connection> {
  const startedAt = performance.now();
  try {
    const health = await apiRequest<HealthResponse>("/health");
    return {
      state: "online",
      latencyMs: Math.round(performance.now() - startedAt),
      environment: health.environment,
    };
  } catch {
    return { state: "offline" };
  }
}

/** Live indicator for backend reachability, polled on an interval. */
export function BackendStatus() {
  const [connection, setConnection] = useState<Connection>({ state: "checking" });

  useEffect(() => {
    let active = true;

    const run = async () => {
      const result = await probe();
      if (active) {
        setConnection(result);
      }
    };

    void run();
    const timer = setInterval(() => void run(), POLL_INTERVAL_MS);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  const dotClass =
    connection.state === "online"
      ? "bg-long"
      : connection.state === "offline"
        ? "bg-short"
        : "bg-ink-faint";

  return (
    <div className="flex items-center gap-2 rounded-full border border-line bg-raised px-3 py-1">
      <span className="relative flex h-1.5 w-1.5">
        {connection.state === "online" && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-long opacity-60" />
        )}
        <span className={`relative inline-flex h-1.5 w-1.5 rounded-full ${dotClass}`} />
      </span>
      <span className="tabular text-[11px] text-ink-dim">
        {connection.state === "online" && `api ${connection.environment} · ${connection.latencyMs}ms`}
        {connection.state === "offline" && "api unreachable"}
        {connection.state === "checking" && "connecting"}
      </span>
    </div>
  );
}