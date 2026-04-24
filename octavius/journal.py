"""Append-only action journal with inverse operations for undo."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .config import JOURNAL_PATH


@dataclass
class JournalEntry:
    id: str
    timestamp: float
    kind: str              # e.g. "fs.move", "fs.write", "shell.run"
    forward: dict[str, Any]
    inverse: dict[str, Any] | None  # None = not reversible
    status: str = "committed"       # committed | undone | failed


def _append(entry: JournalEntry) -> None:
    with JOURNAL_PATH.open("a") as f:
        f.write(json.dumps(asdict(entry)) + "\n")


def _read_all() -> list[JournalEntry]:
    if not JOURNAL_PATH.exists():
        return []
    out = []
    with JOURNAL_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(JournalEntry(**json.loads(line)))
    return out


def _rewrite_all(entries: list[JournalEntry]) -> None:
    tmp = JOURNAL_PATH.with_suffix(".tmp")
    with tmp.open("w") as f:
        for e in entries:
            f.write(json.dumps(asdict(e)) + "\n")
    tmp.replace(JOURNAL_PATH)


def record(kind: str, forward: dict, inverse: dict | None) -> JournalEntry:
    entry = JournalEntry(
        id=uuid.uuid4().hex[:12],
        timestamp=time.time(),
        kind=kind,
        forward=forward,
        inverse=inverse,
    )
    _append(entry)
    return entry


def list_recent(limit: int = 20) -> list[dict]:
    return [asdict(e) for e in _read_all()[-limit:]]


def _apply_inverse(entry: JournalEntry) -> None:
    """Execute the inverse op for a journal entry."""
    if entry.inverse is None:
        raise RuntimeError(f"Entry {entry.id} ({entry.kind}) has no inverse — not reversible.")
    op = entry.inverse
    kind = op["op"]
    if kind == "fs.move":
        src = Path(op["src"])
        dst = Path(op["dst"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
    elif kind == "fs.restore":
        backup = Path(op["backup"])
        dst = Path(op["dst"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(backup), str(dst))
    elif kind == "fs.write":
        # inverse-write: previous content was captured in op["content"]
        Path(op["path"]).write_text(op["content"])
    elif kind == "fs.delete":
        p = Path(op["path"])
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    elif kind == "noop":
        pass
    else:
        raise RuntimeError(f"Unknown inverse op: {kind}")


def undo(count: int = 1) -> list[dict]:
    entries = _read_all()
    reversible = [e for e in entries if e.status == "committed"]
    target = reversible[-count:] if count <= len(reversible) else reversible
    undone: list[dict] = []
    for entry in reversed(target):
        try:
            _apply_inverse(entry)
            entry.status = "undone"
            undone.append(asdict(entry))
        except Exception as exc:  # noqa: BLE001
            entry.status = "failed"
            undone.append({**asdict(entry), "error": str(exc)})
            break
    # persist updated statuses
    by_id = {e.id: e for e in entries}
    for u in undone:
        by_id[u["id"]].status = u.get("status", "undone")
    _rewrite_all(list(by_id.values()))
    return undone
