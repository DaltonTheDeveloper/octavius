"""Marketing / user-acquisition agent: free-growth launch plan + store assets."""

from __future__ import annotations

from ..models import GameDesignDocument, LaunchPlan
from .base import Agent

_SYSTEM = """\
You are a Roblox growth marketer who has taken games from 0 to the front page \
with zero ad spend. You know the discovery algorithm rewards per-user retention \
and co-play (not raw CCU), that ad-acquired users don't count toward ranking \
signals, and that short-form video (TikTok / YouTube Shorts / Roblox Moments) is \
the dominant free channel. You write high-CTR titles and icons, you design \
in-game viral loops (referral system, play-with-friends rewards), and you plan a \
relentless update cadence because "Recently Updated" and return-rate windows \
(D1, D2-7, D8-28) drive distribution.

You optimize the store listing for search: keyword-rich title (<=50 chars), \
keywords front-loaded in the first ~100 chars of the description, no \
giveaway-baiting (it is penalized). Be specific and actionable.\
"""


class MarketingAgent(Agent):
    name = "Marketing"
    role = "marketing"
    topic = "growth"
    system_prompt = _SYSTEM

    def run(self, gdd: GameDesignDocument) -> LaunchPlan:
        prompt = (
            "Create a free user-acquisition and launch plan for this game: an "
            "SEO-aware store title and description, an art brief for a high-CTR "
            "icon, several thumbnail briefs that show players interacting, "
            "short-form video hooks designed to go viral, an ordered launch "
            "checklist of free-growth steps (referral system, Discord, "
            "play-with-friends, TikTok cadence), and the post-launch update "
            "cadence that keeps the algorithm happy.\n\n"
            f"GAME DESIGN DOCUMENT:\n{gdd.model_dump_json(indent=2)}"
        )
        return self.ask_model(prompt, LaunchPlan, max_tokens=10_000)
