"use client";

/** Scrollable list of per-trade P&L percentages, colour-coded. */
export function TradeList({ trades }: { trades: number[] }) {
  if (trades.length === 0) {
    return (
      <p className="px-1 py-2 text-[11px] text-ink-faint">
        No closed trades in this run.
      </p>
    );
  }

  return (
    <div className="max-h-40 overflow-auto">
      <table className="w-full text-[11px]">
        <thead className="sticky top-0 bg-panel">
          <tr className="text-ink-faint">
            <th className="px-1 py-1 text-left font-medium">#</th>
            <th className="px-1 py-1 text-right font-medium">P&amp;L %</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((pnl, index) => (
            <tr key={index} className="border-t border-line">
              <td className="px-1 py-1 text-ink-faint">{index + 1}</td>
              <td
                className={`tabular px-1 py-1 text-right ${
                  pnl >= 0 ? "text-long" : "text-short"
                }`}
              >
                {pnl >= 0 ? "+" : ""}
                {pnl.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}