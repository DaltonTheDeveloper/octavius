"""``forge`` — the RobloxForge command-line interface."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import (
    DEFAULT_BACKEND,
    DEFAULT_EFFORT,
    DEFAULT_MODEL,
    MEMORY_PATH,
    OUTPUT_ROOT,
    OpenCloudConfig,
)
from .llm import LLM, LLMError

app = typer.Typer(
    add_completion=False,
    help="AI pipeline that automates Roblox game dev (research -> design -> "
    "code -> UI -> QA -> free user acquisition), running on Claude Code and "
    "improving itself from reviews and real feedback.",
)
console = Console()


def _llm(backend: str, model: str, effort: str) -> LLM:
    try:
        return LLM(backend=backend, model=model, effort=effort)
    except LLMError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


@app.command()
def new(
    brief: str = typer.Argument(
        ..., help="Your idea, or a vague direction (e.g. 'a chill pet collecting game')."
    ),
    concept_index: Optional[int] = typer.Option(
        None, "--concept", help="Pick a specific ranked concept instead of the top one."
    ),
    out: Path = typer.Option(OUTPUT_ROOT, "--out", help="Output directory."),
    backend: str = typer.Option(DEFAULT_BACKEND, "--backend", help="claude-code | api."),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Model id or CLI alias."),
    effort: str = typer.Option(DEFAULT_EFFORT, "--effort", help="low|medium|high|xhigh|max."),
    no_review: bool = typer.Option(False, "--no-review", help="Skip the self-review/learning step."),
) -> None:
    """Run the full pipeline and write a ready-to-open Rojo project."""
    from .memory import Memory
    from .pipeline import Pipeline

    llm = _llm(backend, model, effort)
    pipeline = Pipeline(llm, Memory(), log=lambda m: console.print(f"[dim]{m}[/dim]"))
    try:
        result = pipeline.run(
            brief, concept_index=concept_index, dest=out, review=not no_review
        )
    except (LLMError, RuntimeError) as exc:
        console.print(f"[red]Pipeline failed: {exc}[/red]")
        raise typer.Exit(1) from exc

    review_line = ""
    if result.review:
        review_line = (
            f"[bold]Review[/bold]  {result.review.score}/10 "
            f"({result.lessons_added} lessons learned)\n"
        )
    body = (
        f"[bold]{result.gdd.title}[/bold]\n{result.gdd.elevator_pitch}\n\n"
        f"[bold]Genre[/bold]   {result.concept.genre}\n"
        f"[bold]Files[/bold]   {len(result.files)} source files\n"
        f"[bold]QA[/bold]      {result.qa.verdict}\n"
        f"{review_line}\n"
        f"[bold]Project[/bold] {result.project_dir}\n"
        f"[dim]Open in Studio: cd {result.project_dir} && rokit install && rojo serve[/dim]\n"
        f"[dim]Launch plan:    {result.project_dir / 'forge' / 'LAUNCH.md'}[/dim]"
    )
    console.print(Panel(body, title="🎮 Game generated", border_style="green"))


@app.command()
def research(
    brief: str = typer.Argument(..., help="Idea or direction to research."),
    backend: str = typer.Option(DEFAULT_BACKEND, "--backend"),
    model: str = typer.Option(DEFAULT_MODEL, "--model"),
    effort: str = typer.Option(DEFAULT_EFFORT, "--effort"),
) -> None:
    """Only run market research and print ranked, buildable concepts."""
    from .agents import MarketResearchAgent
    from .memory import Memory

    llm = _llm(backend, model, effort)
    console.print("[dim]Researching the Roblox market...[/dim]")
    try:
        report = MarketResearchAgent(llm, Memory()).run(brief)
    except LLMError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    table = Table(title="Ranked concepts", show_lines=True)
    table.add_column("#", style="bold")
    table.add_column("Title")
    table.add_column("Genre")
    table.add_column("Hook")
    for i, c in enumerate(report.concepts):
        table.add_row(str(i), c.title, c.genre, c.hook)
    console.print(table)
    console.print(Panel(report.recommendation, title="Recommendation", border_style="cyan"))


@app.command()
def review(
    project_dir: Path = typer.Argument(..., help="A generated project directory."),
    backend: str = typer.Option(DEFAULT_BACKEND, "--backend"),
    model: str = typer.Option(DEFAULT_MODEL, "--model"),
    effort: str = typer.Option(DEFAULT_EFFORT, "--effort"),
) -> None:
    """Critique a generated game and learn lessons for future runs."""
    from .memory import Memory
    from .reviewing import review_project

    llm = _llm(backend, model, effort)
    memory = Memory()
    console.print("[dim]Reviewing project and learning lessons...[/dim]")
    try:
        result = review_project(project_dir, llm=llm, memory=memory)
    except (LLMError, FileNotFoundError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_review(result)


@app.command()
def feedback(
    project_dir: Path = typer.Argument(..., help="A generated project directory."),
    ccu: Optional[int] = typer.Option(None, "--ccu", help="Peak concurrent users observed."),
    d1: Optional[float] = typer.Option(None, "--d1", help="D1 retention %."),
    d7: Optional[float] = typer.Option(None, "--d7", help="D7 retention %."),
    note: Optional[str] = typer.Option(None, "--note", help="Free-text player feedback."),
    backend: str = typer.Option(DEFAULT_BACKEND, "--backend"),
    model: str = typer.Option(DEFAULT_MODEL, "--model"),
    effort: str = typer.Option(DEFAULT_EFFORT, "--effort"),
) -> None:
    """Record real-world outcomes for a game and learn from them."""
    from .memory import Memory
    from .reviewing import format_feedback, review_project

    fb = format_feedback(ccu=ccu, d1=d1, d7=d7, note=note)
    llm = _llm(backend, model, effort)
    memory = Memory()
    console.print("[dim]Folding real-world feedback into memory...[/dim]")
    try:
        result = review_project(project_dir, llm=llm, memory=memory, feedback=fb)
    except (LLMError, FileNotFoundError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    _print_review(result)


@app.command()
def lessons(
    scope: Optional[str] = typer.Option(None, "--scope", help="Filter by role/genre/global."),
) -> None:
    """List the lessons the system has learned so far."""
    from .memory import Memory

    mem = Memory()
    items = mem.for_scopes([scope], limit=1000) if scope else mem.all()
    if not items:
        console.print("[yellow]No lessons learned yet. Run `forge new` or `forge review`.[/yellow]")
        return
    table = Table(title=f"Lessons learned ({len(items)})", show_lines=True)
    table.add_column("Scope", style="bold")
    table.add_column("Source")
    table.add_column("Lesson")
    for lesson in items:
        table.add_row(lesson.scope, lesson.source, lesson.text)
    console.print(table)


@app.command()
def info() -> None:
    """Show configuration and whether the toolchain/keys are set up."""
    from .memory import Memory

    cfg = OpenCloudConfig()
    n_lessons = len(Memory().all())
    table = Table(title=f"RobloxForge v{__version__}")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("Backend", DEFAULT_BACKEND)
    table.add_row("Model", DEFAULT_MODEL)
    table.add_row("Effort", DEFAULT_EFFORT)
    table.add_row("Output dir", str(OUTPUT_ROOT))
    table.add_row("Lessons learned", f"{n_lessons} ({MEMORY_PATH})")
    cc = "found" if shutil.which("claude") else "[red]not installed[/red]"
    table.add_row("claude CLI (default backend)", cc)
    table.add_row("ANTHROPIC_API_KEY (api backend)", "set" if _env("ANTHROPIC_API_KEY") else "not set")
    table.add_row("Open Cloud key", "set" if cfg.configured else "[yellow]not set (optional)[/yellow]")
    table.add_row("rojo", "found" if shutil.which("rojo") else "[yellow]not installed[/yellow]")
    table.add_row("rokit", "found" if shutil.which("rokit") else "[yellow]not installed[/yellow]")
    console.print(table)


@app.command()
def publish(
    place_file: Path = typer.Argument(..., help="A built .rbxl / .rbxlx to publish."),
    draft: bool = typer.Option(False, "--draft", help="Save a draft instead of releasing."),
) -> None:
    """Publish a built place to a live experience via Open Cloud."""
    from .roblox import OpenCloudClient
    from .roblox.opencloud import OpenCloudError

    cfg = OpenCloudConfig()
    try:
        with OpenCloudClient(cfg) as client:
            result = client.publish_place(place_file, published=not draft)
    except OpenCloudError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print(Panel(str(result), title="Published", border_style="green"))


def _print_review(result) -> None:
    strengths = "\n".join(f"[green]+[/green] {s}" for s in result.strengths)
    weaknesses = "\n".join(f"[red]-[/red] {w}" for w in result.weaknesses)
    lessons = "\n".join(f"[cyan]→[/cyan] ({lesson.scope}) {lesson.text}" for lesson in result.lessons)
    body = (
        f"[bold]Hit-potential: {result.score}/10[/bold]\n\n"
        f"[bold]Strengths[/bold]\n{strengths}\n\n"
        f"[bold]Weaknesses[/bold]\n{weaknesses}\n\n"
        f"[bold]Lessons learned (saved to memory)[/bold]\n{lessons}"
    )
    console.print(Panel(body, title="Review", border_style="magenta"))


def _env(key: str) -> bool:
    import os

    return bool(os.environ.get(key))


if __name__ == "__main__":  # pragma: no cover
    app()
