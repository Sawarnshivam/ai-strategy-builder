"use client";

import { useWorkspaceStore } from "@/store/workspace-store";
import type { BacktestMetrics } from "@/types/backtest";

const METRIC_LABELS: { key: keyof BacktestMetrics; label: string; suffix: string }[] = [
  { key: "total_return_pct", label: "Total Return", suffix: "%" },
  { key: "annualized_return_pct", label: "Annualized", suffix: "%" },
  { key: "sharpe_ratio", label: "Sharpe", suffix: "" },
  { key: "max_drawdown_pct", label: "Max Drawdown", suffix: "%" },
  { key: "win_rate_pct", label: "Win Rate", suffix: "%" },
  { key: "exposure_pct", label: "Exposure", suffix: "%" },
  { key: "num_trades", label: "Trades", suffix: "" },
];

/** Renders metrics as a grid; a real chart arrives in the dashboard module. */
export function ResultsView() {
  const result = useWorkspaceStore((s) => s.result);

  if (!result) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <p className="max-w-[26ch] text-center text-[13px] leading-relaxed text-ink-faint">
          Run a backtest to see equity, drawdown and trade statistics.
        </p>
      </div>
    );
  }

  return (
    <div className="p-3">
      <div className="mb-3 flex items-baseline justify-between">
        <span className="text-[13px] font-medium text-ink">{result.spec.name}</span>
        <span className="tabular text-[11px] text-ink-faint">
          ${result.final_equity.toFixed(0)} / ${result.initial_capital.toFixed(0)}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {METRIC_LABELS.map(({ key, label, suffix }) => {
          const value = result.metrics[key];
          const isReturn = key === "total_return_pct" || key === "annualized_return_pct";
          const tone =
            isReturn && typeof value === "number"
              ? value >= 0
                ? "text-long"
                : "text-short"
              : "text-ink";
          return (
            <div key={key} className="rounded-md border border-line bg-panel p-2">
              <div className="text-[10px] uppercase tracking-wide text-ink-faint">{label}</div>
              <div className={`tabular text-[15px] ${tone}`}>
                {value}
                {suffix}
              </div>
            </div>
          );
        })}
      </div>

      {/* TODO(module-11): replace this grid with an interactive equity chart. */}
      <p className="mt-3 text-[11px] text-ink-faint">
        {result.equity_curve.length} equity points · interactive chart in the dashboard module.
      </p>
    </div>
  );
}