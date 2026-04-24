"""MCP server exposed at /mcp. Claude Code connects here over HTTP."""
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import graph as graph_mod
from . import journal as journal_mod
from .bus import bus

mcp = FastMCP("octavius")


@mcp.tool()
async def query_graph(detail: str = "summary") -> dict[str, Any]:
    """Return the live machine graph.

    Args:
        detail: "summary" (top processes only) or "full" (everything).
    """
    if detail == "full":
        return graph_mod.snapshot().to_dict()
    return graph_mod.summary()


@mcp.tool()
async def list_capabilities() -> list[str]:
    """List capability names this host bus exposes."""
    return bus.capabilities()


@mcp.tool()
async def propose_action(
    capability: str,
    summary: str,
    params: dict,
    detail: str = "",
    danger: str = "medium",
    wait: bool = True,
) -> dict[str, Any]:
    """Queue an action for the user to approve in the Octavius UI.

    Returns immediately with status="pending" if wait=False; otherwise blocks
    until the user approves/rejects (or until approval timeout) and returns
    the resolved action.

    Args:
        capability: e.g. "fs.move", "shell.run", "ue5.move_project", "chrome.open_url".
        summary: short human-readable label shown on the approval button.
        params: capability-specific parameters.
        detail: longer multi-line description (dry-run preview, file counts, sizes...).
        danger: "low" | "medium" | "high" — affects UI color coding.
        wait: if True, block until resolved.
    """
    action = await bus.propose(capability, summary, params, detail=detail, danger=danger)
    if not wait:
        from dataclasses import asdict
        return asdict(action)
    resolved = await bus.wait_and_run(action.id)
    from dataclasses import asdict
    return asdict(resolved)


@mcp.tool()
async def action_status(action_id: str) -> dict[str, Any]:
    """Check status of a previously proposed action."""
    a = bus.get(action_id)
    if not a:
        return {"error": f"unknown action: {action_id}"}
    from dataclasses import asdict
    return asdict(a)


@mcp.tool()
async def list_journal(limit: int = 20) -> list[dict]:
    """Recent committed actions (most recent last)."""
    return journal_mod.list_recent(limit=limit)


@mcp.tool()
async def undo(count: int = 1) -> list[dict]:
    """Reverse the last N reversible actions. Returns what was undone."""
    return journal_mod.undo(count=count)
