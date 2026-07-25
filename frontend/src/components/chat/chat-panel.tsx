"use client";

import { runBacktest } from "@/lib/backtests";
import { ApiError } from "@/lib/api-client";
import { useWorkspaceStore } from "@/store/workspace-store";
import type { BacktestRequest, StrategySpec } from "@/types/backtest";

import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";

type Mode = "describe" | "spec";

/** The chat panel: transcript plus composer, wired to the backtest API. */
export function ChatPanel() {
  const messages = useWorkspaceStore((s) => s.messages);
  const isRunning = useWorkspaceStore((s) => s.isRunning);
  const addMessage = useWorkspaceStore((s) => s.addMessage);
  const setRunning = useWorkspaceStore((s) => s.setRunning);
  const setResult = useWorkspaceStore((s) => s.setResult);
  const setError = useWorkspaceStore((s) => s.setError);

  const handleSubmit = async (mode: Mode, text: string): Promise<void> => {
    addMessage("user", text);

    let request: BacktestRequest;
    if (mode === "spec") {
      let parsed: StrategySpec;
      try {
        parsed = JSON.parse(text) as StrategySpec;
      } catch {
        addMessage("assistant", "That spec isn't valid JSON. Check the syntax and try again.");
        return;
      }
      request = { spec: parsed };
    } else {
      request = { description: text };
    }

    setRunning(true);
    setError(null);
    try {
      const result = await runBacktest(request);
      setResult(result);
      const { total_return_pct, num_trades, sharpe_ratio } = result.metrics;
      addMessage(
        "assistant",
        `Backtested ${result.spec.name} on ${result.symbol} (${result.timeframe}).\n` +
          `Return ${total_return_pct}% · Sharpe ${sharpe_ratio} · ${num_trades} trades.`,
      );
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Something went wrong running the backtest.";
      setError(message);
      addMessage("assistant", message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="min-h-0 flex-1 overflow-auto">
        <MessageList messages={messages} />
      </div>
      <ChatInput disabled={isRunning} onSubmit={(mode, text) => void handleSubmit(mode, text)} />
    </div>
  );
}