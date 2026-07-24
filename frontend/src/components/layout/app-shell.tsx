"use client";

import type { ReactNode } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

import { WorkPanel, EmptyPanel } from "@/components/layout/panel";
import { Sidebar } from "@/components/layout/sidebar";
import { BackendStatus } from "@/components/system/backend-status";

function ResizeHandle() {
  return (
    <PanelResizeHandle className="group w-px bg-line transition-colors data-[resize-handle-state=drag]:bg-signal hover:bg-line-bright" />
  );
}

/** Top-level workspace frame: rail, top bar, and three resizable columns. */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-dvh w-full overflow-hidden bg-void">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-11 shrink-0 items-center justify-between border-b border-line px-4">
          <div className="flex items-baseline gap-2">
            <span className="text-[13px] font-semibold">AI Strategy Builder</span>
            <span className="text-[12px] text-ink-faint">Untitled strategy</span>
          </div>
          <BackendStatus />
        </header>

        <PanelGroup
          direction="horizontal"
          autoSaveId="workspace-layout"
          className="min-h-0 flex-1"
        >
          <Panel defaultSize={30} minSize={20} order={1}>
            <WorkPanel title="Chat">
              {/* TODO(module-10): mount the streaming chat interface here. */}
              <EmptyPanel>
                Describe a strategy in plain language to start. Chat arrives in a later module.
              </EmptyPanel>
            </WorkPanel>
          </Panel>

          <ResizeHandle />

          <Panel defaultSize={40} minSize={25} order={2}>
            <WorkPanel title="Strategy" hint="python">
              {/* TODO(module-6): replace with the Monaco editor and generated code. */}
              <EmptyPanel>Generated strategy code will appear here, ready to run.</EmptyPanel>
            </WorkPanel>
          </Panel>

          <ResizeHandle />

          <Panel defaultSize={30} minSize={20} order={3}>
            <WorkPanel title="Results">
              {/* TODO(module-11): render equity curve, metrics and trade list. */}
              <EmptyPanel>Run a backtest to see equity, drawdown and trade statistics.</EmptyPanel>
            </WorkPanel>
          </Panel>
        </PanelGroup>

        {children}
      </div>
    </div>
  );
}