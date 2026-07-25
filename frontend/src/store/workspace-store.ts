/**
 * Shared workspace state connecting the chat, strategy, and results panels.
 *
 * Panels stay decoupled: chat writes the latest result and messages here; the
 * strategy and results panels subscribe and render. No panel imports another.
 */

import { create } from "zustand";

import type { BacktestResult } from "@/types/backtest";

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
}

interface WorkspaceState {
  messages: ChatMessage[];
  isRunning: boolean;
  result: BacktestResult | null;
  error: string | null;

  addMessage: (role: ChatRole, content: string) => void;
  setRunning: (running: boolean) => void;
  setResult: (result: BacktestResult) => void;
  setError: (error: string | null) => void;
}

let messageCounter = 0;
const nextId = (): string => {
  messageCounter += 1;
  return `msg-${messageCounter}`;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  messages: [],
  isRunning: false,
  result: null,
  error: null,

  addMessage: (role, content) =>
    set((state) => ({
      messages: [...state.messages, { id: nextId(), role, content }],
    })),
  setRunning: (isRunning) => set({ isRunning }),
  setResult: (result) => set({ result, error: null }),
  setError: (error) => set({ error }),
}));