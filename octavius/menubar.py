"""Octavius menubar app — minimal native shell on top of the daemon.

Shows:
  - daemon status (live ↔ down)
  - count of pending approvals
  - one-click open dashboard
  - recent runs
  - capabilities list
  - jobs list (resumable)
  - start/stop daemon
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
import time
import urllib.request
import webbrowser

import rumps

DAEMON_URL = "http://127.0.0.1:7777"
DAEMON_BIN = os.environ.get("OCTAVIUS_BUS", "octavius-bus")


def get_json(path: str, timeout: float = 1.5):
    try:
        with urllib.request.urlopen(f"{DAEMON_URL}{path}", timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def daemon_alive() -> bool:
    return get_json("/api/heartbeat") is not None


def start_daemon() -> int | None:
    if daemon_alive():
        return None
    proc = subprocess.Popen(
        [DAEMON_BIN],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return proc.pid


def stop_daemon() -> bool:
    """Try to stop the daemon by killing whatever's bound to :7777."""
    try:
        out = subprocess.check_output(["lsof", "-ti", ":7777"], text=True).strip()
        for pid in out.splitlines():
            os.kill(int(pid), signal.SIGTERM)
        return True
    except Exception:
        return False


class OctaviusApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("🐙", quit_button=None)
        self.menu = [
            "Dashboard",
            None,
            "— Status —",
            "Daemon: …",
            "Pending: 0",
            None,
            ("Recent runs", []),
            ("Jobs", []),
            ("Capabilities", []),
            None,
            "Start daemon",
            "Stop daemon",
            None,
            "Open data folder",
            "Quit",
        ]
        self._refresh()
        self.timer = rumps.Timer(self._refresh, 5)
        self.timer.start()

    def _refresh(self, _=None):
        hb = get_json("/api/heartbeat")
        if hb:
            self.title = f"🐙 {hb['pending_count']}" if hb["pending_count"] else "🐙"
            self.menu["Daemon: …"].title = f"Daemon: live ({hb['executors']} caps)"
            self.menu["Pending: 0"].title = f"Pending: {hb['pending_count']}"
        else:
            self.title = "🐙·"
            self.menu["Daemon: …"].title = "Daemon: not running"
            self.menu["Pending: 0"].title = "Pending: —"

        # Recent
        recent_menu = self.menu["Recent runs"]
        recent_menu.clear()
        for a in get_json("/api/recent?limit=10") or []:
            label = f"{a['status'][:4]}·{a['capability']}: {a['summary'][:40]}"
            item = rumps.MenuItem(label)
            recent_menu.add(item)
        if not recent_menu:
            recent_menu.add(rumps.MenuItem("(none)"))

        # Jobs
        jobs_menu = self.menu["Jobs"]
        jobs_menu.clear()
        jobs_resp = get_json("/api/graph?detail=summary")  # placeholder
        # use jobs.list capability via /api/run? use graph endpoint? simplest: read filesystem
        try:
            from pathlib import Path
            jobs_dir = Path.home() / ".octavius" / "jobs"
            if jobs_dir.exists():
                dirs = sorted([d for d in jobs_dir.iterdir() if d.is_dir()],
                              key=lambda d: d.stat().st_mtime, reverse=True)[:10]
                for d in dirs:
                    state_p = d / "state.json"
                    if not state_p.exists():
                        continue
                    try:
                        s = json.loads(state_p.read_text())
                        label = f"{s['status'][:4]} · {s['slug']} · step={s['current_step']}"
                        item = rumps.MenuItem(label[:60])
                        jobs_menu.add(item)
                    except Exception:
                        continue
        except Exception:
            pass
        if not jobs_menu:
            jobs_menu.add(rumps.MenuItem("(no jobs)"))

        # Capabilities
        caps_menu = self.menu["Capabilities"]
        caps_menu.clear()
        caps = get_json("/api/capabilities") or []
        # Group by namespace
        by_ns: dict[str, list[str]] = {}
        for c in caps:
            ns = c.split(".")[0]
            by_ns.setdefault(ns, []).append(c)
        for ns in sorted(by_ns):
            sub = rumps.MenuItem(f"{ns} ({len(by_ns[ns])})")
            for c in by_ns[ns]:
                sub.add(rumps.MenuItem(c))
            caps_menu.add(sub)
        if not caps_menu:
            caps_menu.add(rumps.MenuItem("(daemon down)"))

    @rumps.clicked("Dashboard")
    def open_dashboard(self, _):
        webbrowser.open(f"{DAEMON_URL}/")

    @rumps.clicked("Start daemon")
    def start(self, _):
        pid = start_daemon()
        if pid is None:
            rumps.notification("Octavius", "Daemon", "Already running.")
        else:
            rumps.notification("Octavius", "Daemon started", f"pid {pid}")
            time.sleep(2)
            self._refresh()

    @rumps.clicked("Stop daemon")
    def stop(self, _):
        ok = stop_daemon()
        rumps.notification("Octavius", "Daemon", "Stopped." if ok else "Not running.")
        time.sleep(1)
        self._refresh()

    @rumps.clicked("Open data folder")
    def open_data(self, _):
        subprocess.run(["open", os.path.expanduser("~/.octavius")])

    @rumps.clicked("Quit")
    def quit_app(self, _):
        rumps.quit_application()


def main() -> None:
    OctaviusApp().run()


if __name__ == "__main__":
    main()
