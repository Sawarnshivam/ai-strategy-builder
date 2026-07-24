"use client";

import { FlaskConical, LayoutGrid, MessagesSquare, Settings2 } from "lucide-react";
import { useState } from "react";

const NAV_ITEMS = [
  { id: "build", label: "Build", icon: MessagesSquare },
  { id: "library", label: "Library", icon: LayoutGrid },
  { id: "runs", label: "Runs", icon: FlaskConical },
] as const;

type NavId = (typeof NAV_ITEMS)[number]["id"];

/** Icon rail for switching workspace sections. */
export function Sidebar() {
  // TODO(module-10): drive the active section from the router once pages exist.
  const [active, setActive] = useState<NavId>("build");

  return (
    <nav
      aria-label="Workspace sections"
      className="flex w-14 shrink-0 flex-col items-center gap-1 border-r border-line bg-panel py-3"
    >
      <div className="mb-4 flex h-8 w-8 items-center justify-center rounded-md bg-signal">
        <span className="text-sm font-semibold text-void">Q</span>
      </div>

      {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
        const isActive = active === id;
        return (
          <button
            key={id}
            type="button"
            title={label}
            aria-current={isActive ? "page" : undefined}
            onClick={() => setActive(id)}
            className={`flex h-9 w-9 items-center justify-center rounded-md transition-colors ${
              isActive
                ? "bg-raised text-signal"
                : "text-ink-faint hover:bg-raised hover:text-ink-dim"
            }`}
          >
            <Icon size={17} strokeWidth={1.75} />
            <span className="sr-only">{label}</span>
          </button>
        );
      })}

      <button
        type="button"
        title="Settings"
        className="mt-auto flex h-9 w-9 items-center justify-center rounded-md text-ink-faint transition-colors hover:bg-raised hover:text-ink-dim"
      >
        <Settings2 size={17} strokeWidth={1.75} />
        <span className="sr-only">Settings</span>
      </button>
    </nav>
  );
}