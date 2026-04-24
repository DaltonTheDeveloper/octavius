"""UI automation fallback — AppleScript System Events for button clicks.

Used only when the API path (legendary) doesn't work. Brittle: any UI
change in the target app breaks us. Keep calls narrow and always give
the user an approval prompt first.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .. import journal


async def _osascript(script: str, timeout: int = 20) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        "osascript", "-e", script,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", "timeout"
    return proc.returncode or 0, out.decode(errors="replace"), err.decode(errors="replace")


async def _click_by_label(params: dict[str, Any]) -> dict[str, Any]:
    """Click a button in the frontmost window of <app> whose name contains <label>."""
    app = params["app"]
    label = params["label"]
    # Bring app to front, then use System Events to click the first matching button.
    script = f'''
    tell application "{app}" to activate
    delay 0.5
    tell application "System Events"
      tell process "{app}"
        set theButtons to every button of window 1 whose name contains "{label}"
        if (count of theButtons) = 0 then
          -- search deeper: any UI element with the label
          set theButtons to (entire contents of window 1)
          repeat with b in theButtons
            try
              if (role of b is "AXButton") and ((name of b contains "{label}") or (title of b contains "{label}")) then
                click b
                return "clicked: " & (name of b)
              end if
            end try
          end repeat
          error "no button labeled {label}"
        end if
        click first item of theButtons
        return "clicked: " & (name of first item of theButtons)
      end tell
    end tell
    '''
    code, out, err = await _osascript(script)
    if code != 0:
        raise RuntimeError(f"click_by_label failed: {err.strip() or 'unknown'}")
    journal.record(
        kind="ui.click_by_label",
        forward={"app": app, "label": label, "result": out.strip()},
        inverse=None,
    )
    return {"clicked": True, "result": out.strip()}


async def _type_text(params: dict[str, Any]) -> dict[str, Any]:
    """Type text into the frontmost app."""
    app = params["app"]
    text = params["text"]
    # Escape quotes for AppleScript
    text_esc = text.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
    tell application "{app}" to activate
    delay 0.3
    tell application "System Events" to keystroke "{text_esc}"
    '''
    code, out, err = await _osascript(script)
    if code != 0:
        raise RuntimeError(f"type_text failed: {err.strip()}")
    journal.record(kind="ui.type_text", forward={"app": app, "chars": len(text)}, inverse=None)
    return {"typed": len(text)}


async def _keystroke(params: dict[str, Any]) -> dict[str, Any]:
    """Send a single keystroke combo, e.g. {keys: 'return'} or {keys: 'v', with: 'command down'}."""
    keys = params["keys"]
    with_ = params.get("with")
    if with_:
        script = f'tell application "System Events" to keystroke "{keys}" using {{{with_}}}'
    else:
        # for named keys like return, tab, escape
        named = {"return": "return", "tab": "tab", "escape": "53", "enter": "return"}
        if keys in named and keys != "escape":
            script = f'tell application "System Events" to key code (ASCII character of keys in named.get("{keys}") as integer)'
            script = f'tell application "System Events" to keystroke return'
        else:
            script = f'tell application "System Events" to keystroke "{keys}"'
    code, out, err = await _osascript(script)
    if code != 0:
        raise RuntimeError(f"keystroke failed: {err.strip()}")
    return {"sent": keys}


def register(bus) -> None:
    bus.register("ui.click_by_label", _click_by_label)
    bus.register("ui.type_text", _type_text)
    bus.register("ui.keystroke", _keystroke)
