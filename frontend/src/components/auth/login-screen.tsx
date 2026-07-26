"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { ApiError } from "@/lib/api-client";
import { login, signup } from "@/lib/auth";
import { useAuthStore } from "@/store/auth-store";

type Mode = "login" | "signup";

/** Full-screen auth gate shown when there is no token. */
export function LoginScreen() {
  const setToken = useAuthStore((s) => s.setToken);
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (): Promise<void> => {
    setBusy(true);
    setError(null);
    try {
      const call = mode === "login" ? login : signup;
      const { access_token } = await call({ email, password });
      setToken(access_token);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex h-dvh w-full items-center justify-center bg-void">
      <div className="w-full max-w-xs rounded-xl border border-line bg-panel p-6">
        <div className="mb-5 flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-signal">
            <span className="text-[13px] font-semibold text-void">Q</span>
          </div>
          <span className="text-[14px] font-semibold text-ink">AI Strategy Builder</span>
        </div>

        <div className="mb-4 flex gap-1">
          {(["login", "signup"] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setMode(option)}
              className={`flex-1 rounded-md px-2 py-1 text-[12px] transition-colors ${
                mode === option ? "bg-raised text-signal" : "text-ink-faint hover:text-ink-dim"
              }`}
            >
              {option === "login" ? "Log in" : "Sign up"}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="rounded-md border border-line bg-void px-3 py-2 text-[13px] text-ink placeholder:text-ink-faint focus:border-line-bright focus:outline-none"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void submit();
            }}
            placeholder={mode === "signup" ? "Password (min 8 chars)" : "Password"}
            className="rounded-md border border-line bg-void px-3 py-2 text-[13px] text-ink placeholder:text-ink-faint focus:border-line-bright focus:outline-none"
          />
        </div>

        {error && <p className="mt-2 text-[11px] text-short">{error}</p>}

        <button
          type="button"
          onClick={() => void submit()}
          disabled={busy || !email || !password}
          className="mt-4 flex w-full items-center justify-center gap-1 rounded-md bg-signal px-3 py-2 text-[13px] font-medium text-void disabled:opacity-50"
        >
          {busy ? <Loader2 size={14} className="animate-spin" /> : null}
          {mode === "login" ? "Log in" : "Create account"}
        </button>
      </div>
    </div>
  );
}