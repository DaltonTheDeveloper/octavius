"""Filesystem capability — move, copy, write, delete. All journaled with inverses."""
from __future__ import annotations

import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any

from .. import journal
from ..config import DATA_DIR

TRASH = DATA_DIR / "trash"
TRASH.mkdir(exist_ok=True)


async def _move(params: dict[str, Any]) -> dict[str, Any]:
    src = Path(params["src"]).expanduser().resolve()
    dst = Path(params["dst"]).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"source does not exist: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    # offload the actual move to a thread (can be slow on big dirs)
    await asyncio.to_thread(shutil.move, str(src), str(dst))
    journal.record(
        kind="fs.move",
        forward={"src": str(src), "dst": str(dst)},
        inverse={"op": "fs.move", "src": str(dst), "dst": str(src)},
    )
    return {"moved": str(dst)}


async def _copy(params: dict[str, Any]) -> dict[str, Any]:
    src = Path(params["src"]).expanduser().resolve()
    dst = Path(params["dst"]).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"source does not exist: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        await asyncio.to_thread(shutil.copytree, str(src), str(dst), dirs_exist_ok=False)
    else:
        await asyncio.to_thread(shutil.copy2, str(src), str(dst))
    journal.record(
        kind="fs.copy",
        forward={"src": str(src), "dst": str(dst)},
        inverse={"op": "fs.delete", "path": str(dst)},
    )
    return {"copied": str(dst)}


async def _write(params: dict[str, Any]) -> dict[str, Any]:
    path = Path(params["path"]).expanduser().resolve()
    new = params["content"]
    prev = path.read_text() if path.exists() else None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new)
    inverse: dict[str, Any]
    if prev is None:
        inverse = {"op": "fs.delete", "path": str(path)}
    else:
        inverse = {"op": "fs.write", "path": str(path), "content": prev}
    journal.record(
        kind="fs.write",
        forward={"path": str(path), "bytes": len(new.encode())},
        inverse=inverse,
    )
    return {"wrote": str(path), "bytes": len(new.encode())}


async def _delete(params: dict[str, Any]) -> dict[str, Any]:
    path = Path(params["path"]).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"does not exist: {path}")
    # move to trash so we can restore
    trash_name = f"{uuid.uuid4().hex[:8]}_{path.name}"
    backup = TRASH / trash_name
    await asyncio.to_thread(shutil.move, str(path), str(backup))
    journal.record(
        kind="fs.delete",
        forward={"path": str(path), "trash": str(backup)},
        inverse={"op": "fs.restore", "backup": str(backup), "dst": str(path)},
    )
    return {"deleted": str(path), "trash": str(backup)}


def register(bus) -> None:
    bus.register("fs.move", _move)
    bus.register("fs.copy", _copy)
    bus.register("fs.write", _write)
    bus.register("fs.delete", _delete)
