import type { ReactNode } from "react";

interface WorkPanelProps {
  title: string;
  hint?: string;
  children: ReactNode;
}

/** A titled surface inside the resizable workspace. */
export function WorkPanel({ title, hint, children }: WorkPanelProps) {
  return (
    <section className="flex h-full flex-col overflow-hidden bg-panel">
      <header className="flex h-9 shrink-0 items-center justify-between border-b border-line px-3">
        <h2 className="text-[11px] font-medium uppercase tracking-[0.08em] text-ink-dim">
          {title}
        </h2>
        {hint && <span className="tabular text-[11px] text-ink-faint">{hint}</span>}
      </header>
      <div className="min-h-0 flex-1 overflow-auto">{children}</div>
    </section>
  );
}

/** Placeholder body shown until a panel's feature module lands. */
export function EmptyPanel({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <p className="max-w-[26ch] text-center text-[13px] leading-relaxed text-ink-faint">
        {children}
      </p>
    </div>
  );
}