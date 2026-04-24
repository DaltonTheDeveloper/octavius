"""Action bus — pending queue, approval events, live SSE feed."""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Awaitable, Callable

from .config import APPROVAL_TIMEOUT_SECONDS

Executor = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass
class PendingAction:
    id: str
    capability: str           # e.g. "fs.move", "shell.run", "ue5.move_project"
    summary: str              # human-readable one-liner for the UI
    detail: str               # multi-line description / dry-run preview
    params: dict[str, Any]
    danger: str = "medium"    # low | medium | high
    status: str = "pending"   # pending | approved | rejected | running | done | failed | timeout
    result: dict[str, Any] | None = None
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    error: str | None = None


class Bus:
    def __init__(self) -> None:
        self._pending: dict[str, PendingAction] = {}
        self._executors: dict[str, Executor] = {}
        self._approval_events: dict[str, asyncio.Event] = {}
        self._listeners: list[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    # ---- registration ----

    def register(self, capability: str, executor: Executor) -> None:
        self._executors[capability] = executor

    def capabilities(self) -> list[str]:
        return sorted(self._executors.keys())

    # ---- propose / approve / reject ----

    async def propose(
        self,
        capability: str,
        summary: str,
        params: dict[str, Any],
        detail: str = "",
        danger: str = "medium",
    ) -> PendingAction:
        if capability not in self._executors:
            raise KeyError(f"unknown capability: {capability}")
        action = PendingAction(
            id=uuid.uuid4().hex[:10],
            capability=capability,
            summary=summary,
            detail=detail,
            params=params,
            danger=danger,
        )
        async with self._lock:
            self._pending[action.id] = action
            self._approval_events[action.id] = asyncio.Event()
        await self._broadcast({"type": "proposed", "action": asdict(action)})
        # Spawn the wait-and-run loop so approval always triggers execution
        # even when the proposer didn't await.
        asyncio.create_task(self._background_wait_and_run(action.id))
        return action

    async def _background_wait_and_run(self, action_id: str) -> None:
        try:
            await self.wait_and_run(action_id)
        except Exception:
            pass

    async def approve(self, action_id: str) -> PendingAction:
        async with self._lock:
            action = self._pending.get(action_id)
            if not action:
                raise KeyError(action_id)
            if action.status != "pending":
                return action
            action.status = "approved"
            self._approval_events[action_id].set()
        await self._broadcast({"type": "approved", "action": asdict(action)})
        return action

    async def reject(self, action_id: str, reason: str = "") -> PendingAction:
        async with self._lock:
            action = self._pending.get(action_id)
            if not action:
                raise KeyError(action_id)
            if action.status != "pending":
                return action
            action.status = "rejected"
            action.error = reason or "rejected by user"
            action.resolved_at = time.time()
            self._approval_events[action_id].set()
        await self._broadcast({"type": "rejected", "action": asdict(action)})
        return action

    # ---- run loop ----

    async def wait_and_run(self, action_id: str) -> PendingAction:
        """Block until user approves or rejects, then execute. Returns the resolved action."""
        action = self._pending[action_id]
        event = self._approval_events[action_id]
        try:
            await asyncio.wait_for(event.wait(), timeout=APPROVAL_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            action.status = "timeout"
            action.error = f"no approval within {APPROVAL_TIMEOUT_SECONDS}s"
            action.resolved_at = time.time()
            await self._broadcast({"type": "timeout", "action": asdict(action)})
            return action

        if action.status == "rejected":
            return action

        # approved → execute
        action.status = "running"
        await self._broadcast({"type": "running", "action": asdict(action)})
        try:
            result = await self._executors[action.capability](action.params)
            action.result = result
            action.status = "done"
        except Exception as exc:  # noqa: BLE001
            action.status = "failed"
            action.error = f"{type(exc).__name__}: {exc}"
        finally:
            action.resolved_at = time.time()
            await self._broadcast({"type": "resolved", "action": asdict(action)})
        return action

    # ---- accessors ----

    def get(self, action_id: str) -> PendingAction | None:
        return self._pending.get(action_id)

    def list_pending(self) -> list[dict]:
        return [asdict(a) for a in self._pending.values() if a.status == "pending"]

    def list_recent(self, limit: int = 30) -> list[dict]:
        items = sorted(self._pending.values(), key=lambda a: a.created_at, reverse=True)
        return [asdict(a) for a in items[:limit]]

    # ---- SSE plumbing ----

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=64)
        self._listeners.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._listeners:
            self._listeners.remove(q)

    async def _broadcast(self, event: dict) -> None:
        for q in list(self._listeners):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


bus = Bus()
