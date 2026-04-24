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


async def _create_project_skeleton(params: dict[str, Any]) -> dict[str, Any]:
    """Create a minimal valid UE5 project structure (no engine required to scaffold).

    Layout written:
        <root>/<name>/<name>.uproject     # JSON, valid for UE 5.4+
        <root>/<name>/Content/            # asset library root
        <root>/<name>/Config/DefaultEngine.ini
        <root>/<name>/Source/             # placeholder
    """
    root = Path(params["root"]).expanduser().resolve()
    name = params["name"]
    engine = params.get("engine_association", "5.4")

    project_dir = root / name
    if project_dir.exists():
        raise FileExistsError(f"already exists: {project_dir}")

    project_dir.mkdir(parents=True)
    (project_dir / "Content").mkdir()
    (project_dir / "Source").mkdir()
    (project_dir / "Config").mkdir()

    uproject = project_dir / f"{name}.uproject"
    uproject_data = {
        "FileVersion": 3,
        "EngineAssociation": engine,
        "Category": "",
        "Description": "Scaffolded by Octavius.",
        "Modules": [],
        "Plugins": [],
    }
    uproject.write_text(json.dumps(uproject_data, indent=2))

    (project_dir / "Config" / "DefaultEngine.ini").write_text(
        "[/Script/EngineSettings.GameMapsSettings]\n"
        "GameDefaultMap=/Engine/Maps/Templates/OpenWorld\n"
    )

    journal.record(
        kind="ue5.create_project_skeleton",
        forward={"project_dir": str(project_dir), "uproject": str(uproject)},
        inverse={"op": "fs.delete", "path": str(project_dir)},
    )
    return {
        "project_dir": str(project_dir),
        "uproject": str(uproject),
        "content_dir": str(project_dir / "Content"),
    }


async def _create_asset_file(params: dict[str, Any]) -> dict[str, Any]:
    """Create a file inside a UE5 project's Content/<library>/ folder.

    For binary asset creation (true .uasset) you'd round-trip through the editor's
    Python API; this capability handles the common case of staging text/json/CSV
    data that Unreal Data Tables and Curve Tables can import directly.
    """
    uproject = Path(params["uproject"]).expanduser().resolve()
    if not uproject.exists() or uproject.suffix != ".uproject":
        raise FileNotFoundError(f"not a uproject: {uproject}")

    library = params.get("library", "OctaviusTest")
    filename = params["filename"]
    content = params.get("content", "")

    content_root = uproject.parent / "Content"
    target_dir = content_root / library
    target_dir.mkdir(parents=True, exist_ok=True)

    target = target_dir / filename
    if target.exists():
        raise FileExistsError(f"file already exists: {target}")

    target.write_text(content)

    journal.record(
        kind="ue5.create_asset_file",
        forward={"path": str(target), "uproject": str(uproject), "library": library},
        inverse={"op": "fs.delete", "path": str(target)},
    )
    return {
        "path": str(target),
        "library": library,
        "uproject": str(uproject),
        "bytes": len(content.encode()),
    }


def register(bus) -> None:
    bus.register("ue5.move_project", _move_project)
    bus.register("ue5.read_uproject", _read_uproject)
    bus.register("ue5.launch_editor", _launch_editor)
    bus.register("ue5.create_project_skeleton", _create_project_skeleton)
    bus.register("ue5.create_asset_file", _create_asset_file)
