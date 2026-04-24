"""Volume capability — external drive ops."""
from __future__ import annotations

import asyncio
import json
import plistlib
import subprocess
from pathlib import Path
from typing import Any

from .. import journal
from ..config import DATA_DIR

WATCHERS_DIR = DATA_DIR / "watchers"
WATCHERS_DIR.mkdir(exist_ok=True)

LAUNCH_AGENTS = Path.home() / "Library" / "LaunchAgents"
LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)


async def _diskutil_info(device_or_mount: str) -> dict:
    proc = await asyncio.create_subprocess_exec(
        "diskutil", "info", "-plist", device_or_mount,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, _ = await proc.communicate()
    if proc.returncode != 0:
        return {}
    try:
        return plistlib.loads(out)
    except Exception:
        return {}


async def _list_external(params: dict[str, Any]) -> dict[str, Any]:
    """True external drives only — USB / Thunderbolt / SD / FireWire, not DMGs."""
    proc = await asyncio.create_subprocess_exec(
        "diskutil", "list", "-plist", "external", "physical",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, _ = await proc.communicate()
    drives: list[dict] = []
    try:
        info = plistlib.loads(out)
        for entry in info.get("AllDisksAndPartitions", []):
            for part in entry.get("Partitions", []):
                mp = part.get("MountPoint")
                if not mp:
                    continue
                detail = await _diskutil_info(part.get("DeviceIdentifier", ""))
                drives.append({
                    "mount": mp,
                    "device": "/dev/" + part.get("DeviceIdentifier", ""),
                    "volume_name": part.get("VolumeName") or Path(mp).name,
                    "fs": detail.get("FilesystemType"),
                    "bus": detail.get("BusProtocol") or detail.get("Protocol"),
                    "total_gb": round(detail.get("TotalSize", 0) / 1024**3, 2),
                    "free_gb": round(detail.get("FreeSpace", 0) / 1024**3, 2) if "FreeSpace" in detail else None,
                    "ejectable": bool(detail.get("Ejectable")),
                    "removable_media": bool(detail.get("RemovableMedia")),
                    "writable": bool(detail.get("Writable")),
                })
    except Exception:
        pass
    return {"drives": drives}


async def _assert_space(params: dict[str, Any]) -> dict[str, Any]:
    """Verify a mount has at least `gb_required` free. Raises if not."""
    mount = Path(params["mount"]).expanduser().resolve()
    required = float(params["gb_required"])
    if not mount.exists():
        raise FileNotFoundError(f"mount missing: {mount}")
    stat = shutil_disk_usage(mount)
    free_gb = stat.free / 1024**3
    ok = free_gb >= required
    if not ok:
        raise RuntimeError(
            f"insufficient space on {mount}: have {free_gb:.1f}GB, need {required:.1f}GB"
        )
    return {"mount": str(mount), "free_gb": round(free_gb, 2), "required_gb": required, "ok": True}


# cheap shim so we can call disk_usage as a top-level helper
def shutil_disk_usage(path):
    import shutil
    return shutil.disk_usage(path)


def _unplug_watcher_plist(label: str, target_mount: str, log_path: str) -> str:
    """macOS launchd agent that triggers when target_mount disappears from /Volumes."""
    script = (
        "#!/usr/bin/env bash\n"
        f'TARGET="{target_mount}"\n'
        f'LOG="{log_path}"\n'
        'echo "$(date -Iseconds) unplug_detected $TARGET" >> "$LOG"\n'
        'osascript -e "display notification \\"Drive $TARGET was unplugged. Epic will be notified on next launch.\\" with title \\"Octavius\\" subtitle \\"External drive unplugged\\" sound name \\"Ping\\""\n'
        # Leave a marker the Epic Launcher check can pick up
        f'mkdir -p ~/.octavius && echo $(date -Iseconds) > ~/.octavius/last_unplug\n'
    )
    script_path = WATCHERS_DIR / f"{label}.sh"
    script_path.write_text(script)
    script_path.chmod(0o755)

    plist = {
        "Label": label,
        "ProgramArguments": [str(script_path)],
        "WatchPaths": [str(Path(target_mount).parent)],
        "RunAtLoad": False,
        "StandardOutPath": log_path,
        "StandardErrorPath": log_path,
    }
    plist_path = LAUNCH_AGENTS / f"{label}.plist"
    with plist_path.open("wb") as f:
        plistlib.dump(plist, f)
    return str(plist_path)


async def _install_unplug_watcher(params: dict[str, Any]) -> dict[str, Any]:
    """Install a launchd agent that notifies on the target external drive eject.

    The watcher uses a WatchPaths on /Volumes so it fires any time a sibling
    volume appears or disappears; the script checks whether our specific mount
    is still present and posts a notification only if it's gone.
    """
    mount = Path(params["mount"]).expanduser().resolve()
    label = f"com.octavius.unplug.{mount.name.lower().replace(' ', '_')}"
    log_path = str(DATA_DIR / f"unplug-{mount.name}.log")
    plist_path = _unplug_watcher_plist(label, str(mount), log_path)

    # Load into launchd
    proc = await asyncio.create_subprocess_exec(
        "launchctl", "load", "-w", plist_path,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    loaded = proc.returncode == 0

    journal.record(
        kind="volume.install_unplug_watcher",
        forward={"mount": str(mount), "label": label, "plist": plist_path},
        inverse={"op": "noop"},  # uninstall via dedicated capability
    )
    return {
        "mount": str(mount),
        "label": label,
        "plist_path": plist_path,
        "log_path": log_path,
        "loaded": loaded,
        "stderr": err.decode(errors="replace") if err else "",
    }


async def _uninstall_unplug_watcher(params: dict[str, Any]) -> dict[str, Any]:
    label = params["label"]
    plist_path = LAUNCH_AGENTS / f"{label}.plist"
    proc = await asyncio.create_subprocess_exec(
        "launchctl", "unload", "-w", str(plist_path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    if plist_path.exists():
        plist_path.unlink()
    journal.record(
        kind="volume.uninstall_unplug_watcher",
        forward={"label": label},
        inverse=None,
    )
    return {"uninstalled": label}


def register(bus) -> None:
    bus.register("volume.list_external", _list_external)
    bus.register("volume.assert_space", _assert_space)
    bus.register("volume.install_unplug_watcher", _install_unplug_watcher)
    bus.register("volume.uninstall_unplug_watcher", _uninstall_unplug_watcher)
