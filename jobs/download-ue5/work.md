# work.md — Download UE5 to an external drive via Octavius

> **You (Claude): execute this document as a playbook.** Each step is a call to the Octavius daemon at `http://127.0.0.1:7777`. Propose via `POST /api/propose`, wait for the user's approval (they'll click in the sidebar), then poll `/api/recent?limit=1`. Report progress in plain prose between steps. Do NOT skip the estimated-time + caveats block before starting.

---

## Opening message to user (required — say this first)

When the user says "do work.md so we can download UE5", respond first with:

```
I'm about to kick off the UE5 download job. Here's the plan:

  Step 1: Scan for your external drive (2s)
  Step 2: Check space (need ≥80GB) (2s)
  Step 3: Prepare target folder (5s)
  Step 4: Install legendary (OSS Epic client) (~30s)
  Step 5: Open Epic OAuth in your browser — you log in + paste code (~1min)
  Step 6: List your UE builds in Epic (5s)
  Step 7: Start UE5 download (background, ~45–120 min)
  Step 8: Arm the unplug watcher (5s)
  Step 9: Poll progress + give live ETA

Heads-up:
  - Epic has no official CLI. We're using `legendary` (OSS, GPL). You log in
    with your real Epic account via OAuth — we do not bypass authentication.
  - Epic's launcher ToS is unfriendly to non-official clients. Account bans
    for legendary users are near-zero historically but not impossible.
  - Download time depends on your internet. Rough estimate: ~60 min on a
    100 Mbps connection. I'll give a live ETA after 30s of actual download.

Ready to start? (I'll propose each step; you click Approve in the sidebar.)
```

Wait for user confirmation before proceeding.

---

## Step 1 — Scan for external drives

**Capability:** `volume.list_external`
**Params:** `{}`
**Summary:** "Scan for external drives"
**Danger:** low

After approval, inspect `result.drives[]`. If empty:
> "I don't see any external drives plugged in. Plug one in and tell me when you're ready."
And stop.

If multiple drives, ask user which one.
If one drive, use it but show the user its info (name, free space, filesystem) before proceeding.

### Filesystem check
If the drive's `fs` is anything other than `apfs`, `hfs`, or `hfsx`, **warn the user**:
> "This drive is formatted as `<fs>`. UE5 stores files that Windows/ExFAT can't represent faithfully (Unix permissions, extended attributes). The download will likely complete but the editor may refuse to open. Reformat to APFS, or continue at your own risk."
Ask for confirmation.

---

## Step 2 — Verify space

**Capability:** `volume.assert_space`
**Params:** `{"mount": "<chosen mount>", "gb_required": 80}`
**Summary:** "Verify <drive name> has ≥80 GB free"
**Danger:** low

If it fails (insufficient space), tell user the actual free space and stop.

---

## Step 3 — Prepare the target folder

**Capability:** `epic.prepare_install_target`
**Params:** `{"mount": "<chosen mount>", "folder_name": "UnrealEngine"}`
**Summary:** "Create UnrealEngine/ on <drive name>"
**Danger:** medium (creates a directory on the drive)

Remember the returned `target_path` — you'll use it in Step 7.

Also call:

**Capability:** `epic.set_install_dir_hint`
**Params:** `{"target_path": "<returned target_path>"}`
**Summary:** "Remember this as the preferred UE5 install dir"
**Danger:** low

---

## Step 4 — Install legendary (the OSS Epic client)

First check if it's already installed:

**Capability:** `epic.check_legendary`
**Params:** `{}`
**Summary:** "Is legendary installed?"

If `result.installed == true`, skip to Step 5.

Otherwise:

**Capability:** `epic.install_legendary`
**Params:** `{}`
**Summary:** "Install legendary (OSS Epic CLI) via pipx"
**Danger:** medium

After this, re-run `epic.check_legendary` to confirm and capture the version.

---

## Step 5 — Epic OAuth

**Capability:** `epic.legendary_status`
**Params:** `{}`
**Summary:** "Check if Epic is already authenticated"

If `authenticated: true`, skip to Step 6.

Otherwise:

**Capability:** `epic.legendary_auth_begin`
**Params:** `{}`
**Summary:** "Open Epic OAuth login in browser"
**Danger:** low (just opens a browser tab)

Tell the user:
> "I've opened Epic's login page. Log in with your Epic account. After you click 'I Agree', Epic shows a page with a JSON blob containing an `authorizationCode` — a 32-character hex string. Copy that code and paste it here in the chat so I can complete the auth."

