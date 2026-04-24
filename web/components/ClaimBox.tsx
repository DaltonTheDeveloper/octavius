"use client";
import { useEffect, useState } from "react";
import { Check, Lock, Key, LogIn } from "lucide-react";

export default function ClaimBox({
  extensionId,
  slug,
  tier,
  hasLicense,
  licenseSource,
  authConfigured,
  signedIn,
  autoCode,
}: {
  extensionId: string;
  slug: string;
  tier: string;
  hasLicense: boolean;
  licenseSource: string | null;
  authConfigured: boolean;
  signedIn: boolean;
  autoCode: string | null;
}) {
  const [code, setCode] = useState(autoCode ?? "");
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle");
  const [msg, setMsg] = useState<string>("");

  useEffect(() => {
    // auto-redeem when user arrives with ?code=XYZ and is signed in
    if (autoCode && signedIn && !hasLicense) {
      void redeem(autoCode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function claimFree() {
    setStatus("loading");
    try {
      const r = await fetch(`/api/license/issue`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ extensionId }),
      });
      const data = await r.json();
      if (!r.ok) {
        setStatus("err");
        setMsg(data.error ?? "could not claim");
        return;
      }
      setStatus("ok");
      setMsg("License issued — run `octavius install " + slug + "`");
      setTimeout(() => window.location.reload(), 900);
    } catch (e) {
      setStatus("err");
      setMsg("network error");
    }
  }

  async function redeem(c: string) {
    setStatus("loading");
    try {
      const r = await fetch(`/api/membership/redeem`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ extensionId, code: c }),
      });
      const data = await r.json();
      if (!r.ok) {
        setStatus("err");
        setMsg(data.error ?? "code rejected");
        return;
      }
      setStatus("ok");
      setMsg("Membership code accepted. You can now install.");
      setTimeout(() => window.location.reload(), 1200);
    } catch {
      setStatus("err");
      setMsg("network error");
    }
  }

  if (hasLicense) {
    return (
      <div className="glass rounded-2xl p-6 border-emerald-500/40">
        <div className="flex items-center gap-2 text-emerald-300 font-semibold">
          <Check size={16} /> Licensed
        </div>
        <div className="mt-2 text-sm text-ink-100/70">
          Source: <code className="text-plasma-300">{licenseSource ?? "free"}</code>
        </div>
        <div className="mt-4 font-mono text-sm bg-ink-950/70 border border-ink-700 rounded-lg p-3 text-plasma-300">
          octavius install {slug}
        </div>
      </div>
    );
  }

  if (!authConfigured) {
    return (
      <div className="glass rounded-2xl p-6 border-rust-500/30">
        <div className="flex items-center gap-2 font-semibold">
          <Lock size={16} /> Login not configured
        </div>
        <p className="mt-2 text-sm text-ink-100/60">
          Set <code>AUTH_SECRET</code>, <code>AUTH_GITHUB_ID</code>, <code>AUTH_GITHUB_SECRET</code> in env to enable sign-in and claims.
        </p>
      </div>
    );
  }

  if (!signedIn) {
    return (
      <div className="glass rounded-2xl p-6">
        <div className="font-semibold">Sign in to claim</div>
        <p className="mt-2 text-sm text-ink-100/60">Everything is free during beta. Auth just tracks which extensions you've claimed.</p>
        <a
          href={`/login?next=/extensions/${slug}`}
          className="mt-4 inline-flex items-center gap-2 w-full justify-center rounded-xl py-2.5 bg-gradient-to-br from-plasma-500 to-rust-500 text-white font-semibold hover:brightness-110 transition"
        >
          <LogIn size={16} /> Sign in
        </a>
      </div>
    );
  }

  return (
    <div className="glass rounded-2xl p-6 space-y-4">
      <div>
        <div className="font-semibold">Claim this extension</div>
        <div className="text-xs text-ink-100/50 mt-1">Free during beta — one click.</div>
      </div>
      <button
        onClick={claimFree}
        disabled={status === "loading"}
        className="w-full inline-flex items-center justify-center gap-2 rounded-xl py-2.5 bg-gradient-to-br from-plasma-500 to-rust-500 text-white font-semibold disabled:opacity-60 hover:brightness-110 transition"
      >
        {status === "loading" ? "Working..." : "Claim for free"}
      </button>

      <div className="relative py-1 text-center text-xs text-ink-100/40 font-mono tracking-widest">
        <span className="bg-ink-900 px-2 relative z-10">OR MEMBERSHIP CODE</span>
        <div className="absolute inset-x-0 top-1/2 h-px bg-plasma-500/20" />
      </div>

      <div className="space-y-2">
        <input
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Enter creator's code"
          className="w-full rounded-lg bg-ink-950/70 border border-plasma-500/30 px-3 py-2 font-mono text-sm focus:outline-none focus:border-plasma-400 focus:ring-1 focus:ring-plasma-400"
        />
        <button
          onClick={() => code && redeem(code)}
          disabled={!code || status === "loading"}
          className="w-full inline-flex items-center justify-center gap-2 rounded-xl py-2 border border-rust-500/40 bg-rust-500/10 text-rust-300 font-semibold disabled:opacity-50 hover:bg-rust-500/20 transition"
        >
          <Key size={14} /> Redeem code
        </button>
      </div>

      {msg && (
        <div className={`text-sm ${status === "err" ? "text-rust-400" : "text-emerald-300"}`}>
          {msg}
        </div>
      )}
    </div>
  );
}
