"""Reviewer agent: critiques a generated game and extracts lessons to learn from.

This is the engine of self-improvement. It looks at a finished run (and optional
real-world metrics) the way a skeptical senior producer would, scores its
hit-potential, and — most importantly — emits **transferable lessons** scoped to
each pipeline role. Those lessons are written to memory and injected into future
runs, so the system gets better the more it ships and the more feedback it gets.
"""

from __future__ import annotations

from ..models import ReviewResult
from .base import Agent

_SYSTEM = """\
You are a brutally honest senior Roblox producer running a post-mortem. You have
shipped front-page hits and killed projects that wouldn't retain. You judge a
game by what actually drives success on Roblox: a fast non-bouncing first
session, per-user retention (D1/D2-7/D8-28), intentional co-play, fair
non-blocking monetization, and free organic growth — NOT raw CCU or clickbait.

You are given the artifacts of a generated game (market report, design doc, QA
report, launch plan) and sometimes REAL outcomes (CCU, retention, player notes).
Critique it honestly, score its hit-potential 1-10, and then extract concrete,
TRANSFERABLE lessons that would make the NEXT generated game better. Each lesson
is scoped to the role it should change (market, design, engineering, ui, qa,
marketing, or global) and phrased as imperative guidance a future agent can act
on (e.g. "design: get the core loop playable within 10 seconds; cut intro
cutscenes"). Prefer a few sharp, generalizable lessons over many vague ones. Do
not restate lessons that are obvious or already standard practice.\
"""


class ReviewerAgent(Agent):
    name = "Reviewer"
    role = "global"
    topic = "growth"
    system_prompt = _SYSTEM

    def run(self, artifacts: str, *, feedback: str | None = None) -> ReviewResult:
        fb = f"\n\nREAL-WORLD OUTCOMES / FEEDBACK:\n{feedback}" if feedback else ""
        prompt = (
            "Review this generated Roblox game. Score its hit-potential, list "
            "strengths and weaknesses, and extract transferable lessons for "
            "future generations.\n\n"
            f"GAME ARTIFACTS:\n{artifacts}{fb}"
        )
        return self.ask_model(prompt, ReviewResult, max_tokens=10_000)
