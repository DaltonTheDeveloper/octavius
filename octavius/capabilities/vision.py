"""Vision capabilities — calibrated screenshots + color-based button detection.

Codifies the technique that defeated Epic Games Launcher's Qt opacity:
  1. Screenshot a window by CGWindowID.
  2. Calibrate via the macOS traffic-light close button (always at fixed
     window-local offset).
  3. Locate UI elements by color centroid (e.g. yellow Install button).
  4. Click in screen coordinates via cliclick (which inherits the
     parent process's Accessibility permission).

Works on any walled-garden app whose buttons have distinctive colors.
"""
from __future__ import annotations

import asyncio
import shutil
import time
from pathlib import Path
from typing import Any

from .. import journal
from ..config import DATA_DIR

SCREEN_DIR = DATA_DIR / "screens"
SCREEN_DIR.mkdir(exist_ok=True)


def _list_windows_for_app(app_substring: str) -> list[dict]:
    """Use Quartz to enumerate on-screen windows for a given app."""
    try:
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGWindowListExcludeDesktopElements,
            kCGNullWindowID,
        )
    except ImportError:
        return []
    wins = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements, kCGNullWindowID
    )
    out = []
    for w in wins:
        owner = w.get("kCGWindowOwnerName", "") or ""
        if app_substring.lower() in owner.lower():
            b = dict(w.get("kCGWindowBounds", {}))
            out.append({
                "window_id": w.get("kCGWindowNumber"),
                "owner": owner,
                "name": w.get("kCGWindowName", "") or "",
                "bounds": b,
                "layer": w.get("kCGWindowLayer"),
            })
    return out


async def _list_windows(params: dict[str, Any]) -> dict[str, Any]:
    return {"windows": _list_windows_for_app(params.get("app", ""))}


