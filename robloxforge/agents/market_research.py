"""Market-research agent: turns a rough idea (or nothing) into ranked concepts."""

from __future__ import annotations

from ..models import MarketReport
from .base import Agent

_SYSTEM = """\
You are a Roblox market analyst and game producer who has shipped multiple \
front-page hits. You think in terms of CCU (concurrent users), D1/D7 retention, \
average session length, and what the Discover algorithm rewards. You know which \
genres are saturated and which niches have demand without supply.

Your job: propose game concepts that a small team can build fast, that have a \
real shot at organic growth (no ad budget), and that monetize cleanly. Be \
concrete and ruthless about what actually trends on Roblox today. Favor strong \
core loops, built-in social/viral hooks, and low-but-fair monetization that does \
not gate fun.\
"""


class MarketResearchAgent(Agent):
    name = "Market Research"
    topic = "market"
    system_prompt = _SYSTEM

    def run(self, brief: str) -> MarketReport:
        prompt = (
            "Produce a market report and at least 4 ranked, buildable game "
            "concepts for the following brief. If the brief is vague, choose the "
            "most promising directions yourself.\n\n"
            f"BRIEF:\n{brief}\n\n"
            "Ground every concept in current Roblox trends and the discovery "
            "algorithm's incentives. Rank concepts by (organic-growth potential "
            "x buildability), and name your single recommendation."
        )
        return self.ask_model(prompt, MarketReport, max_tokens=12_000)
