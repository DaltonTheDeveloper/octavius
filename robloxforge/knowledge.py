"""Loads the bundled Roblox knowledge base as grounding context for agents.

The ``docs/`` directory is the distilled result of researching how Roblox games
are actually built, shipped, and grown. Feeding the relevant docs into each agent
keeps generated code and strategy aligned with real platform practice instead of
the model's priors.
"""

from __future__ import annotations

from functools import lru_cache

from .config import DOCS_ROOT

# Maps a knowledge "topic" to the doc files most relevant to it. Agents request a
# topic; the loader concatenates the matching docs into a single context block.
TOPICS: dict[str, list[str]] = {
    "market": ["05-market-and-monetization.md", "06-discovery-algorithm.md"],
    "growth": ["07-user-acquisition.md", "08-thumbnails-and-launch.md", "06-discovery-algorithm.md"],
    "design": ["04-game-systems.md", "05-market-and-monetization.md", "06-discovery-algorithm.md"],
    "engineering": ["01-luau-and-studio.md", "02-tooling-rojo-wally.md", "04-game-systems.md"],
    "qa": ["01-luau-and-studio.md", "04-game-systems.md", "02-tooling-rojo-wally.md"],
    "opencloud": ["03-open-cloud-api.md"],
}


@lru_cache(maxsize=None)
def _read(name: str) -> str:
    path = DOCS_ROOT / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def context_for(topic: str) -> str:
    """Return a concatenated knowledge block for ``topic`` (empty if unknown)."""
    parts: list[str] = []
    for name in TOPICS.get(topic, []):
        body = _read(name)
        if body:
            parts.append(f"=== {name} ===\n{body}")
    if not parts:
        return ""
    return (
        "Use the following Roblox knowledge base as authoritative grounding. "
        "Prefer it over your priors where they conflict.\n\n" + "\n\n".join(parts)
    )
