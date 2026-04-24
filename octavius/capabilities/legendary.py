"""Legendary — OSS Epic Games CLI. Used here to automate UE5 download.

Legendary (https://github.com/derrod/legendary, GPL-3) authenticates via
Epic's real OAuth flow — we do not bypass Epic's login. It then uses the
same catalog and CDN endpoints the official launcher uses to download
content the user already owns.

Caveats Claude should surface to the user:
  - Epic has historically not broken legendary, but does not officially
    bless it. Epic's ToS for the launcher forbids automation; using a
    different client is a gray area. Account bans are rare but not zero.
  - Legendary can install some UE "engine" entries via Epic's catalog,
    but UE engine builds are not always listed as installable like
    regular games. If `legendary list --include-ue` returns no UE, fall
    back to the AppleScript UI-automation path in volume.py / a dedicated
    fallback capability.
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .. import journal
from ..config import DATA_DIR

JOB_DIR = DATA_DIR / "jobs"
JOB_DIR.mkdir(exist_ok=True)


def _legendary_bin() -> str | None:
    # pipx / pip / brew / manual — search PATH first
    found = shutil.which("legendary")
    if found:
        return found
    # pipx default
    pipx_bin = Path.home() / ".local" / "bin" / "legendary"
    if pipx_bin.exists():
        return str(pipx_bin)
    return None


async def _sh(*cmd: str, timeout: int = 30, cwd: str | None = None) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", "timeout"
    return proc.returncode or 0, out.decode(errors="replace"), err.decode(errors="replace")


async def _check(params: dict[str, Any]) -> dict[str, Any]:
    bin_ = _legendary_bin()
    if not bin_:
        return {"installed": False, "hint": "run epic.install_legendary"}
    code, out, _ = await _sh(bin_, "--version", timeout=5)
    return {"installed": True, "path": bin_, "version": out.strip() or "unknown"}


async def _install(params: dict[str, Any]) -> dict[str, Any]:
    """Install legendary. Tries in order: brew → pipx (auto-install pipx if missing)
    → pip3 --break-system-packages as last resort."""
    attempts: list[dict[str, Any]] = []

    # Path 1: Homebrew
    brew = shutil.which("brew")
    if brew:
        code, out, err = await _sh(brew, "install", "legendary-gl", timeout=300)
        attempts.append({"via": "brew", "code": code, "stderr_tail": err[-200:]})
        if code == 0 or "already installed" in err.lower() or "already installed" in out.lower():
            journal.record(kind="epic.install_legendary", forward={"via": "brew"}, inverse=None)
            return {"installed_via": "brew", "attempts": attempts}

    # Path 2: pipx
    pipx = shutil.which("pipx")
    if not pipx and brew:
        # bootstrap pipx via brew
        code, out, err = await _sh(brew, "install", "pipx", timeout=180)
        attempts.append({"via": "brew install pipx", "code": code, "stderr_tail": err[-200:]})
        if code == 0 or "already installed" in err.lower():
            # ensurepath
            await _sh(brew, "pipx", "ensurepath", timeout=30)
            pipx = shutil.which("pipx") or str(Path("/opt/homebrew/bin/pipx"))
    if pipx and Path(pipx).exists():
        code, out, err = await _sh(pipx, "install", "legendary-gl", timeout=300)
        attempts.append({"via": "pipx", "code": code, "stderr_tail": err[-200:]})
        if code == 0 or "already installed" in err.lower():
            journal.record(kind="epic.install_legendary", forward={"via": "pipx"}, inverse=None)
            return {"installed_via": "pipx", "attempts": attempts}

    # Path 3: pip3 with --break-system-packages as last resort
    pip = shutil.which("pip3") or shutil.which("pip")
    if pip:
        code, out, err = await _sh(
            pip, "install", "--user", "--break-system-packages", "legendary-gl",
            timeout=300,
        )
        attempts.append({"via": "pip3 --break-system-packages", "code": code, "stderr_tail": err[-200:]})
        if code == 0:
            journal.record(kind="epic.install_legendary", forward={"via": "pip3"}, inverse=None)
            return {"installed_via": "pip3 --break-system-packages", "attempts": attempts}

    raise RuntimeError(f"all install paths failed. attempts: {attempts}")


async def _status(params: dict[str, Any]) -> dict[str, Any]:
    bin_ = _legendary_bin()
    if not bin_:
        return {"authenticated": False, "error": "legendary not installed"}
    code, out, err = await _sh(bin_, "status", timeout=15)
    authed = "Logged in as:" in out or "Logged in as:" in err
    return {
        "authenticated": authed,
        "stdout_excerpt": out.splitlines()[:10],
        "raw_exit": code,
    }


async def _auth_begin(params: dict[str, Any]) -> dict[str, Any]:
    """Open the browser auth flow. User pastes the authorization code back
    via a follow-up capability call (epic.legendary_auth_complete)."""
    bin_ = _legendary_bin()
    if not bin_:
        raise RuntimeError("legendary not installed")
    # Open the auth URL in a browser; legendary's flow prints a URL when run.
    # We open Epic's OAuth page directly — same URL legendary uses.
    auth_url = "https://www.epicgames.com/id/api/redirect?clientId=34a02cf8f4414e29b15921876da36f9a&responseType=code"
    proc = await asyncio.create_subprocess_exec(
        "open", auth_url,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    journal.record(kind="epic.legendary_auth_begin", forward={"url": auth_url}, inverse=None)
    return {
        "auth_url_opened": auth_url,
        "next_step": "After logging in, Epic will show a page with an 'authorizationCode' value. "
                     "Copy it and run epic.legendary_auth_complete with {code: '...'}",
    }


async def _auth_complete(params: dict[str, Any]) -> dict[str, Any]:
    bin_ = _legendary_bin()
    if not bin_:
        raise RuntimeError("legendary not installed")
    code_value = params["code"]
    proc = await asyncio.create_subprocess_exec(
        bin_, "auth", "--code", code_value,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(f"legendary auth failed: {err.decode(errors='replace')[-500:]}")
    journal.record(kind="epic.legendary_auth_complete", forward={"code": "***redacted***"}, inverse=None)
    return {"authenticated": True, "stdout": out.decode(errors="replace")[-500:]}


async def _list_ue(params: dict[str, Any]) -> dict[str, Any]:
    """List Unreal Engine builds in the user's Epic library."""
    bin_ = _legendary_bin()
    if not bin_:
        raise RuntimeError("legendary not installed")
    # legendary uses --include-ue to surface UE entries specifically
    code, out, err = await _sh(bin_, "list", "--include-ue", "--json", timeout=60)
    if code != 0:
        return {"error": err[-500:], "hint": "legendary may not support UE in your version; upgrade or use UI fallback"}
    try:
        entries = json.loads(out)
    except Exception:
        return {"error": "non-json output", "raw": out[:2000]}
    ue_entries = [
        {
            "app_name": e.get("app_name"),
            "app_title": e.get("app_title"),
            "namespace": e.get("namespace"),
            "metadata_categories": [c.get("path") for c in (e.get("metadata", {}).get("categories") or [])],
        }
        for e in entries
        if "UE_" in (e.get("app_name") or "") or "unreal" in (e.get("app_title") or "").lower()
    ]
    return {"ue_entries": ue_entries, "total": len(ue_entries)}


