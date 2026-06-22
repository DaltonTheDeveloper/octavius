"""Game-design agent: expands a chosen concept into an implementable GDD."""

from __future__ import annotations

from ..models import GameConcept, GameDesignDocument
from .base import Agent

_SYSTEM = """\
You are a senior Roblox game designer. You translate a concept into a tight, \
implementable design document for a small team building an MVP that can ship in \
days, not months. You design for retention first (D1/D7 hooks, daily rewards, \
progression, social proof) because the Discover algorithm rewards engagement. \
You specify a clean economy with clear sources and sinks, and fair monetization \
that accelerates rather than gates. Keep MVP scope brutally small; push \
everything else to the content roadmap.\
"""


class GameDesignAgent(Agent):
    name = "Game Design"
    topic = "design"
    system_prompt = _SYSTEM

    def run(self, concept: GameConcept) -> GameDesignDocument:
        prompt = (
            "Turn this concept into a structured Game Design Document. Be specific "
            "enough that an engineer can implement each named system without "
            "guessing. Keep mvp_scope to the smallest set that is fun and "
            "retentive.\n\n"
            f"CONCEPT:\n{concept.model_dump_json(indent=2)}"
        )
        return self.ask_model(prompt, GameDesignDocument, max_tokens=12_000)
