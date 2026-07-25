"use client";

import { CornerDownLeft, Loader2 } from "lucide-react";
import { useState } from "react";

type Mode = "describe" | "spec";

interface ChatInputProps {
  disabled: boolean;
  onSubmit: (mode: Mode, text: string) => void;
}

/** Composer with a describe/spec mode toggle and a submit action. */
export function ChatInput({ disabled, onSubmit }: ChatInputProps) {
  const [mode, setMode] = useState<Mode>("describe");
  const [text, setText] = useState("");

  const placeholder =
    mode === "describe"
      ? "Describe a strategy in plain language…"
      : 'Paste a strategy spec as JSON…';

  const submit = (): void => {
    const trimmed = text.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSubmit(mode, trimmed);
    setText("");
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-line p-3">
      <div className="mb-2 flex gap-1">
        {(["describe", "spec"] as const).map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setMode(option)}
            className={`rounded-md px-2 py-1 text-[11px] transition-colors ${
              mode === option
                ? "bg-raised text-signal"
                : "text-ink-faint hover:text-ink-dim"
            }`}
          >
            {option === "describe" ? "Describe" : "Spec (JSON)"}
          </button>
        ))}
      </div>

      <div className="relative">
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          rows={mode === "spec" ? 6 : 3}
          disabled={disabled}
          className="w-full resize-none rounded-lg border border-line bg-panel px-3 py-2 pr-10 font-mono text-[12px] text-ink placeholder:text-ink-faint focus:border-line-bright focus:outline-none disabled:opacity-60"
        />
        <button
          type="button"
          onClick={submit}
          disabled={disabled || !text.trim()}
          title="Run (Ctrl/Cmd + Enter)"
          className="absolute bottom-2 right-2 flex h-6 w-6 items-center justify-center rounded-md bg-signal text-void transition-opacity disabled:opacity-40"
        >
          {disabled ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <CornerDownLeft size={14} />
          )}
        </button>
      </div>
      <p className="mt-1 text-[10px] text-ink-faint">
        {mode === "describe"
          ? "Natural language needs an API key on the backend."
          : "Runs directly — no API key required."}{" "}
        Ctrl/Cmd + Enter to run.
      </p>
    </div>
  );
}