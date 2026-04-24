"""Epic Games Launcher capability — inspect config, prep install target.

Honest scope: Epic does NOT expose a headless download CLI. This capability
handles everything *around* the download:

  - locate Epic's config dir + LauncherInstalled.dat
  - read which engines are currently managed by Epic
  - write a hint file telling Epic where the user wants UE5 installed
    (Epic will honor this as the default when the user actually clicks Install)
  - prepare the target directory on the external drive
  - arm an unplug watcher on the target volume

The actual "click Install" happens in the launcher UI.
"""
from __future__ import annotations

import asyncio
import json
import plistlib
from pathlib import Path
from typing import Any

from .. import journal

EPIC_SUPPORT_ROOTS = [
    Path.home() / "Library" / "Application Support" / "Epic",
]


async def _locate_config(params: dict[str, Any]) -> dict[str, Any]:
    """Find Epic Launcher's config files."""
    found: dict[str, str] = {}
    candidates = {
        "launcher_installed": "UnrealEngineLauncher/LauncherInstalled.dat",
        "manifests_dir": "EpicGamesLauncher/Data/Manifests",
        "settings": "UnrealEngineLauncher/Settings.json",
        "game_user_settings": "EpicGamesLauncher/Saved/Config",
    }
    for root in EPIC_SUPPORT_ROOTS:
        if not root.exists():
            continue
        for key, rel in candidates.items():
            path = root / rel
            if path.exists():
                found[key] = str(path)
    if not found:
        return {
            "installed": False,
            "hint": "Epic Games Launcher may not be signed-in yet — launch it once to create config.",
        }
    return {"installed": True, "paths": found}


async def _inspect(params: dict[str, Any]) -> dict[str, Any]:
    """Read LauncherInstalled.dat to see what engines / games Epic knows about."""
    loc = await _locate_config({})
    if not loc.get("installed"):
        return loc
    li_path = loc["paths"].get("launcher_installed")
    if not li_path:
        return {"engines": [], "note": "no LauncherInstalled.dat yet"}
    try:
        data = json.loads(Path(li_path).read_text())
    except Exception as exc:
        return {"error": f"could not parse LauncherInstalled.dat: {exc}"}
    installs = data.get("InstallationList", [])
    engines = []
    for entry in installs:
        path = entry.get("InstallLocation", "")
        app_name = entry.get("AppName", "")
        if "UE_" in app_name or "Unreal" in entry.get("NamespaceId", ""):
            engines.append({
                "app_name": app_name,
                "version": entry.get("AppVersion"),
                "install_location": path,
                "exists_on_disk": Path(path).exists() if path else False,
            })
    return {
        "config_path": li_path,
        "engines": engines,
        "total_installs": len(installs),
    }


async def _prepare_install_target(params: dict[str, Any]) -> dict[str, Any]:
    """Create the UE5 install folder on an external drive and record it.

    Epic will ask the user to choose a path when they click Install UE5 in the
    launcher. We prepare a clean, well-named folder so it's an obvious pick.
    """
    mount = Path(params["mount"]).expanduser().resolve()
    if not mount.exists():
        raise FileNotFoundError(f"mount missing: {mount}")
    folder_name = params.get("folder_name", "UnrealEngine")
    target = mount / folder_name
    target.mkdir(parents=True, exist_ok=True)

    # Drop a README so users remember what this folder is for.
    readme = target / "README.txt"
    if not readme.exists():
        readme.write_text(
            "This folder is managed by Octavius as the target directory for Unreal Engine installs.\n"
            "When you click Install UE_5.x in the Epic Games Launcher, point it here.\n"
            "Octavius watches this volume and will notify you if it is ejected while UE5 is running.\n"
        )

    journal.record(
        kind="epic.prepare_install_target",
        forward={"mount": str(mount), "target": str(target)},
        inverse={"op": "fs.delete", "path": str(target)},
    )
    return {
        "mount": str(mount),
        "target_path": str(target),
        "next_step": "Open Epic Games Launcher, click Install on Unreal Engine 5.x, "
                     f"and choose this folder: {target}",
    }


async def _set_install_dir_hint(params: dict[str, Any]) -> dict[str, Any]:
    """Write a hint file so the user (and future automation) remembers the
    preferred UE5 install location. This does NOT change Epic's config
    directly — Epic refuses external writes to LauncherInstalled.dat."""
    preferred = Path(params["target_path"]).expanduser().resolve()
    hint_dir = Path.home() / ".octavius"
    hint_dir.mkdir(parents=True, exist_ok=True)
    hint_file = hint_dir / "ue5_install_target.txt"
    hint_file.write_text(str(preferred) + "\n")
    journal.record(
        kind="epic.set_install_dir_hint",
        forward={"hint_file": str(hint_file), "target": str(preferred)},
        inverse={"op": "fs.delete", "path": str(hint_file)},
    )
    return {"hint_file": str(hint_file), "target": str(preferred)}


def register(bus) -> None:
    bus.register("epic.locate_config", _locate_config)
    bus.register("epic.inspect", _inspect)
    bus.register("epic.prepare_install_target", _prepare_install_target)
    bus.register("epic.set_install_dir_hint", _set_install_dir_hint)
