"""Persistent "lessons" memory — how RobloxForge improves over time.

Every review and every piece of real-world feedback is distilled into short,
transferable **lessons** scoped to a pipeline role (e.g. ``design``,
``engineering``, ``growth``, ``global``). Before an agent runs, the lessons for
its role are injected into its system prompt, so each generation is shaped by
everything learned from prior ones.

Lessons are stored as JSONL so they're easy to diff, review, and commit — the
memory file is meant to live in git and grow with the project.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from .config import MEMORY_PATH

# Canonical scopes. "global" lessons apply to every agent; the rest map to an
# agent's ``role``. A genre name (e.g. "simulator") is also a valid scope.
ROLE_SCOPES = ("market", "design", "engineering", "ui", "qa", "marketing", "global")


class Lesson(BaseModel):
    """A single transferable insight learned from a review or real feedback."""

    scope: str = Field(description="Role/genre this applies to, or 'global'.")
    text: str = Field(description="The actionable lesson, phrased as guidance.")
    source: str = Field(default="review", description="review | feedback | manual")
    created: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Memory:
    """Append-only lessons store with role-scoped retrieval."""

    def __init__(self, path: Path = MEMORY_PATH) -> None:
        self.path = Path(path)
        self._lessons: list[Lesson] = []
        self._load()

    def _load(self) -> None:
        self._lessons = []
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                self._lessons.append(Lesson.model_validate_json(line))
            except Exception:  # skip a corrupt line rather than crash a run
                continue

    # ------------------------------------------------------------------ write
    def add(self, scope: str, text: str, *, source: str = "review") -> Lesson:
        lesson = Lesson(scope=scope.strip().lower() or "global", text=text.strip(), source=source)
        self._append(lesson)
        return lesson

    def add_many(self, lessons: list[Lesson]) -> int:
        added = 0
        for lesson in lessons:
            if lesson.text.strip() and not self._is_duplicate(lesson):
                self._append(lesson)
                added += 1
        return added

    def _append(self, lesson: Lesson) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(lesson.model_dump_json() + "\n")
        self._lessons.append(lesson)

    def _is_duplicate(self, lesson: Lesson) -> bool:
        key = (lesson.scope.lower(), lesson.text.strip().lower())
        return any((lesson.scope.lower(), lesson.text.strip().lower()) == key for lesson in self._lessons)

    # ------------------------------------------------------------------- read
    def all(self) -> list[Lesson]:
        return list(self._lessons)

    def for_scopes(self, scopes: list[str], *, limit: int = 12) -> list[Lesson]:
        wanted = {s.lower() for s in scopes}
        matches = [lesson for lesson in self._lessons if lesson.scope.lower() in wanted]
        return matches[-limit:]  # most recent are the most refined

    def context_for(self, role: str, *, genre: str | None = None, limit: int = 12) -> str:
        """Return an injectable block of lessons for ``role`` (+ global + genre)."""
        scopes = [role, "global"]
        if genre:
            scopes.append(genre.lower())
        lessons = self.for_scopes(scopes, limit=limit)
        if not lessons:
            return ""
        bullets = "\n".join(f"- {lesson.text}" for lesson in lessons)
        return (
            "LESSONS LEARNED from past games (reviews + real outcomes). Apply "
            "these — they encode what worked and what failed before:\n" + bullets
        )
