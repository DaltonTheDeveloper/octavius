"""Central configuration for RobloxForge.

Everything tunable lives here so the rest of the codebase can stay declarative.
Values can be overridden with environment variables (prefixed ``FORGE_``) so the
pipeline is easy to drive from CI without editing code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# The model the whole pipeline runs on. Opus 4.8 is the most capable model for
# the long-horizon, multi-step reasoning this pipeline does (design -> code ->
# review). Override with FORGE_MODEL if you want to trade cost for capability.
DEFAULT_MODEL = os.environ.get("FORGE_MODEL", "claude-opus-4-8")

# Per-agent effort. "high" is the sweet spot for code/design quality; drop to
# "medium" to cut cost on routine generation. See robloxforge/llm.py.
DEFAULT_EFFORT = os.environ.get("FORGE_EFFORT", "high")

# Where generated games are written. Each run gets its own subdirectory.
OUTPUT_ROOT = Path(os.environ.get("FORGE_OUTPUT", "games")).resolve()

# Root of the bundled Roblox knowledge base (docs/). Agents read these as
# grounding context so generated code/strategy reflects real Roblox practice.
REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = REPO_ROOT / "docs"


@dataclass(slots=True)
class OpenCloudConfig:
    """Credentials for Roblox Open Cloud (programmatic publish/datastore/assets).

    All optional — the pipeline produces a full project without them. Supply
    them only when you want RobloxForge to publish or manage a live experience.
    """

    api_key: str | None = field(default_factory=lambda: os.environ.get("ROBLOX_API_KEY"))
    universe_id: str | None = field(default_factory=lambda: os.environ.get("ROBLOX_UNIVERSE_ID"))
    place_id: str | None = field(default_factory=lambda: os.environ.get("ROBLOX_PLACE_ID"))
    creator_id: str | None = field(default_factory=lambda: os.environ.get("ROBLOX_CREATOR_ID"))
    # "User" or "Group" — required for asset uploads.
    creator_type: str = field(default_factory=lambda: os.environ.get("ROBLOX_CREATOR_TYPE", "User"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key)