async def _download_ue(params: dict[str, Any]) -> dict[str, Any]:
    """Kick off a UE install via legendary in the background. Returns a job_id."""
    bin_ = _legendary_bin()
    if not bin_:
        raise RuntimeError("legendary not installed")
    app_name = params["app_name"]          # e.g. "UE_5.4"
    base_path = str(Path(params["base_path"]).expanduser().resolve())
    Path(base_path).mkdir(parents=True, exist_ok=True)

    job_id = f"ue-{int(time.time())}"
    log_path = JOB_DIR / f"{job_id}.log"
    state_path = JOB_DIR / f"{job_id}.state.json"

    # Start legendary in background. `-y` auto-confirms.
    env = os.environ.copy()
    # Prevent tty-based ui
    env["LEGENDARY_NO_UI"] = "1"
    proc = await asyncio.create_subprocess_exec(
        bin_, "install", app_name, "--base-path", base_path, "-y",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
    )
    # detach: write output to log in a fire-and-forget task
    async def pump():
        with open(log_path, "ab") as f:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                f.write(line)
                f.flush()
        await proc.wait()
        state = {"status": "done" if proc.returncode == 0 else "failed", "exit_code": proc.returncode}
        state_path.write_text(json.dumps(state))

    asyncio.create_task(pump())

    state = {"status": "running", "pid": proc.pid, "app_name": app_name, "base_path": base_path, "started_at": time.time()}
    state_path.write_text(json.dumps(state))

    journal.record(
        kind="epic.legendary_download_ue",
        forward={"app_name": app_name, "base_path": base_path, "job_id": job_id, "pid": proc.pid},
        inverse=None,
    )
    return {
        "job_id": job_id,
        "pid": proc.pid,
        "log_path": str(log_path),
        "state_path": str(state_path),
        "target": base_path,
    }


