"use client";

import { LogOut } from "lucide-react";
import type { ReactNode } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

import { LoginScreen } from "@/components/auth/login-screen";
import { ChatPanel } from "@/components/chat/chat-panel";
import { WorkPanel } from "@/components/layout/panel";
import { Sidebar } from "@/components/layout/sidebar";
import { ResultsView } from "@/components/results/results-view";
import { StrategyView } from "@/components/strategy/strategy-view";
import { BackendStatus } from "@/components/system/backend-status";
import { useAuthStore } from "@/store/auth-store";

function ResizeHandle() {
  return (
    <PanelResizeHandle className="group w-px bg-line transition-colors data-[resize-handle-state=drag]:bg-signal hover:bg-line-bright" />
  );
}

/** Top-level workspace frame: rail, top bar, and three resizable columns. */
export function AppShell({ children }: { children: ReactNode }) {
  const token = useAuthStore((s) => s.token);
  const clearToken = useAuthStore((s) => s.clearToken);

  if (!token) {
    return <LoginScreen />;
  }

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-void">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-11 shrink-0 items-center justify-between border-b border-line px-4">
          <div className="flex items-baseline gap-2">
            <span className="text-[13px] font-semibold">AI Strategy Builder</span>
            <span className="text-[12px] text-ink-faint">Untitled strategy</span>
          </div>
          <div className="flex items-center gap-3">
            <BackendStatus />
            <button
              type="button"
              onClick={clearToken}
              title="Log out"
              className="flex h-7 w-7 items-center justify-center rounded-md text-ink-faint transition-colors hover:bg-raised hover:text-ink-dim"
            >
              <LogOut size={15} strokeWidth={1.75} />
              <span className="sr-only">Log out</span>
            </button>
          </div>
        </header>

        <PanelGroup
          direction="horizontal"
          autoSaveId="workspace-layout"
          className="min-h-0 flex-1"
        >
          <Panel defaultSize={30} minSize={20} order={1}>
            <WorkPanel title="Chat">
              <ChatPanel />
            </WorkPanel>
          </Panel>

          <ResizeHandle />

          <Panel defaultSize={40} minSize={25} order={2}>
            <WorkPanel title="Strategy" hint="spec">
              <StrategyView />
            </WorkPanel>
          </Panel>

          <ResizeHandle />

          <Panel defaultSize={30} minSize={20} order={3}>
            <WorkPanel title="Results">
              <ResultsView />
            </WorkPanel>
          </Panel>
        </PanelGroup>

        {children}
      </div>
    </div>
  );
}