"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/store/workspace-store";

/** Scrolling transcript of chat messages. */
export function MessageList({ messages }: { messages: ChatMessage[] }) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <p className="max-w-[28ch] text-center text-[13px] leading-relaxed text-ink-faint">
          Describe a strategy — &ldquo;momentum BTC with RSI and EMA&rdquo; — or paste a spec to run
          a backtest.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-3">
      {messages.map((message) => (
        <div
          key={message.id}
          className={
            message.role === "user"
              ? "self-end rounded-lg rounded-br-sm bg-raised px-3 py-2 text-[13px] text-ink"
              : "self-start rounded-lg rounded-bl-sm border border-line px-3 py-2 text-[13px] text-ink-dim"
          }
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}