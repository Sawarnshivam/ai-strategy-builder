"use client";

import { useWorkspaceStore } from "@/store/workspace-store";

/** Shows the generated spec as formatted JSON, or a placeholder. */
export function StrategyView() {
  const result = useWorkspaceStore((s) => s.result);

  if (!result) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <p className="max-w-[26ch] text-center text-[13px] leading-relaxed text-ink-faint">
          The generated strategy spec will appear here once you run a backtest.
        </p>
      </div>
    );
  }

  return (
    <pre className="h-full overflow-auto p-3 font-mono text-[12px] leading-relaxed text-ink-dim">
      {JSON.stringify(result.spec, null, 2)}
    </pre>
  );
}