"""Review an existing project and fold what we learn back into memory.

Powers ``forge review`` (critique a generated game) and ``forge feedback``
(record real outcomes — CCU, retention, player notes — and learn from them). Both
distill lessons into the persistent :class:`~robloxforge.memory.Memory` so future
runs improve.
"""

from __future__ import annotations

import json
from pathlib import Path

from .agents import ReviewerAgent
from .llm import LLM
from .memory import Lesson, Memory
from .models import ReviewResult

_ARTIFACT_FILES = ("market_report", "game_design", "qa_report", "launch_plan")


def load_artifacts_blob(project_dir: Path) -> str:
    """Read a project's ``forge/*.json`` artifacts into a single text blob."""
    forge = Path(project_dir) / "forge"
    if not forge.exists():
        raise FileNotFoundError(
            f"No forge/ artifacts found in {project_dir}. Is this a RobloxForge project?"
        )
    parts: list[str] = []
    for name in _ARTIFACT_FILES:
        path = forge / f"{name}.json"
        if path.exists():
            parts.append(f"=== {name} ===\n{path.read_text(encoding='utf-8')}")
    if not parts:
        raise FileNotFoundError(f"No recognised artifacts in {forge}.")
    return "\n\n".join(parts)


def review_project(
    project_dir: Path,
    *,
    llm: LLM,
    memory: Memory,
    feedback: str | None = None,
) -> ReviewResult:
    """Critique a project (optionally with real feedback) and store its lessons."""
    blob = load_artifacts_blob(project_dir)
    reviewer = ReviewerAgent(llm, memory)
    result = reviewer.run(blob, feedback=feedback)

    source = "feedback" if feedback else "review"
    memory.add_many(
        [Lesson(scope=lesson.scope, text=lesson.text, source=source) for lesson in result.lessons]
    )

    out = Path(project_dir) / "forge" / ("feedback_review.json" if feedback else "review.json")
    out.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result


def format_feedback(
    *,
    ccu: int | None = None,
    d1: float | None = None,
    d7: float | None = None,
    note: str | None = None,
) -> str:
    """Turn structured real-world metrics into a feedback string for the reviewer."""
    lines: list[str] = []
    if ccu is not None:
        lines.append(f"Peak concurrent users (CCU): {ccu}")
    if d1 is not None:
        lines.append(f"D1 retention: {d1}%")
    if d7 is not None:
        lines.append(f"D7 retention: {d7}%")
    if note:
        lines.append(f"Notes / player feedback: {note}")
    return "\n".join(lines) or json.dumps({"note": "no metrics provided"})
