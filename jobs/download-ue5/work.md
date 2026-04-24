# work.md — Download UE5 to an external drive (resumable, vision-based)

> **You (Claude): execute this document as a playbook.** Each step proposes a capability via Octavius's `/api/propose`, polls status, and CHECKPOINTS to the jobs subsystem so a daemon restart doesn't lose the run.

## Setup once

If the user hasn't said anything yet, START with:

```
I'm about to install UE5 onto your external drive end-to-end.
Plan (each gate is one approval):
  1.  jobs.create — start a resumable job we can come back to
  2.  volume.list_external — pick the drive
  3.  volume.assert_space — confirm ≥80 GB free
  4.  epic.prepare_install_target — make UnrealEngine/ on the drive
  5.  app.launch — bring Epic Games Launcher to front
  6.  vision.list_windows — find EGL's CGWindowID
  7.  vision.click_calibrated (yellow Install Engine button)
  8.  ui.type_text — overwrite default install path with our target
  9.  vision.click_calibrated (yellow Install button in dialog)
  10. volume.install_unplug_watcher — arm macOS notification on eject
  11. epic.download_progress polling loop with live ETA
ETA: ~50–90 min wall clock once the download starts. I'll check every 30s.

Heads-up: We're using vision automation on Epic's Qt UI. If Epic ships
a new launcher version with a different button color or layout the
calibration may need re-tuning — I'll detect this and stop.

Ready?
```

Wait for confirmation.

## Step 0 — create or resume a job

If the user has a previous `download-ue5-*` job in `~/.octavius/jobs/`, ask whether to **resume** that one or **start fresh**.

```
Capability: jobs.list
Params:     {"limit": 5}
```

If they want to resume an existing one:
```
Capability: jobs.resume
Params:     {"job_id": "<their job id>"}
```
The response has `current_step` — JUMP TO THAT STEP BELOW.

Otherwise:
```
Capability: jobs.create
Params:     {"slug": "download-ue5", "vars": {}}
```
Save the returned `job_id` — pass it to every `jobs.checkpoint` below.

## Step 1 — find external drive

```
Capability: volume.list_external
Summary:    "Scan for external drives"
Danger:     low
```

Read `result.drives[]`. If empty, tell user to plug in a drive.

If multiple drives, ask which.

If exactly one, present it (name, free space, fs) for confirmation.

If `fs` is exfat, warn the user — UE5 file metadata doesn't survive ExFAT cleanly. They can proceed at risk.

```
Capability: jobs.checkpoint
Params:     {"job_id": "...", "step": "drive_selected", "vars": {"mount": "<path>"}}
```

## Step 2 — assert space + prepare target

```
Capability: volume.assert_space
Params:     {"mount": "<mount>", "gb_required": 80}

Capability: epic.prepare_install_target
Params:     {"mount": "<mount>", "folder_name": "UnrealEngine"}
```

Save returned `target_path`. Then:

```
Capability: epic.set_install_dir_hint
Params:     {"target_path": "<target_path>"}
Capability: jobs.checkpoint
Params:     {"job_id": "...", "step": "target_ready", "vars": {"target_path": "..."}}
```

## Step 3 — bring EGL to front + locate window

```
Capability: app.launch
Params:     {"app": "Epic Games Launcher"}
```

Wait 3 seconds for it to render, then:

```
Capability: vision.list_windows
Params:     {"app": "Epic"}
```

Take the first window with the largest bounds (skip notification popups). Save its `window_id`.

If user's EGL is on a different size than expected, that's fine — vision capabilities calibrate dynamically.

## Step 4 — click "Install Engine" via vision

```
Capability: vision.click_calibrated
Summary:    "Click the yellow Install Engine button (color-calibrated)"
Danger:     medium
Params:     {
  "window_id": <id>,
  "color": [245, 166, 35],          // EGL's signature yellow
  "tolerance": 25,
  "region": [0.85, 0.0, 1.0, 0.10]  // top-right corner only
}
```

Wait 3 seconds. Then:

```
Capability: vision.capture_window
Params:     {"window_id": <id>, "name": "after_install_click.png"}
```

The "Choose install location" dialog should now be visible. If not, retry with a slightly larger region or different tolerance.

```
Capability: jobs.checkpoint
Params:     {"job_id": "...", "step": "install_dialog_open"}
```

