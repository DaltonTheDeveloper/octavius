"""Chrome capability — drive Chrome via AppleScript on macOS."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from .. import journal


async def _osascript(script: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "osascript", "-e", script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"osascript failed: {err.decode(errors='replace').strip()}")
    return out.decode(errors="replace").strip()


async def _open_url(params: dict[str, Any]) -> dict[str, Any]:
    url = params["url"]
    new_tab = params.get("new_tab", True)
    if new_tab:
        script = (
            'tell application "Google Chrome"\n'
            '  activate\n'
            f'  tell window 1 to make new tab with properties {{URL:"{url}"}}\n'
            'end tell'
        )
    else:
        script = (
            'tell application "Google Chrome"\n'
            '  activate\n'
            f'  set URL of active tab of window 1 to "{url}"\n'
            'end tell'
        )
    await _osascript(script)
    journal.record(
        kind="chrome.open_url",
        forward={"url": url, "new_tab": new_tab},
        inverse=None,
    )
    return {"opened": url}


async def _list_tabs(params: dict[str, Any]) -> dict[str, Any]:
    script = (
        'tell application "Google Chrome"\n'
        '  set tabList to {}\n'
        '  repeat with w in windows\n'
        '    repeat with t in tabs of w\n'
        '      set end of tabList to (title of t) & "\\t" & (URL of t)\n'
        '    end repeat\n'
        '  end repeat\n'
        '  set AppleScript\'s text item delimiters to linefeed\n'
        '  return tabList as text\n'
        'end tell'
    )
    raw = await _osascript(script)
    tabs = []
    for line in raw.splitlines():
        if "\t" in line:
            title, url = line.split("\t", 1)
            tabs.append({"title": title, "url": url})
    return {"tabs": tabs}


async def _run_js(params: dict[str, Any]) -> dict[str, Any]:
    """Execute JS in the active tab (requires 'Allow JavaScript from Apple Events' in Chrome)."""
    js = params["javascript"]
    escaped = js.replace("\\", "\\\\").replace('"', '\\"')
    script = (
        'tell application "Google Chrome"\n'
        f'  set theResult to execute active tab of window 1 javascript "{escaped}"\n'
        '  return theResult as text\n'
        'end tell'
    )
    out = await _osascript(script)
    journal.record(
        kind="chrome.run_js",
        forward={"javascript": js},
        inverse=None,
    )
    return {"result": out}


def register(bus) -> None:
    bus.register("chrome.open_url", _open_url)
    bus.register("chrome.list_tabs", _list_tabs)
    bus.register("chrome.run_js", _run_js)
