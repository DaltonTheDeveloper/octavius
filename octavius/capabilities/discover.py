"""Discovery capability — introspect a macOS app and report control surfaces.

Given an /Applications/Foo.app path, probe:
  1. Info.plist (URL schemes, document types, XPC, bundle id, minimum OS)
  2. Scripting dictionary via `sdef` (AppleScript surface)
  3. Executable + helper binaries in Contents/MacOS
  4. Frameworks (Electron / CEF / Qt / Python detection)
  5. Entitlements via `codesign`
  6. Python / Lua / JS scripting resources
  7. Services + Automator actions (user-invokable hooks)

Produces a structured ControlSurfaces report Claude can read and use to
draft a new Octavius capability for that app.
"""
from __future__ import annotations

import asyncio
import json
import plistlib
import shutil
import subprocess
from pathlib import Path
from typing import Any


async def _sh(*cmd: str, timeout: int = 10) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", "timeout"
    return proc.returncode or 0, out.decode(errors="replace"), err.decode(errors="replace")


def _read_plist(path: Path) -> dict:
    try:
        with path.open("rb") as f:
            return plistlib.load(f)
    except Exception:
        return {}


async def _applescript_dict(app_path: Path) -> dict[str, Any]:
    """Returns a sdef summary: count of suites, commands, class names."""
    code, out, err = await _sh("sdef", str(app_path))
    if code != 0 or not out.strip():
        return {"scriptable": False}
    # Count commands + classes heuristically; parse XML for precision.
    import re
    commands = re.findall(r"<command name=\"([^\"]+)\"", out)
    classes = re.findall(r"<class name=\"([^\"]+)\"", out)
    return {
        "scriptable": True,
        "command_count": len(commands),
        "class_count": len(classes),
        "commands_sample": commands[:20],
        "classes_sample": classes[:20],
    }


def _detect_framework_flavor(app_path: Path) -> dict[str, Any]:
    """Detect common app frameworks — useful because each has a different control pathway."""
    frameworks = app_path / "Contents" / "Frameworks"
    flavors = {
        "electron": False,
        "cef": False,
        "qt": False,
        "python": False,
        "chromium": False,
        "webview": False,
    }
    if frameworks.exists():
        names = [f.name.lower() for f in frameworks.iterdir() if f.is_dir()]
        flavors["electron"] = any("electron" in n for n in names)
        flavors["cef"] = any("cef" in n or "chromiumembedded" in n for n in names)
        flavors["qt"] = any(n.startswith("qt") for n in names)
        flavors["python"] = any("python" in n for n in names)
        flavors["chromium"] = any("chromium" in n for n in names)
        flavors["webview"] = any("webkit" in n or "wkwebview" in n for n in names)
    return flavors


def _list_macos_binaries(app_path: Path) -> list[str]:
    macos = app_path / "Contents" / "MacOS"
    if not macos.exists():
        return []
    return [
        f.name for f in macos.iterdir()
        if f.is_file() and f.stat().st_mode & 0o100
    ][:50]


def _list_helpers(app_path: Path) -> list[str]:
    helpers = app_path / "Contents" / "Helpers"
    if not helpers.exists():
        return []
    return [f.name for f in helpers.iterdir() if f.is_dir() or f.is_file()][:50]


async def _entitlements(app_path: Path) -> dict[str, Any]:
    code, out, _ = await _sh(
        "codesign", "-d", "--entitlements", ":-", str(app_path), timeout=5
    )
    if code != 0 or not out.strip():
        return {}
    try:
        # codesign prints XML plist; parse it
        return plistlib.loads(out.encode())
    except Exception:
        return {"_raw": out[:2000]}


async def _discover(params: dict[str, Any]) -> dict[str, Any]:
    app_path_str = params["app_path"]
    app_path = Path(app_path_str).expanduser().resolve()
    if not app_path.exists() or not app_path.name.endswith(".app"):
        raise FileNotFoundError(f"not an .app bundle: {app_path}")

    info_plist = _read_plist(app_path / "Contents" / "Info.plist")
    bundle_id = info_plist.get("CFBundleIdentifier", "")
    name = info_plist.get("CFBundleName") or info_plist.get("CFBundleDisplayName") or app_path.stem
    url_schemes: list[str] = []
    for entry in info_plist.get("CFBundleURLTypes", []) or []:
        url_schemes.extend(entry.get("CFBundleURLSchemes", []) or [])
    doc_types = [
        {
            "name": d.get("CFBundleTypeName"),
            "extensions": d.get("CFBundleTypeExtensions"),
            "role": d.get("CFBundleTypeRole"),
        }
        for d in (info_plist.get("CFBundleDocumentTypes", []) or [])
    ]
    xpc_services: list[str] = []
    xpc_dir = app_path / "Contents" / "XPCServices"
    if xpc_dir.exists():
        xpc_services = [f.name for f in xpc_dir.iterdir()]

    # parallel the two subprocess calls
    script, flavor, ents, bin_list = await asyncio.gather(
        _applescript_dict(app_path),
        asyncio.to_thread(_detect_framework_flavor, app_path),
        _entitlements(app_path),
        asyncio.to_thread(_list_macos_binaries, app_path),
    )
    helpers = _list_helpers(app_path)

    # Recommend capability strategies
    recommendations: list[str] = []
    if script.get("scriptable"):
        recommendations.append(
            "AppleScript is available — use osascript via capabilities (like chrome.py)."
        )
    if flavor["electron"]:
        recommendations.append(
            "Electron app — enable --remote-debugging-port and drive via CDP (Chrome DevTools Protocol)."
        )
    if flavor["cef"]:
        recommendations.append(
            "CEF (Chromium Embedded) — similar to Electron; check for a DevTools port."
        )
    if flavor["python"]:
        recommendations.append(
            "Bundled Python — look for scriptable entry points in Contents/Resources/Scripts."
        )
    if url_schemes:
        recommendations.append(
            f"URL schemes registered: {url_schemes}. Use `open -u <scheme>://...` as a control pathway."
        )
    cli_likely = [b for b in bin_list if b not in (app_path.stem, name)]
    if cli_likely:
        recommendations.append(
            f"Potential CLI helpers in Contents/MacOS: {cli_likely[:6]}. Try --help on each."
        )
    if not recommendations:
        recommendations.append(
            "No obvious control surface — fall back to screenshot + AppleScript UI scripting."
        )

    report = {
        "app_path": str(app_path),
        "name": name,
        "bundle_id": bundle_id,
        "url_schemes": url_schemes,
        "document_types": doc_types,
        "xpc_services": xpc_services,
        "macos_binaries": bin_list,
        "helpers": helpers,
        "frameworks": flavor,
        "applescript": script,
        "entitlements_keys": list(ents.keys()) if isinstance(ents, dict) else [],
        "recommended_capability_strategies": recommendations,
    }
    return report


def register(bus) -> None:
    bus.register("app.discover", _discover)
