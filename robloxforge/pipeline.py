"""The end-to-end pipeline: brief in, a buildable+launchable game out.

Stages run in order, each consuming the previous stage's typed artifact:

    market research -> game design -> engineering -> UI/UX -> QA -> marketing

The result is written to disk as a Rojo project (opens in Studio) with a
``forge/`` folder holding every artifact. A final self-review distills lessons
into persistent memory so the *next* run is better than this one.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .agents import (
    GameDesignAgent,
    LuauEngineerAgent,
    MarketingAgent,
    MarketResearchAgent,
    QAAgent,
    ReviewerAgent,
    UIUXAgent,
)
from .config import OUTPUT_ROOT
from .llm import LLM
from .memory import Lesson, Memory
from .models import (
    GameConcept,
    GameDesignDocument,
    GeneratedFile,
    LaunchPlan,
    MarketReport,
    QAReport,
    ReviewResult,
)
from .roblox import scaffold_project

Logger = Callable[[str], None]


@dataclass(slots=True)
class RunResult:
    """Everything a pipeline run produced."""

    project_dir: Path
    concept: GameConcept
    market: MarketReport
    gdd: GameDesignDocument
    files: list[GeneratedFile]
    qa: QAReport
    launch: LaunchPlan
    review: ReviewResult | None = None
    lessons_added: int = 0


def _noop(_msg: str) -> None:  # default logger
    pass


def artifacts_blob(
    market: MarketReport, gdd: GameDesignDocument, qa: QAReport, launch: LaunchPlan
) -> str:
    """Compact text bundle of a run's artifacts for the reviewer to read."""
    return (
        f"MARKET REPORT:\n{market.model_dump_json(indent=2)}\n\n"
        f"GAME DESIGN:\n{gdd.model_dump_json(indent=2)}\n\n"
        f"QA REPORT (summary/issues/verdict):\n"
        f"summary: {qa.summary}\nissues: {qa.issues}\nverdict: {qa.verdict}\n\n"
        f"LAUNCH PLAN:\n{launch.model_dump_json(indent=2)}"
    )


class Pipeline:
    """Wires the agents together over a shared LLM client and shared memory."""

    def __init__(
        self,
        llm: LLM | None = None,
        memory: Memory | None = None,
        *,
        log: Logger = _noop,
    ) -> None:
        self.llm = llm or LLM()
        self.memory = memory if memory is not None else Memory()
        self.log = log
        self.market = MarketResearchAgent(self.llm, self.memory)
        self.design = GameDesignAgent(self.llm, self.memory)
        self.engineer = LuauEngineerAgent(self.llm, self.memory)
        self.ui = UIUXAgent(self.llm, self.memory)
        self.qa = QAAgent(self.llm, self.memory)
        self.marketing = MarketingAgent(self.llm, self.memory)
        self.reviewer = ReviewerAgent(self.llm, self.memory)

    def run(
        self,
        brief: str,
        *,
        concept_index: int | None = None,
        dest: Path = OUTPUT_ROOT,
        review: bool = True,
    ) -> RunResult:
        self.log("[1/6] Market research — finding a concept that can grow for free...")
        market = self.market.run(brief)
        concept = self._pick_concept(market, concept_index)
        self.log(f"      -> {concept.title} ({concept.genre})")

        self.log("[2/6] Game design — writing the design document...")
        gdd = self.design.run(concept)

        self.log("[3/6] Engineering — generating server/shared/client Luau...")
        code = self.engineer.run(gdd)
        self.log(f"      -> {len(code)} source files")

        self.log("[4/6] UI/UX — building the interface...")
        ui = self.ui.run(gdd)
        self.log(f"      -> {len(ui)} UI files")

        all_files = code + ui

        self.log("[5/6] QA — reviewing code and writing tests...")
        qa = self.qa.review(all_files)
        tests = self.qa.write_tests(all_files)
        qa.test_files = tests
        all_files += tests
        self.log(f"      -> verdict: {qa.verdict}")

        self.log("[6/6] Marketing — building the free-growth launch plan...")
        launch = self.marketing.run(gdd)

        self.log("Scaffolding Rojo project...")
        project_dir = scaffold_project(gdd.title, gdd.elevator_pitch, all_files, dest)
        self._write_artifacts(project_dir, market, gdd, qa, launch)

        result = RunResult(
            project_dir=project_dir,
            concept=concept,
            market=market,
            gdd=gdd,
            files=all_files,
            qa=qa,
            launch=launch,
        )

        if review:
            self.log("Self-review — learning lessons for next time...")
            try:
                review_result = self.reviewer.run(artifacts_blob(market, gdd, qa, launch))
                added = self.memory.add_many(
                    [Lesson(scope=lesson.scope, text=lesson.text, source="review") for lesson in review_result.lessons]
                )
                result.review = review_result
                result.lessons_added = added
                (project_dir / "forge" / "review.json").write_text(
                    review_result.model_dump_json(indent=2), encoding="utf-8"
                )
                self.log(f"      -> score {review_result.score}/10, {added} new lessons learned")
            except Exception as exc:  # a failed review must not lose the game
                self.log(f"      -> review skipped ({exc})")

        self.log(f"Done -> {project_dir}")
        return result

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _pick_concept(market: MarketReport, index: int | None) -> GameConcept:
        if not market.concepts:
            raise RuntimeError("Market research returned no concepts.")
        if index is not None:
            return market.concepts[index % len(market.concepts)]
        return market.concepts[0]

    @staticmethod
    def _write_artifacts(
        project_dir: Path,
        market: MarketReport,
        gdd: GameDesignDocument,
        qa: QAReport,
        launch: LaunchPlan,
    ) -> None:
        forge = project_dir / "forge"
        forge.mkdir(parents=True, exist_ok=True)
        for name, model in (
            ("market_report", market),
            ("game_design", gdd),
            ("qa_report", qa),
            ("launch_plan", launch),
        ):
            (forge / f"{name}.json").write_text(model.model_dump_json(indent=2), encoding="utf-8")
        (forge / "LAUNCH.md").write_text(_launch_markdown(launch), encoding="utf-8")


def _launch_markdown(p: LaunchPlan) -> str:
    """Render the launch plan as a human-friendly checklist."""
    thumbs = "\n".join(f"- {t}" for t in p.thumbnail_briefs)
    hooks = "\n".join(f"- {h}" for h in p.tiktok_hooks)
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(p.launch_checklist, 1))
    return (
        f"# Launch plan — {p.game_title}\n\n"
        f"## Store description\n\n{p.game_description}\n\n"
        f"## Icon brief\n\n{p.icon_brief}\n\n"
        f"## Thumbnail briefs\n\n{thumbs}\n\n"
        f"## Short-form video hooks (free growth)\n\n{hooks}\n\n"
        f"## Launch checklist\n\n{steps}\n\n"
        f"## Update cadence\n\n{p.update_cadence}\n"
    )


__all__ = ["Pipeline", "RunResult", "artifacts_blob"]
