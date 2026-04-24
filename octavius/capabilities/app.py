"""Generic app capability — launch any macOS app by name."""
from __future__ import annotations

import asyncio
from typing import Any

from .. import journal


async def _launch(params: dict[str, Any]) -> dict[str, Any]:
    app = params["app"]
    args = params.get("args") or []
    proc = await asyncio.create_subprocess_exec(
        "open", "-a", app, *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"open failed: {err.decode(errors='replace')}")
    journal.record(
        kind="app.launch",
        forward={"app": app, "args": args},
        inverse=None,
    )
    return {"launched": app, "args": args}


def register(bus) -> None:
    bus.register("app.launch", _launch)
