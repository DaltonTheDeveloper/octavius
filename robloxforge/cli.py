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
from .config import DEFAULT_EFFORT, DEFAULT_MODEL, OUTPUT_ROOT, OpenCloudConfig
from .llm import LLM, LLMError

app = typer.Typer(
    add_completion=False,
    help="AI pipeline that automates Roblox game dev: research -> design -> "
    "code -> UI -> QA -> free user acquisition.",
)
console = Console()


def _llm(model: str, effort: str) -> LLM:
    try:
        return LLM(model=model, effort=effort)
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
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Claude model id."),
    effort: str = typer.Option(DEFAULT_EFFORT, "--effort", help="low|medium|high|max."),
) -> None:
    """Run the full pipeline and write a ready-to-open Rojo project."""
    from .pipeline import Pipeline

    llm = _llm(model, effort)
    pipeline = Pipeline(llm, log=lambda m: console.print(f"[dim]{m}[/dim]"))
    try:
        result = pipeline.run(brief, concept_index=concept_index, dest=out)
    except (LLMError, RuntimeError) as exc:
        console.print(f"[red]Pipeline failed: {exc}[/red]")
        raise typer.Exit(1) from exc

    body = (
        f"[bold]{result.gdd.title}[/bold]\n{result.gdd.elevator_pitch}\n\n"
        f"[bold]Genre[/bold]   {result.concept.genre}\n"
        f"[bold]Files[/bold]   {len(result.files)} source files\n"
        f"[bold]QA[/bold]      {result.qa.verdict}\n\n"
        f"[bold]Project[/bold] {result.project_dir}\n"
        f"[dim]Open in Studio: cd {result.project_dir} && rokit install && rojo serve[/dim]\n"
        f"[dim]Launch plan:    {result.project_dir / 'forge' / 'LAUNCH.md'}[/dim]"
    )
    console.print(Panel(body, title="🎮 Game generated", border_style="green"))


@app.command()
def research(
    brief: str = typer.Argument(..., help="Idea or direction to research."),
    model: str = typer.Option(DEFAULT_MODEL, "--model"),
    effort: str = typer.Option(DEFAULT_EFFORT, "--effort"),
) -> None:
    """Only run market research and print ranked, buildable concepts."""
    from .agents import MarketResearchAgent

    llm = _llm(model, effort)
    console.print("[dim]Researching the Roblox market...[/dim]")
    try:
        report = MarketResearchAgent(llm).run(brief)
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


@app.command()
def info() -> None:
    """Show configuration and whether the toolchain/keys are set up."""
    cfg = OpenCloudConfig()
    table = Table(title=f"RobloxForge v{__version__}")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("Model", DEFAULT_MODEL)
    table.add_row("Effort", DEFAULT_EFFORT)
    table.add_row("Output dir", str(OUTPUT_ROOT))
    table.add_row("ANTHROPIC_API_KEY", "set" if _env("ANTHROPIC_API_KEY") else "[red]missing[/red]")
    table.add_row("Open Cloud key", "set" if cfg.configured else "[yellow]not set (optional)[/yellow]")
    table.add_row("rojo", "found" if shutil.which("rojo") else "[yellow]not installed[/yellow]")
    table.add_row("rokit", "found" if shutil.which("rokit") else "[yellow]not installed[/yellow]")
    console.print(table)


def _env(key: str) -> bool:
    import os

    return bool(os.environ.get(key))


if __name__ == "__main__":  # pragma: no cover
    app()