async def _capture_window(params: dict[str, Any]) -> dict[str, Any]:
    """Screenshot a window by CGWindowID. Returns the path."""
    window_id = int(params["window_id"])
    name = params.get("name", f"win_{window_id}_{int(time.time())}.png")
    out_path = SCREEN_DIR / name
    proc = await asyncio.create_subprocess_exec(
        "screencapture", "-x", "-l", str(window_id), str(out_path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    if not out_path.exists():
        raise RuntimeError(f"screencapture failed: {err.decode(errors='replace')}")
    return {"path": str(out_path), "window_id": window_id}


def _find_color_region(png_path: str, target_rgb: tuple[int, int, int],
                       tolerance: int = 30,
                       region: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)
                       ) -> dict | None:
    """Scan PNG for pixels matching target_rgb within tolerance.
    region is (x0, y0, x1, y1) as fractions of image dims to search.
    Returns centroid + bbox in PNG pixel coords, or None if no pixels found.
    """
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError("Pillow not installed; pip install pillow")
    im = Image.open(png_path)
    w, h = im.size
    px = im.load()
    tr, tg, tb = target_rgb
    x0, y0, x1, y1 = int(w*region[0]), int(h*region[1]), int(w*region[2]), int(h*region[3])
    matches = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            pix = px[x, y]
            r, g, b = pix[0], pix[1], pix[2]
            if abs(r-tr) <= tolerance and abs(g-tg) <= tolerance and abs(b-tb) <= tolerance:
                matches.append((x, y))
    if not matches:
        return None
    xs, ys = [p[0] for p in matches], [p[1] for p in matches]
    return {
        "centroid_px": (sum(xs)//len(xs), sum(ys)//len(ys)),
        "bbox_px": (min(xs), min(ys), max(xs), max(ys)),
        "match_count": len(matches),
        "image_size": (w, h),
    }


async def _calibrate_window(params: dict[str, Any]) -> dict[str, Any]:
    """Find the macOS traffic-light close (red) button to calibrate
    PNG-pixel ↔ screen-point mapping.

    Standard close button is at window-local (~14, 14) points (varies by
    OS slightly). Returns the offset and scale needed to translate any
    PNG pixel into a screen point.
    """
    window_id = int(params["window_id"])
    cap = await _capture_window({"window_id": window_id, "name": f"calibrate_{window_id}.png"})
    png_path = cap["path"]
    # Find red close button in top-left
    red = await asyncio.to_thread(
        _find_color_region, png_path, (255, 95, 87), 25, (0.0, 0.0, 0.08, 0.08),
    )
    if not red:
        raise RuntimeError("calibration failed: no traffic-light red found in top-left")
    # Locate the window's bounds in screen points
    wins = _list_windows_for_app("")  # any
    matched = None
    for w in wins:
        if w["window_id"] == window_id:
            matched = w
            break
    if not matched:
        raise RuntimeError(f"window {window_id} not found")
    win_x = matched["bounds"]["X"]
    win_y = matched["bounds"]["Y"]
    win_w = matched["bounds"]["Width"]
    win_h = matched["bounds"]["Height"]
    # Close button is at ~(14, 14) in window-local POINTS. Retina = 2x.
    close_local_pt = (14, 14)
    px_x, px_y = red["centroid_px"]
    # PNG offset relative to window origin in pixels:
    png_origin_px_x = px_x - close_local_pt[0] * 2
    png_origin_px_y = px_y - close_local_pt[1] * 2
    return {
        "window_id": window_id,
        "screenshot": png_path,
        "image_size": red["image_size"],
        "window_screen_origin": {"x": win_x, "y": win_y},
        "window_size_pt": {"w": win_w, "h": win_h},
        "png_origin_offset_px": {"x": png_origin_px_x, "y": png_origin_px_y},
        "retina_scale": 2.0,
    }


async def _find_button_by_color(params: dict[str, Any]) -> dict[str, Any]:
    """Locate a button by its dominant color in a calibrated window.

    params:
      window_id: int
      color: [R,G,B] of the button
      tolerance: int (default 25)
      region: [x0,y0,x1,y1] fractional search area (default whole window)
    returns: screen-point center to click + bbox.
    """
    cal = await _calibrate_window({"window_id": int(params["window_id"])})
    color = tuple(params["color"])
    region = tuple(params.get("region", [0.0, 0.0, 1.0, 1.0]))
    found = await asyncio.to_thread(
        _find_color_region, cal["screenshot"], color,
        params.get("tolerance", 25), region,
    )
    if not found:
        raise RuntimeError(f"no pixels matched {color} in region {region}")
    px_x, px_y = found["centroid_px"]
    win_x = (px_x - cal["png_origin_offset_px"]["x"]) / cal["retina_scale"]
    win_y = (px_y - cal["png_origin_offset_px"]["y"]) / cal["retina_scale"]
    screen_x = cal["window_screen_origin"]["x"] + win_x
    screen_y = cal["window_screen_origin"]["y"] + win_y
    return {
        "screen_point": {"x": int(screen_x), "y": int(screen_y)},
        "bbox_px": found["bbox_px"],
        "match_count": found["match_count"],
        "calibration": cal,
    }


async def _click_calibrated(params: dict[str, Any]) -> dict[str, Any]:
    """Find a button by color and click it. One-shot for the common case."""
    found = await _find_button_by_color(params)
    sp = found["screen_point"]
    cliclick = shutil.which("cliclick")
    if not cliclick:
        raise RuntimeError("cliclick not installed; brew install cliclick")
    proc = await asyncio.create_subprocess_exec(
        cliclick, f"m:{sp['x']},{sp['y']}", "w:200", f"c:{sp['x']},{sp['y']}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    journal.record(
        kind="vision.click_calibrated",
        forward={"window_id": params["window_id"], "color": params["color"], "click_at": sp},
        inverse=None,
    )
    return {"clicked_at": sp, "stderr": err.decode(errors="replace")}


def register(bus) -> None:
    bus.register("vision.list_windows", _list_windows)
    bus.register("vision.capture_window", _capture_window)
    bus.register("vision.calibrate_window", _calibrate_window)
    bus.register("vision.find_button_by_color", _find_button_by_color)
    bus.register("vision.click_calibrated", _click_calibrated)
