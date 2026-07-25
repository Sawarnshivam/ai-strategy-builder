/** API calls for running and retrieving backtests. */

import { apiRequest } from "@/lib/api-client";
import type { BacktestRequest, BacktestResult } from "@/types/backtest";

/** Run a backtest from a description or a spec. Returns the full result. */
export function runBacktest(request: BacktestRequest): Promise<BacktestResult> {
  return apiRequest<BacktestResult>("/backtests", {
    method: "POST",
    body: request,
  });
}