"""FastAPI app — confirmation UI + JSON API + SSE feed."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from . import graph as graph_mod
from . import journal as journal_mod
from .bus import bus
from .mcp_server import mcp

UI_DIR = Path(__file__).parent / "ui"


def create_app() -> FastAPI:
    app = FastAPI(title="Octavius Host Bus")

    # Mount the MCP HTTP app at /mcp.
    app.mount("/mcp", mcp.streamable_http_app())

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        return HTMLResponse((UI_DIR / "index.html").read_text())

    @app.get("/api/graph")
    async def api_graph(detail: str = "summary") -> dict:
        if detail == "full":
            return graph_mod.snapshot().to_dict()
        return graph_mod.summary()

    @app.get("/api/capabilities")
    async def api_capabilities() -> list[str]:
        return bus.capabilities()

    @app.get("/api/pending")
    async def api_pending() -> list[dict]:
        return bus.list_pending()

    @app.get("/api/recent")
    async def api_recent(limit: int = 30) -> list[dict]:
        return bus.list_recent(limit=limit)

    @app.get("/api/journal")
    async def api_journal(limit: int = 30) -> list[dict]:
        return journal_mod.list_recent(limit=limit)

    @app.post("/api/propose")
    async def api_propose(payload: dict) -> dict:
        """Mirror of the MCP propose_action tool — useful for HTTP testing.

        propose() spawns the background runner internally, so we just poll
        for terminal status when the caller wants to wait.
        """
        from dataclasses import asdict
        wait = payload.pop("wait", True)
        action = await bus.propose(
            capability=payload["capability"],
            summary=payload["summary"],
            params=payload.get("params", {}),
            detail=payload.get("detail", ""),
            danger=payload.get("danger", "medium"),
        )
        if not wait:
            return asdict(action)
        # poll for terminal status
        for _ in range(600):
            current = bus.get(action.id)
            if current and current.status in ("done", "failed", "rejected", "timeout"):
                return asdict(current)
            await asyncio.sleep(0.1)
        return asdict(bus.get(action.id))

    @app.post("/api/approve/{action_id}")
    async def api_approve(action_id: str) -> dict:
        try:
            a = await bus.approve(action_id)
        except KeyError:
            raise HTTPException(404, "unknown action")
        from dataclasses import asdict
        return asdict(a)

    @app.post("/api/reject/{action_id}")
    async def api_reject(action_id: str, reason: str = "") -> dict:
        try:
            a = await bus.reject(action_id, reason=reason)
        except KeyError:
            raise HTTPException(404, "unknown action")
        from dataclasses import asdict
        return asdict(a)

    @app.post("/api/undo")
    async def api_undo(count: int = 1) -> list[dict]:
        return journal_mod.undo(count=count)

    @app.get("/api/events")
    async def api_events():
        async def gen():
            q = bus.subscribe()
            try:
                while True:
                    try:
                        evt = await asyncio.wait_for(q.get(), timeout=15)
                        yield {"event": evt["type"], "data": json.dumps(evt)}
                    except asyncio.TimeoutError:
                        # heartbeat
                        yield {"event": "ping", "data": "{}"}
            finally:
                bus.unsubscribe(q)
        return EventSourceResponse(gen())

    return app
