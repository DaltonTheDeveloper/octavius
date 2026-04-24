# Job — Download UE5 to external drive

This folder is a **runnable job**. Point Claude at `work.md` and it executes the whole playbook through Octavius.

## How to run

1. Plug in your target external drive. **Must have ≥80 GB free** and be **APFS** or **HFS+** formatted (ExFAT breaks UE5 attributes).
2. Make sure Octavius daemon is running:
   ```sh
   cd ~/octavius && source .venv/bin/activate && octavius-bus
   ```
3. In Claude Code (or any Claude interface with MCP to Octavius), say:
   > **do work.md so we can download UE5**
   Claude will read `work.md`, give you an estimated time, and walk through each step with approval prompts.

## What it does (summary)

- Detects your external drive
- Installs **legendary** (an OSS Epic client) locally via pipx
- Walks you through Epic OAuth login (you enter the code)
- Lists the UE5 builds in your Epic library
- Kicks off a background download to `<drive>/UnrealEngine/`
- Polls progress, gives you live ETA, notifies on completion
- Arms the unplug watcher

Total wall-clock: depends on your internet — usually **45–120 min** for the UE5 core (~40 GB).

## If anything fails

Claude will switch to the AppleScript UI-automation fallback in `work.md` → "Plan B." That path clicks through the Epic Launcher UI directly. Brittle but works when legendary breaks.

## What this is NOT

- It's not bypassing Epic login. You log in with your own Epic account via OAuth — we just use a different client (`legendary`).
- It's not redistributing anything. Everything downloads from Epic's CDN to your drive.
- It's not against *technical* safeguards — but Epic's Launcher ToS does frown on non-official clients. Account bans for legendary users have been near-zero historically, but the risk isn't zero. Informed-user territory.

## Side-effects to know about

- Installs `legendary-gl` via pipx (under ~/.local/)
- Creates `<drive>/UnrealEngine/` with a README
- Installs a launchd agent at `~/Library/LaunchAgents/com.octavius.unplug.<drive>.plist`
- Writes a hint at `~/.octavius/ue5_install_target.txt`
- Creates job state at `~/.octavius/jobs/ue-<timestamp>.state.json`

Every action above goes through the Octavius approval bus — you click Approve/Reject on each one in the sidebar UI.
