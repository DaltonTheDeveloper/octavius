"""Resumable job state — survives daemon restart.

A job is a long-running flow (e.g. work.md "download UE5"). Each job has:
  ~/.octavius/jobs/<job_id>/
    state.json      # current state, current step, vars
    log.txt         # human-readable progress
    snapshots/      # screenshots / artifacts captured along the way

Jobs are append-only journaled too — every checkpoint is a journal entry,
so undo / re-trace is possible.

Public verbs (capabilities):
  jobs.create({slug, vars}) -> job_id
  jobs.checkpoint({job_id, step, vars})
  jobs.complete({job_id, status, summary})
  jobs.list()
  jobs.get({job_id})
  jobs.resume({job_id}) -> next_step + accumulated state
  jobs.append_log({job_id, line})
"""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from .config import DATA_DIR
from . import journal as journal_mod

JOBS_DIR = DATA_DIR / "jobs"
JOBS_DIR.mkdir(exist_ok=True)


@dataclass
class Job:
    id: str
    slug: str
    status: str         # running | done | failed | cancelled | abandoned
    current_step: str
    vars: dict[str, Any]
    started_at: float
    updated_at: float
    completed_at: float | None = None
    summary: str = ""
    snapshots: list[str] = field(default_factory=list)


def _job_dir(job_id: str) -> Path:
    return JOBS_DIR / job_id


def _state_path(job_id: str) -> Path:
    return _job_dir(job_id) / "state.json"


def _log_path(job_id: str) -> Path:
    return _job_dir(job_id) / "log.txt"


def _snap_dir(job_id: str) -> Path:
    return _job_dir(job_id) / "snapshots"


def _save(job: Job) -> None:
    _state_path(job.id).write_text(json.dumps(asdict(job), indent=2))


def _load(job_id: str) -> Job | None:
    p = _state_path(job_id)
    if not p.exists():
        return None
    try:
        return Job(**json.loads(p.read_text()))
    except Exception:
        return None


async def _create(params: dict[str, Any]) -> dict[str, Any]:
    slug = params["slug"]
    job_id = f"{slug}-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    d = _job_dir(job_id)
    d.mkdir(parents=True, exist_ok=True)
    _snap_dir(job_id).mkdir(exist_ok=True)
    job = Job(
        id=job_id,
        slug=slug,
        status="running",
        current_step="start",
        vars=params.get("vars", {}),
        started_at=time.time(),
        updated_at=time.time(),
    )
    _save(job)
    _log_path(job_id).write_text(f"[{time.strftime('%H:%M:%S')}] job created: {slug}\n")
    journal_mod.record(
        kind="jobs.create",
        forward={"job_id": job_id, "slug": slug, "vars": job.vars},
        inverse={"op": "fs.delete", "path": str(d)},
    )
    return {"job_id": job_id, "dir": str(d)}


async def _checkpoint(params: dict[str, Any]) -> dict[str, Any]:
    job = _load(params["job_id"])
    if not job:
        raise FileNotFoundError(f"unknown job: {params['job_id']}")
    if "step" in params:
        job.current_step = params["step"]
    if "vars" in params:
        job.vars.update(params["vars"])
    job.updated_at = time.time()
    _save(job)
    line = params.get("note", f"checkpoint: step={job.current_step}")
    with _log_path(job.id).open("a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {line}\n")
    return {"job_id": job.id, "step": job.current_step, "vars": job.vars}


async def _complete(params: dict[str, Any]) -> dict[str, Any]:
    job = _load(params["job_id"])
    if not job:
        raise FileNotFoundError(f"unknown job: {params['job_id']}")
    job.status = params.get("status", "done")
    job.summary = params.get("summary", "")
    job.completed_at = time.time()
    job.updated_at = job.completed_at
    _save(job)
    with _log_path(job.id).open("a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] complete: {job.status} — {job.summary}\n")
    return {"job_id": job.id, "status": job.status}


async def _list_jobs(params: dict[str, Any]) -> dict[str, Any]:
    out: list[dict] = []
    for d in sorted(JOBS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not d.is_dir():
            continue
        job = _load(d.name)
        if job:
            out.append(asdict(job))
    return {"jobs": out[: params.get("limit", 30)]}


async def _get(params: dict[str, Any]) -> dict[str, Any]:
    job = _load(params["job_id"])
    if not job:
        raise FileNotFoundError(f"unknown job: {params['job_id']}")
    log = _log_path(job.id).read_text() if _log_path(job.id).exists() else ""
    return {"job": asdict(job), "log": log[-4000:]}


async def _resume(params: dict[str, Any]) -> dict[str, Any]:
    """Re-engage a job that was interrupted. Returns the last checkpoint so
    the caller (Claude reading work.md) knows where to pick up."""
    job = _load(params["job_id"])
    if not job:
        raise FileNotFoundError(f"unknown job: {params['job_id']}")
    if job.status != "running":
        # mark abandoned ones runnable again
        if job.status in ("abandoned", "failed"):
            job.status = "running"
            job.updated_at = time.time()
            _save(job)
    log_lines = []
    if _log_path(job.id).exists():
        log_lines = _log_path(job.id).read_text().splitlines()[-30:]
    return {
        "job_id": job.id,
        "current_step": job.current_step,
        "vars": job.vars,
        "elapsed_s": int(time.time() - job.started_at),
        "log_tail": log_lines,
        "next_action": f"continue from step '{job.current_step}'",
    }


async def _append_log(params: dict[str, Any]) -> dict[str, Any]:
    p = _log_path(params["job_id"])
    if not p.exists():
        raise FileNotFoundError(p)
    with p.open("a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {params['line']}\n")
    return {"appended": True}


async def _snapshot(params: dict[str, Any]) -> dict[str, Any]:
    """Capture an arbitrary file/screenshot under the job's snapshots/."""
    import shutil
    job_id = params["job_id"]
    src = Path(params["src"]).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(src)
    name = params.get("name", f"snap_{int(time.time())}_{src.name}")
    dst = _snap_dir(job_id) / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    job = _load(job_id)
    if job:
        job.snapshots.append(str(dst))
        job.updated_at = time.time()
        _save(job)
    return {"snapshot": str(dst)}


def register(bus) -> None:
    bus.register("jobs.create", _create)
    bus.register("jobs.checkpoint", _checkpoint)
    bus.register("jobs.complete", _complete)
    bus.register("jobs.list", _list_jobs)
    bus.register("jobs.get", _get)
    bus.register("jobs.resume", _resume)
    bus.register("jobs.append_log", _append_log)
    bus.register("jobs.snapshot", _snapshot)
