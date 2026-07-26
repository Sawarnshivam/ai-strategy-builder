"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { ApiError } from "@/lib/api-client";
import { runSweep } from "@/lib/optimize";
import type { StrategySpec } from "@/types/backtest";
import type { SweepPoint } from "@/types/optimize";

const RANK_OPTIONS = [
  { value: "sharpe_ratio", label: "Sharpe" },
  { value: "total_return_pct", label: "Return" },
  { value: "max_drawdown_pct", label: "Drawdown" },
  { value: "win_rate_pct", label: "Win rate" },
] as const;

interface OptimizePanelProps {
  spec: StrategySpec;
}

/** Inline parameter-sweep launcher and ranked-result table. */
export function OptimizePanel({ spec }: OptimizePanelProps) {
  const firstIndicator = spec.indicators[0];
  const [indicatorName, setIndicatorName] = useState(firstIndicator?.name ?? "");
  const [param, setParam] = useState("period");
  const [start, setStart] = useState(5);
  const [stop, setStop] = useState(30);
  const [step, setStep] = useState(5);
  const [rankBy, setRankBy] = useState<string>("sharpe_ratio");

  const [running, setRunning] = useState(false);
  const [points, setPoints] = useState<SweepPoint[] | null>(null);
  const [bestValue, setBestValue] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const launch = async (): Promise<void> => {
    setRunning(true);
    setError(null);
    try {
      const response = await runSweep({
        spec,
        indicator_name: indicatorName,
        param,
        start,
        stop,
        step,
        rank_by: rankBy,
      });
      setPoints(response.points);
      setBestValue(response.best_value);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sweep failed.");
      setPoints(null);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="rounded-md border border-line bg-panel p-2">
      <div className="mb-2 text-[10px] uppercase tracking-wide text-ink-faint">
        Optimize
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <label className="flex flex-col gap-1">
          <span className="text-ink-faint">Indicator</span>
          <select
            value={indicatorName}
            onChange={(e) => setIndicatorName(e.target.value)}
            className="rounded border border-line bg-void px-1 py-1 text-ink"
          >
            {spec.indicators.map((ind) => (
              <option key={ind.name} value={ind.name}>
                {ind.name}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-ink-faint">Param</span>
          <input
            value={param}
            onChange={(e) => setParam(e.target.value)}
            className="rounded border border-line bg-void px-1 py-1 font-mono text-ink"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-ink-faint">Start</span>
          <input
            type="number"
            value={start}
            onChange={(e) => setStart(Number(e.target.value))}
            className="tabular rounded border border-line bg-void px-1 py-1 text-ink"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-ink-faint">Stop</span>
          <input
            type="number"
            value={stop}
            onChange={(e) => setStop(Number(e.target.value))}
            className="tabular rounded border border-line bg-void px-1 py-1 text-ink"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-ink-faint">Step</span>
          <input
            type="number"
            value={step}
            min={0.0001}
            onChange={(e) => setStep(Number(e.target.value))}
            className="tabular rounded border border-line bg-void px-1 py-1 text-ink"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-ink-faint">Rank by</span>
          <select
            value={rankBy}
            onChange={(e) => setRankBy(e.target.value)}
            className="rounded border border-line bg-void px-1 py-1 text-ink"
          >
            {RANK_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={() => void launch()}
        disabled={running || !indicatorName}
        className="mt-2 flex w-full items-center justify-center gap-1 rounded-md bg-signal px-2 py-1 text-[12px] font-medium text-void disabled:opacity-50"
      >
        {running ? <Loader2 size={13} className="animate-spin" /> : null}
        {running ? "Sweeping…" : "Run sweep"}
      </button>

      {error && <p className="mt-2 text-[11px] text-short">{error}</p>}

      {points && (
        <table className="mt-2 w-full text-[11px]">
          <thead className="text-ink-faint">
            <tr>
              <th className="px-1 py-1 text-left font-medium">{param}</th>
              <th className="px-1 py-1 text-right font-medium">Return</th>
              <th className="px-1 py-1 text-right font-medium">Sharpe</th>
              <th className="px-1 py-1 text-right font-medium">Max DD</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p) => {
              const best = p.value === bestValue;
              return (
                <tr
                  key={p.value}
                  className={`border-t border-line ${best ? "text-signal" : "text-ink-dim"}`}
                >
                  <td className="tabular px-1 py-1">{p.value}</td>
                  <td className="tabular px-1 py-1 text-right">
                    {p.metrics.total_return_pct}%
                  </td>
                  <td className="tabular px-1 py-1 text-right">{p.metrics.sharpe_ratio}</td>
                  <td className="tabular px-1 py-1 text-right">
                    {p.metrics.max_drawdown_pct}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}