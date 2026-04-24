"""Shell capability — runs commands. Forward only (shell isn't reversible)."""
from __future__ import annotations

import asyncio
import shlex
from typing import Any

from .. import journal


async def _run(params: dict[str, Any]) -> dict[str, Any]:
    cmd = params["cmd"]
    cwd = params.get("cwd")
    timeout = params.get("timeout", 60)

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"shell timed out after {timeout}s")

    result = {
        "exit_code": proc.returncode,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }
    journal.record(
        kind="shell.run",
        forward={"cmd": cmd, "cwd": cwd, "exit_code": proc.returncode},
        inverse=None,
    )
    return result


def register(bus) -> None:
    bus.register("shell.run", _run)
