"""Typed artifacts that flow between pipeline stages.

Keeping these as Pydantic models (rather than loose dicts) means each stage has a
clear contract, the CLI can render results nicely, and a run can be serialised to
JSON and resumed or inspected later.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class GameConcept(BaseModel):
    """A single candidate game idea, grounded in current Roblox market trends."""

    title: str = Field(description="Catchy, search-friendly working title.")
    genre: str = Field(description="Primary genre, e.g. Simulator, Tycoon, Obby, Horror.")
    hook: str = Field(description="One-sentence reason a player clicks and stays.")
    target_audience: str = Field(description="Who this is for (age band + interests).")
    core_loop: str = Field(description="The 30-second repeatable gameplay loop.")
    why_now: str = Field(description="Trend / market timing rationale.")
    differentiation: str = Field(description="How it stands out from saturated competitors.")
    monetization: list[str] = Field(description="Game passes / dev products / mechanics.")
    virality: list[str] = Field(description="Built-in free-growth hooks (social, shareable).")
    estimated_scope: str = Field(description="MVP build effort: small / medium / large.")


class MarketReport(BaseModel):
    """Output of the market-research stage."""

    trends: list[str] = Field(description="What is hot on Roblox right now and why.")
    opportunities: list[str] = Field(description="Under-served niches with demand.")
    concepts: list[GameConcept] = Field(description="Ranked candidate concepts.")
    recommendation: str = Field(description="Which concept to build and why.")


class GameDesignDocument(BaseModel):
    """Structured GDD that drives the engineering and UI stages."""

    title: str
    elevator_pitch: str
    core_loop: str
    progression: str = Field(description="How players advance over a session and over weeks.")
    systems: list[str] = Field(description="Named gameplay systems to implement.")
    economy: str = Field(description="Currencies, sources, sinks, and balance notes.")
    monetization: list[str] = Field(description="Concrete game passes and dev products.")
    retention_mechanics: list[str] = Field(description="D1/D7 hooks: dailies, streaks, events.")
    ui_screens: list[str] = Field(description="Screens/HUD the UI stage must build.")
    mvp_scope: list[str] = Field(description="The smallest shippable feature set.")
    content_roadmap: list[str] = Field(description="Post-launch update beats for live-ops.")


class GeneratedFile(BaseModel):
    """A single source file the engineering/UI stages emit into the Rojo tree."""

    path: str = Field(description="Path relative to the project's src/ root.")
    purpose: str = Field(description="One line describing what this file does.")
    content: str = Field(description="Full Luau source.")


class QAReport(BaseModel):
    """Output of the QA stage."""

    summary: str
    issues: list[str] = Field(description="Bugs, exploits, and design risks found.")
    test_files: list[GeneratedFile] = Field(description="TestEZ specs to add to the project.")
    verdict: str = Field(description="ship / fix-first, with the rationale.")


class ReviewLesson(BaseModel):
    """A transferable lesson the reviewer wants future runs to remember."""

    scope: str = Field(
        description="Which role this improves: market, design, engineering, ui, "
        "qa, marketing, or global."
    )
    text: str = Field(description="Actionable guidance, phrased imperatively.")


class ReviewResult(BaseModel):
    """A critique of a generated game plus lessons to fold back into memory."""

    score: int = Field(description="Overall hit-potential score, 1-10.")
    strengths: list[str] = Field(description="What this game does well.")
    weaknesses: list[str] = Field(description="Concrete risks to retention/growth/quality.")
    lessons: list[ReviewLesson] = Field(
        description="Transferable lessons to improve FUTURE generations."
    )


class LaunchPlan(BaseModel):
    """Output of the marketing / user-acquisition stage."""

    game_title: str = Field(description="Final store-facing title (SEO-aware).")
    game_description: str = Field(description="Store description with keywords.")
    icon_brief: str = Field(description="Art direction for a high-CTR game icon.")
    thumbnail_briefs: list[str] = Field(description="Briefs for high-CTR thumbnails.")
    tiktok_hooks: list[str] = Field(description="Short-form video ideas to go viral for free.")
    launch_checklist: list[str] = Field(description="Ordered free-growth launch steps.")
    update_cadence: str = Field(description="The live-ops update schedule to please the algorithm.")
