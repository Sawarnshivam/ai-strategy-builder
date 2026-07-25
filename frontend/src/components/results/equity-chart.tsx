"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS, compactCurrency, shortDate } from "@/components/results/chart-theme";
import type { EquityPoint } from "@/types/backtest";

interface EquityChartProps {
  data: EquityPoint[];
  initialCapital: number;
}

interface TooltipEntry {
  value: number;
  payload: EquityPoint;
}

function EquityTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipEntry[];
}) {
  if (!active || !payload?.length) {
    return null;
  }
  const point = payload[0].payload;
  return (
    <div className="rounded-md border border-line bg-raised px-2 py-1 text-[11px]">
      <div className="tabular text-ink">{compactCurrency(point.equity)}</div>
      <div className="text-ink-faint">{shortDate(point.timestamp)}</div>
    </div>
  );
}

/** Interactive equity curve as a filled area chart. */
export function EquityChart({ data, initialCapital }: EquityChartProps) {
  const gain = data.length > 0 && data[data.length - 1].equity >= initialCapital;
  const stroke = gain ? CHART_COLORS.long : CHART_COLORS.short;

  return (
    <ResponsiveContainer width="100%" height={160}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
        <defs>
          <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={stroke} stopOpacity={0.35} />
            <stop offset="100%" stopColor={stroke} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="2 4" vertical={false} />
        <XAxis
          dataKey="timestamp"
          tickFormatter={shortDate}
          tick={{ fill: CHART_COLORS.axis, fontSize: 10 }}
          stroke={CHART_COLORS.grid}
          minTickGap={40}
        />
        <YAxis
          tickFormatter={compactCurrency}
          tick={{ fill: CHART_COLORS.axis, fontSize: 10 }}
          stroke={CHART_COLORS.grid}
          width={44}
          domain={["auto", "auto"]}
        />
        <Tooltip content={<EquityTooltip />} />
        <Area
          type="monotone"
          dataKey="equity"
          stroke={stroke}
          strokeWidth={1.5}
          fill="url(#equityFill)"
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}