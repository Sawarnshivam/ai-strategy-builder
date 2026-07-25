/** Derives a drawdown series from an equity curve. */

import type { EquityPoint } from "@/types/backtest";

export interface DrawdownPoint {
  timestamp: string;
  /** Drawdown as a negative percentage from the running peak (0 at highs). */
  drawdown: number;
}

/** Compute percent drawdown from the running maximum at each point. */
export function computeDrawdown(curve: EquityPoint[]): DrawdownPoint[] {
  let peak = Number.NEGATIVE_INFINITY;
  return curve.map((point) => {
    peak = Math.max(peak, point.equity);
    const drawdown = peak > 0 ? ((point.equity - peak) / peak) * 100 : 0;
    return { timestamp: point.timestamp, drawdown: Number(drawdown.toFixed(3)) };
  });
}