Wait for user to paste the code (it'll look like `abc123...`). Then:

**Capability:** `epic.legendary_auth_complete`
**Params:** `{"code": "<pasted code>"}`
**Summary:** "Complete Epic authentication"
**Danger:** medium

---

## Step 6 — Find UE builds in the library

**Capability:** `epic.legendary_list_ue`
**Params:** `{}`
**Summary:** "List Unreal Engine builds in your Epic library"
**Danger:** low

If `ue_entries` is empty, switch to **Plan B** (below).

Otherwise, show the user the list (with `app_name` and `app_title`) and ask which they want to install. Default to the latest `UE_5.x`.

---

## Step 7 — Start the download

**Capability:** `epic.legendary_download_ue`
**Params:** `{"app_name": "<chosen UE_5.x>", "base_path": "<target_path from Step 3>"}`
**Summary:** "Start UE5 download in background"
**Danger:** **high** (long-running, writes tens of GB)

The capability returns a `job_id` and a `pid`. Save the `job_id`.

---

## Step 8 — Arm the unplug watcher

**Capability:** `volume.install_unplug_watcher`
**Params:** `{"mount": "<chosen mount>"}`
**Summary:** "Arm macOS notification if <drive name> is ejected"
**Danger:** medium (installs a launchd agent)

---

## Step 9 — Progress loop

Every 30 seconds, poll:

**Capability:** `epic.download_progress`
**Params:** `{"job_id": "<from Step 7>"}`
**Summary:** *do not re-propose — use the MCP tool or `/api/propose` with danger=low; or auto-approve since this is read-only.*

Actually the cleanest: this step is read-only, so **don't** route through the approval bus. Just `GET /api/graph?detail=full` to pull the job state, OR add a new `/api/run` endpoint for read-only capabilities. If neither exists yet, use `POST /api/propose` with `wait: true` — the user will approve these quickly, they're informational.

Report to the user every poll:
```
~23% done · 9.1 GB / ~40 GB · 6.8 MB/s · ETA 1h 14m
```

When `status == "done"`, declare victory and:
- Tell the user to open the Epic Games Launcher to verify UE shows as installed there (the "official" launcher won't auto-detect a legendary install; the user needs to add it as a manual install location in Preferences).
- Suggest running `octavius-bus` capability `ue5.launch_editor` on the Sandbox project if they want to test.

When `status == "failed"`, read the log tail from the result and help the user diagnose. Common failures:
- "No login" → re-run Step 5
- "Disk full" → free space on target
- "Network error" → retry
- "App not found" → legendary doesn't have this UE build — try Plan B

---

## Plan B — UI automation fallback

If legendary doesn't work (no UE in library, auth fails, UE install breaks halfway), switch to UI automation of the actual Epic Games Launcher.

### B-1 — Launch Epic

**Capability:** `app.launch`
**Params:** `{"app": "Epic Games Launcher"}`

Wait ~10s for the launcher to be fully loaded.

### B-2 — Navigate to Unreal Engine tab

**Capability:** `ui.click_by_label`
**Params:** `{"app": "Epic Games Launcher", "label": "Unreal Engine"}`
**Summary:** "Click Unreal Engine tab in the launcher"
**Danger:** high (UI automation is fragile)

### B-3 — Click Install

**Capability:** `ui.click_by_label`
**Params:** `{"app": "Epic Games Launcher", "label": "Install"}`
**Summary:** "Click Install on the latest UE5 build"

### B-4 — Browse for install dir

Epic will show a dialog. Use:
**Capability:** `ui.click_by_label`
**Params:** `{"app": "Epic Games Launcher", "label": "Browse"}`

Then type the target path:
**Capability:** `ui.type_text`
**Params:** `{"app": "Epic Games Launcher", "text": "<target_path from Step 3>"}`

### B-5 — Confirm

**Capability:** `ui.click_by_label`
**Params:** `{"app": "Epic Games Launcher", "label": "Open"}`

Then monitor the install via Epic's own progress UI (you can read it via `app.discover` on the Launcher window, or take periodic screenshots if we add that capability).

**Warning about Plan B:** the labels above are Epic's current UI. They change. If `ui.click_by_label` fails with "no button labeled X", run `app.discover` on the Launcher and ask the user to tell you the actual label.

---

## Cleanup on failure

If anything fails mid-flow, tell the user what state we're in, list what's already on disk and what's already been scheduled (unplug watcher, hint file, partial download dir), and ask whether they want to `undo` the last N actions via `/api/undo?count=N`. The journal has inverses for the fs and epic.prepare ops; the legendary download itself isn't atomically rollback-able but you can delete the partial dir.
