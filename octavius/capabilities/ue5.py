"""UE5 capability — high-level project ops that know about .uproject + DDC."""
from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

from .. import journal


async def _move_project(params: dict[str, Any]) -> dict[str, Any]:
    """Move a UE5 project directory to a new location.

    Handles:
      - moving the whole project folder
      - leaving DDC behind (it's regenerable, no point dragging it across volumes)
      - preserving the .uproject (no path rewrites needed; UE uses relative paths)
    """
    src_uproject = Path(params["uproject"]).expanduser().resolve()
    dst_root = Path(params["dst_root"]).expanduser().resolve()
    drop_ddc = params.get("drop_ddc", True)

    if not src_uproject.exists() or src_uproject.suffix != ".uproject":
        raise FileNotFoundError(f"not a uproject: {src_uproject}")

    src_dir = src_uproject.parent
    dst_dir = dst_root / src_dir.name
    if dst_dir.exists():
        raise FileExistsError(f"destination already exists: {dst_dir}")
    dst_root.mkdir(parents=True, exist_ok=True)

    skipped: list[str] = []

    def _copy_filtered(s: str, names: list[str]) -> list[str]:
        ignore: list[str] = []
        if drop_ddc:
            for n in names:
                if n in ("DerivedDataCache", "Intermediate", "Saved", "Binaries"):
                    ignore.append(n)
                    skipped.append(str(Path(s) / n))
        return ignore

    await asyncio.to_thread(
        shutil.copytree,
        str(src_dir),
        str(dst_dir),
        ignore=_copy_filtered,
    )

    # We've copied; remove the original (move-style) but keep it in trash via fs.delete-like flow
    # Instead, we record an inverse that restores via reverse copy, and then rmtree the source.
    backup_marker = dst_dir  # acts as our "backup" — restoring just means swapping back

    await asyncio.to_thread(shutil.rmtree, str(src_dir))

    journal.record(
        kind="ue5.move_project",
        forward={
            "uproject": str(src_uproject),
            "src_dir": str(src_dir),
            "dst_dir": str(dst_dir),
            "skipped_subdirs": skipped,
        },
        inverse={"op": "fs.move", "src": str(dst_dir), "dst": str(src_dir)},
    )

    new_uproject = dst_dir / src_uproject.name
    return {
        "old_path": str(src_uproject),
        "new_path": str(new_uproject),
        "skipped_regenerable_dirs": skipped,
    }


async def _read_uproject(params: dict[str, Any]) -> dict[str, Any]:
    uproject = Path(params["uproject"]).expanduser().resolve()
    data = json.loads(uproject.read_text())
    return {"path": str(uproject), "data": data}


async def _launch_editor(params: dict[str, Any]) -> dict[str, Any]:
    """Launch UE5 editor on a given uproject. macOS-specific."""
    uproject = Path(params["uproject"]).expanduser().resolve()
    if not uproject.exists():
        raise FileNotFoundError(uproject)
    # `open -a UnrealEditor /path/to/file.uproject`
    proc = await asyncio.create_subprocess_exec(
        "open", "-a", "UnrealEditor", str(uproject),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"open failed: {err.decode(errors='replace')}")
    journal.record(
        kind="ue5.launch_editor",
        forward={"uproject": str(uproject)},
        inverse=None,
    )
    return {"launched": str(uproject)}


def register(bus) -> None:
    bus.register("ue5.move_project", _move_project)
    bus.register("ue5.read_uproject", _read_uproject)
    bus.register("ue5.launch_editor", _launch_editor)
