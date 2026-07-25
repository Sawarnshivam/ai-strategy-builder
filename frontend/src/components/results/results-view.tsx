"use client";

import { useMemo } from "react";

import { DrawdownChart } from "@/components/results/drawdown-chart";
import { EquityChart } from "@/components/results/equity-chart";
import { MetricStrip } from "@/components/results/metric-strip";
import { TradeList } from "@/components/results/trade-list";
import { computeDrawdown } from "@/lib/drawdown";
import { useWorkspaceStore } from "@/store/workspace-store";

/** The results dashboard: metric strip, equity curve, drawdown, and trades. */
export function ResultsView() {
  const result = useWorkspaceStore((s) => s.result);

  const drawdown = useMemo(
    () => (result ? computeDrawdown(result.equity_curve) : []),
    [result],
  );

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
    <div className="flex flex-col gap-3 p-3">
      <div className="flex items-baseline justify-between">
        <span className="text-[13px] font-medium text-ink">{result.spec.name}</span>
        <span className="tabular text-[11px] text-ink-faint">
          ${result.final_equity.toFixed(0)} / ${result.initial_capital.toFixed(0)}
        </span>
      </div>

      <MetricStrip metrics={result.metrics} />

      <section>
        <h3 className="mb-1 text-[10px] uppercase tracking-wide text-ink-faint">Equity</h3>
        <EquityChart data={result.equity_curve} initialCapital={result.initial_capital} />
      </section>

      <section>
        <h3 className="mb-1 text-[10px] uppercase tracking-wide text-ink-faint">Drawdown</h3>
        <DrawdownChart data={drawdown} />
      </section>

      <section>
        <h3 className="mb-1 text-[10px] uppercase tracking-wide text-ink-faint">
          Trades ({result.trades.length})
        </h3>
        <TradeList trades={result.trades} />
      </section>
    </div>
  );
}