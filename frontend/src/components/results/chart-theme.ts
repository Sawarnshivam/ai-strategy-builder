/** Shared styling constants for the dashboard charts.

 * Reading colours from the CSS custom properties keeps charts in lockstep with
 * the theme tokens in globals.css instead of duplicating hex values.
 */

export const CHART_COLORS = {
  grid: "var(--color-line)",
  axis: "var(--color-ink-faint)",
  long: "var(--color-long)",
  short: "var(--color-short)",
  signal: "var(--color-signal)",
  panel: "var(--color-panel)",
  ink: "var(--color-ink)",
} as const;

/** Format an ISO timestamp to a short axis label (date only). */
export function shortDate(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

/** Format a number as a currency-ish compact string for the Y axis. */
export function compactCurrency(value: number): string {
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(1)}k`;
  }
  return `$${value.toFixed(0)}`;
}