## Step 5 — overwrite default install path

The dialog defaults to `/Users/Shared/Epic Games`. We need our path on the external.

First focus the folder text field via triple-click. The field is roughly at fraction `(0.42, 0.46)` of the window — click there:

```
Capability: vision.find_button_by_color
Params:     {
  "window_id": <id>,
  "color": [255, 255, 255],   // white text field
  "tolerance": 5,
  "region": [0.30, 0.42, 0.55, 0.50]
}
```

Take the returned `screen_point` and triple-click via `ui.click_by_label` won't work on Qt — use `shell.run` with cliclick:

```
Capability: shell.run
Params:     {"cmd": "cliclick tc:<x>,<y>"}
```

Then select-all + paste the target path. The path was put on clipboard by `epic.prepare_install_target` step — but to be safe, put it again:

```
Capability: shell.run
Params:     {"cmd": "printf '%s' '<target_path>' | pbcopy"}

Capability: shell.run
Params:     {"cmd": "cliclick kd:cmd t:a ku:cmd && sleep 0.2 && cliclick kd:cmd t:v ku:cmd"}
```

Verify by capturing again and reading the dialog. (Future: add OCR capability for full closed-loop verification.)

```
Capability: jobs.checkpoint
Params:     {"job_id": "...", "step": "install_path_pasted"}
```

## Step 6 — click Install button in dialog

The Install button is yellow at the bottom of the dialog. Use a tighter region to avoid hitting "Install Engine" in the background:

```
Capability: vision.click_calibrated
Summary:    "Click yellow Install button in dialog (calibrated)"
Danger:     high
Params:     {
  "window_id": <id>,
  "color": [245, 166, 35],
  "tolerance": 25,
  "region": [0.50, 0.55, 0.65, 0.70]   // dialog button row only
}
```

Wait 5 seconds, then verify download started:

```
Capability: vision.capture_window
Params:     {"window_id": <id>, "name": "post_install_click.png"}
```

If a new (smaller) window also appeared in `vision.list_windows`, that's the download status popup — confirms install kicked off.

```
Capability: jobs.checkpoint
Params:     {"job_id": "...", "step": "download_started"}
```

## Step 7 — arm unplug watcher

```
Capability: volume.install_unplug_watcher
Params:     {"mount": "<mount>"}
```

```
Capability: jobs.checkpoint
Params:     {"job_id": "...", "step": "watcher_armed"}
```

## Step 8 — progress polling loop

Every 60 seconds:
- Run `du -sh <target_path>/UE_5.X` via `shell.run`
- Compute MB/s based on delta
- Estimate ETA (UE5 core ~40 GB)
- Report to user: `"~12% · 4.8 GB · 11 MB/s · ETA 48 min"`

Stop polling when:
- target dir reaches ≥35 GB **and** EGL screenshot shows "Launch" or "Verify" instead of progress bar
- OR user says stop

When done:
```
Capability: jobs.complete
Params:     {"job_id": "...", "status": "done", "summary": "UE5 installed at <path>"}
```

## Failure recovery

If anything fails:
- `jobs.checkpoint` with the failure step
- Tell user what went wrong
- They can resume next session via `jobs.resume`

If EGL crashes mid-download:
- `app.launch` to relaunch
- EGL itself will show a "Resume" button on the partially-downloaded engine — click it via `vision.click_calibrated` with the SAME yellow color but a different region (engine tile area, around fraction `(0.18, 0.20)`)

## Why this works (notes for the human reading)

1. **Calibration via traffic-light**: `vision.calibrate_window` finds the red close button at fixed window-local offset (14, 14 pt). This tells us how PNG pixels map to screen points, accounting for shadow padding the screencapture includes.
2. **Color centroid**: distinctive button colors (Epic's yellow #F5A623) are unique within their region. Centroid + bbox gives us the click target.
3. **cliclick over CGEventPost-from-Python**: cliclick inherits the calling shell's Accessibility permission. Python from a venv often doesn't have its own permission entry yet — too much friction to get the user to grant it.
4. **Jobs**: every step writes to `~/.octavius/jobs/<id>/state.json`. If the daemon crashes, the user just runs `jobs.resume {job_id}` and we pick up at the last checkpoint.
