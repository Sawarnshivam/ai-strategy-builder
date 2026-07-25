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

import { CHART_COLORS, shortDate } from "@/components/results/chart-theme";
import type { DrawdownPoint } from "@/lib/drawdown";

interface TooltipEntry {
  payload: DrawdownPoint;
}

function DrawdownTooltip({
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
      <div className="tabular text-short">{point.drawdown}%</div>
      <div className="text-ink-faint">{shortDate(point.timestamp)}</div>
    </div>
  );
}

/** Underwater (drawdown) chart, filled red below the zero line. */
export function DrawdownChart({ data }: { data: DrawdownPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={90}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
        <defs>
          <linearGradient id="ddFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={CHART_COLORS.short} stopOpacity={0} />
            <stop offset="100%" stopColor={CHART_COLORS.short} stopOpacity={0.4} />
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
          tickFormatter={(value: number) => `${value}%`}
          tick={{ fill: CHART_COLORS.axis, fontSize: 10 }}
          stroke={CHART_COLORS.grid}
          width={44}
          domain={["auto", 0]}
        />
        <Tooltip content={<DrawdownTooltip />} />
        <Area
          type="monotone"
          dataKey="drawdown"
          stroke={CHART_COLORS.short}
          strokeWidth={1.5}
          fill="url(#ddFill)"
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}