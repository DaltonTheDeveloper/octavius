"""Offline tests for the lessons memory (self-improvement store)."""

from __future__ import annotations

from robloxforge.memory import Lesson, Memory


def test_add_and_scope_retrieval(tmp_path):
    mem = Memory(tmp_path / "lessons.jsonl")
    mem.add("design", "Get the core loop playable in under 10 seconds.")
    mem.add("engineering", "Validate every remote argument server-side.")
    mem.add("global", "Ship a visible update every 1-2 weeks.")

    design = mem.for_scopes(["design", "global"])
    texts = {lesson.text for lesson in design}
    assert "Get the core loop playable in under 10 seconds." in texts
    assert "Ship a visible update every 1-2 weeks." in texts
    assert all(lesson.scope != "engineering" for lesson in design)


def test_persistence_roundtrip(tmp_path):
    path = tmp_path / "lessons.jsonl"
    Memory(path).add("qa", "Always BindToClose to save on shutdown.")
    reloaded = Memory(path)
    assert any(lesson.text == "Always BindToClose to save on shutdown." for lesson in reloaded.all())


def test_dedup_on_add_many(tmp_path):
    mem = Memory(tmp_path / "lessons.jsonl")
    lessons = [
        Lesson(scope="design", text="Same lesson."),
        Lesson(scope="design", text="Same lesson."),
        Lesson(scope="design", text="Different lesson."),
    ]
    added = mem.add_many(lessons)
    assert added == 2


def test_context_block_mentions_lessons(tmp_path):
    mem = Memory(tmp_path / "lessons.jsonl")
    mem.add("marketing", "Front-load keywords in the first 100 chars of the description.")
    block = mem.context_for("marketing")
    assert "LESSONS LEARNED" in block
    assert "Front-load keywords" in block
    assert mem.context_for("design") == ""  # no lessons for this role yet
