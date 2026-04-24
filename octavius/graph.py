"""Live machine graph. Queried, not screenshotted."""
from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import psutil

from .config import UE5_SEARCH_ROOTS


@dataclass
class Process:
    pid: int
    name: str
    exe: str | None
    cpu: float
    mem_mb: float


@dataclass
class Volume:
    mountpoint: str
    device: str
    fstype: str
    total_gb: float
    free_gb: float
    removable: bool


@dataclass
class UE5Project:
    path: str
    name: str
    engine_association: str | None
    size_mb: float | None


@dataclass
class AppState:
    running: bool
    pids: list[int] = field(default_factory=list)


@dataclass
class Graph:
    timestamp: float
    processes: list[Process]
    volumes: list[Volume]
    ue5_projects: list[UE5Project]
    ue5_installs: list[str]
    chrome: AppState
    unreal_editor: AppState

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "processes": [asdict(p) for p in self.processes],
            "volumes": [asdict(v) for v in self.volumes],
            "ue5_projects": [asdict(p) for p in self.ue5_projects],
            "ue5_installs": self.ue5_installs,
            "chrome": asdict(self.chrome),
            "unreal_editor": asdict(self.unreal_editor),
        }


def _scan_processes() -> list[Process]:
    out = []
    for p in psutil.process_iter(attrs=["pid", "name", "exe", "cpu_percent", "memory_info"]):
        try:
            info = p.info
            mem = info["memory_info"].rss / 1024 / 1024 if info["memory_info"] else 0.0
            out.append(
                Process(
                    pid=info["pid"],
                    name=info["name"] or "",
                    exe=info["exe"],
                    cpu=info["cpu_percent"] or 0.0,
                    mem_mb=round(mem, 1),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return out


def _scan_volumes() -> list[Volume]:
    out = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue
        removable = "removable" in part.opts or part.mountpoint.startswith("/Volumes/")
        out.append(
            Volume(
                mountpoint=part.mountpoint,
                device=part.device,
                fstype=part.fstype,
                total_gb=round(usage.total / 1024**3, 2),
                free_gb=round(usage.free / 1024**3, 2),
                removable=removable,
            )
        )
    return out


def _dir_size_mb(path: Path, cap_mb: float = 50_000) -> float | None:
    """Fast-ish size via `du`. Returns None if slow/unreliable."""
    try:
        result = subprocess.run(
            ["du", "-sk", str(path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        kb = int(result.stdout.split()[0])
        return round(kb / 1024, 1)
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        return None


def _find_ue5_projects() -> list[UE5Project]:
    projects: list[UE5Project] = []
    seen: set[str] = set()
    for root in UE5_SEARCH_ROOTS:
        if not root.exists():
            continue
        try:
            for uproj in root.rglob("*.uproject"):
                key = str(uproj.resolve())
                if key in seen:
                    continue
                seen.add(key)
                engine = None
                try:
                    import json
                    data = json.loads(uproj.read_text())
                    engine = data.get("EngineAssociation")
                except Exception:
                    pass
                projects.append(
                    UE5Project(
                        path=str(uproj),
                        name=uproj.stem,
                        engine_association=engine,
                        size_mb=_dir_size_mb(uproj.parent),
                    )
                )
        except (PermissionError, OSError):
            continue
    return projects


def _find_ue5_installs() -> list[str]:
    candidates = [
        Path("/Users/Shared/Epic Games"),
        Path("/Applications/Epic Games"),
    ]
    installs = []
    for c in candidates:
        if not c.exists():
            continue
        for child in c.iterdir():
            if child.is_dir() and child.name.startswith("UE_"):
                installs.append(str(child))
    return installs


def _app_state(processes: list[Process], needle: str) -> AppState:
    matching = [p.pid for p in processes if needle.lower() in (p.name or "").lower()]
    return AppState(running=len(matching) > 0, pids=matching)


def snapshot() -> Graph:
    procs = _scan_processes()
    return Graph(
        timestamp=time.time(),
        processes=procs,
        volumes=_scan_volumes(),
        ue5_projects=_find_ue5_projects(),
        ue5_installs=_find_ue5_installs(),
        chrome=_app_state(procs, "Google Chrome"),
        unreal_editor=_app_state(procs, "UnrealEditor"),
    )


def summary() -> dict[str, Any]:
    """Cheap summary — no filesystem scan of large dirs."""
    g = snapshot()
    d = g.to_dict()
    # Trim process list to top 20 by memory for default summary
    d["processes"] = sorted(d["processes"], key=lambda p: -p["mem_mb"])[:20]
    return d
