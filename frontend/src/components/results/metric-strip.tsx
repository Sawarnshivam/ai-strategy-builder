"use client";

import type { BacktestMetrics } from "@/types/backtest";

const ITEMS: { key: keyof BacktestMetrics; label: string; suffix: string; signed?: boolean }[] = [
  { key: "total_return_pct", label: "Return", suffix: "%", signed: true },
  { key: "sharpe_ratio", label: "Sharpe", suffix: "" },
  { key: "max_drawdown_pct", label: "Max DD", suffix: "%" },
  { key: "win_rate_pct", label: "Win", suffix: "%" },
  { key: "num_trades", label: "Trades", suffix: "" },
  { key: "exposure_pct", label: "Expo", suffix: "%" },
];

/** Compact horizontal strip of headline metrics above the charts. */
export function MetricStrip({ metrics }: { metrics: BacktestMetrics }) {
  return (
    <div className="grid grid-cols-3 gap-px overflow-hidden rounded-md border border-line bg-line">
      {ITEMS.map(({ key, label, suffix, signed }) => {
        const value = metrics[key];
        const tone =
          signed && typeof value === "number"
            ? value >= 0
              ? "text-long"
              : "text-short"
            : "text-ink";
        return (
          <div key={key} className="bg-panel px-2 py-1.5">
            <div className="text-[9px] uppercase tracking-wide text-ink-faint">{label}</div>
            <div className={`tabular text-[13px] ${tone}`}>
              {signed && typeof value === "number" && value >= 0 ? "+" : ""}
              {value}
              {suffix}
            </div>
          </div>
        );
      })}
    </div>
  );
}