/** Types mirroring the backend backtest schemas (app/schemas/backtest.py). */

export interface IndicatorSpec {
  name: string;
  type: string;
  params: Record<string, number>;
}

export interface RuleSpec {
  left: string;
  comparator: string;
  right: string;
}

export interface RiskSpec {
  position_size_pct: number;
  stop_loss_pct: number | null;
  take_profit_pct: number | null;
}

export interface StrategySpec {
  name: string;
  symbol: string;
  timeframe: string;
  direction: string;
  indicators: IndicatorSpec[];
  entry_rules: RuleSpec[];
  exit_rules: RuleSpec[];
  risk: RiskSpec;
  rationale: string;
}

export interface BacktestMetrics {
  total_return_pct: number;
  annualized_return_pct: number;
  sharpe_ratio: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  num_trades: number;
  exposure_pct: number;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface BacktestResult {
  id: string;
  symbol: string;
  timeframe: string;
  spec: StrategySpec;
  metrics: BacktestMetrics;
  equity_curve: EquityPoint[];
  trades: number[];
  initial_capital: number;
  final_equity: number;
  created_at: string;
}

/** Request payload — exactly one of description or spec, matching the backend. */
export interface BacktestRequest {
  description?: string;
  spec?: StrategySpec;
  initial_capital?: number;
}