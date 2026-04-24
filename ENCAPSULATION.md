# Encapsulation — what's real, what's theatre

A short honest doc about protecting extension authors' IP on Octavius.

## The honest truth

**Perfect DRM on a user's own machine is impossible.** Any code that runs on a machine can be extracted from that machine. A sufficiently motivated attacker with a debugger, memory dump, or frida script can pull out any decrypted code from any process. This is true of Photoshop, Unreal Engine, every paid VS Code extension, every AAA game. Vendors ship DRM anyway because the goal isn't "can't be cracked" — it's **"not worth the effort for the casual copier."**

That's the bar Octavius aims at: raise the cost enough that the long tail of piracy collapses while keeping the paying path frictionless.

## What Octavius actually does (v1 free tier)

Right now, every extension is public + free + open source. Encapsulation is not a concern yet. Authors opt in to a **membership code** so supporters get free access ahead of non-supporters — it's a distribution and "thank you" mechanism, not a protection one.

## What Octavius will do when paid extensions ship (v2)

### 1. Per-install keys, not per-extension keys

Each `License` row has an `installKey` (already in the schema). When the daemon downloads a bundle, it authenticates with the server and receives the bundle decrypted **with that install key**. Copying the extracted folder to another machine doesn't work — that machine's install key is different. The server tracks one active install per license (rotatable).

### 2. Periodic phone-home

The daemon calls `/api/license/verify` on every startup and every N hours at runtime. If the user revokes or the creator revokes, the extension stops executing within that window. Works offline for a grace period (default 72h).

### 3. Separate-process extensions

Extensions run as subprocesses spawned by the daemon, not as imports in-process. The daemon starts them with decrypted code passed via stdin or a unix socket, never written to disk in cleartext. The subprocess is sandboxed with restricted filesystem + network via macOS's `sandbox-exec` or Linux's `bwrap`.

### 4. Bytecode + obfuscation

Python extensions ship as `.pyc` with names obfuscated (not stripped strings, just mangled). Optional: authors can opt into pyarmor packaging at publish time. This is *speed-bump* protection — not protection against a determined attacker.

### 5. Native-compiled hot paths (author-opt-in)

For anything the author wants well-protected, the recommendation is the same as every commercial vendor: ship the sensitive logic as a compiled binary (Rust/Go/C++), not as script. Octavius extensions can bundle native binaries; the daemon spawns them the same way.

### 6. The server is the key broker

The **only secret** the author ever ships is the server-side key used to encrypt bundles. The server never exposes raw bundles — it only ever emits install-key-specific streams. Compromise of an installed machine compromises that install, not the extension globally.

## What Octavius explicitly will NOT do

- **No browser-style user-agent lock-down.** The daemon runs locally. We won't ask users to disable their own tools.
- **No aggressive anti-debug.** Kernel-level DRM alienates developers, which is our whole audience.
- **No closed-source protocol.** The daemon is open source. The protection lives in the bundle, not in security-through-obscurity of the runtime.

## For creators thinking about monetization

- **Price to match the crack cost.** If your extension takes 2 days to build and costs $5, it will be pirated. If it's $50 and deeply tied to your server-side services (API calls, rendering, whatever), piracy is less interesting than paying.
- **Hybrid: free client + paid service.** The strongest model: extension is free and open-source, but it calls a paid API you control. Piracy of the client doesn't get anyone access to the service.
- **Membership codes are legitimately good.** Your biggest fans pay you via YouTube/Patreon already. They get free access. Lurkers pay. Pirates pirate. The paying-fan column grows; the piracy column doesn't shrink, but you don't care because it was never going to convert anyway.

## Summary

v1 (now): free, open, membership codes distribute trust.
v2 (when paid lands): per-install keys + subprocess runtime + phone-home + optional native binaries. Enough to stop casual copying, not enough to stop a determined attacker — and that's fine.