async def _progress(params: dict[str, Any]) -> dict[str, Any]:
    """Check progress of a download job."""
    job_id = params["job_id"]
    state_path = JOB_DIR / f"{job_id}.state.json"
    log_path = JOB_DIR / f"{job_id}.log"
    if not state_path.exists():
        raise FileNotFoundError(f"unknown job: {job_id}")
    state = json.loads(state_path.read_text())
    base_path = state.get("base_path")

    # Measure the target dir size
    size_bytes = 0
    if base_path and Path(base_path).exists():
        proc = await asyncio.create_subprocess_exec(
            "du", "-sk", base_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await proc.communicate()
        try:
            size_bytes = int(out.split()[0]) * 1024
        except Exception:
            pass

    elapsed = time.time() - (state.get("started_at") or time.time())
    mb_per_s = (size_bytes / 1024 / 1024 / elapsed) if elapsed > 5 else 0

    # Approximate: UE5 core is ~40GB. A user may install more (templates, samples).
    ue_estimate_gb = 40
    percent = min(99.9, (size_bytes / 1024**3) / ue_estimate_gb * 100) if size_bytes else 0
    remaining_gb = max(0.0, ue_estimate_gb - (size_bytes / 1024**3))
    eta_seconds = remaining_gb * 1024 / mb_per_s if mb_per_s > 0.5 else None

    # Last 20 lines of the log
    tail = ""
    if log_path.exists():
        try:
            tail = subprocess.check_output(["tail", "-20", str(log_path)], text=True)
        except Exception:
            tail = ""

    return {
        "job_id": job_id,
        "status": state.get("status"),
        "bytes_on_disk": size_bytes,
        "gb_on_disk": round(size_bytes / 1024**3, 2),
        "est_total_gb": ue_estimate_gb,
        "percent_approx": round(percent, 1),
        "mb_per_s": round(mb_per_s, 1),
        "eta_seconds": int(eta_seconds) if eta_seconds else None,
        "eta_human": _fmt_eta(eta_seconds) if eta_seconds else "—",
        "elapsed_s": int(elapsed),
        "log_tail": tail,
    }


def _fmt_eta(seconds: float | None) -> str:
    if not seconds:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def register(bus) -> None:
    bus.register("epic.check_legendary", _check)
    bus.register("epic.install_legendary", _install)
    bus.register("epic.legendary_status", _status)
    bus.register("epic.legendary_auth_begin", _auth_begin)
    bus.register("epic.legendary_auth_complete", _auth_complete)
    bus.register("epic.legendary_list_ue", _list_ue)
    bus.register("epic.legendary_download_ue", _download_ue)
    bus.register("epic.download_progress", _progress)
