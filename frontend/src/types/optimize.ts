/** Types mirroring the backend optimize schemas (app/schemas/optimize.py). */

import type { BacktestMetrics, StrategySpec } from "@/types/backtest";

export interface SweepRequest {
  spec: StrategySpec;
  indicator_name: string;
  param: string;
  start: number;
  stop: number;
  step: number;
  rank_by: string;
  initial_capital?: number;
}

export interface SweepPoint {
  value: number;
  metrics: BacktestMetrics;
  final_equity: number;
}

export interface SweepResponse {
  indicator_name: string;
  param: string;
  rank_by: string;
  best_value: number;
  points: SweepPoint[];
}