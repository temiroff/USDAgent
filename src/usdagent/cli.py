"""Click-based CLI: usdagent run / validate / info."""

from __future__ import annotations

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """USDAgent — orchestrate USD scenes via natural language."""


@main.command()
@click.argument("prompt")
@click.option("--stage", "-s", default=None, help="Path to .usda stage file")
@click.option(
    "--provider",
    "-p",
    default="anthropic",
    type=click.Choice(["anthropic", "openai", "ollama"]),
    show_default=True,
)
@click.option("--model", "-m", default=None, help="Override model name")
@click.option("--verbose", "-v", is_flag=True, help="Show tool call trace")
def run(prompt: str, stage: str | None, provider: str, model: str | None, verbose: bool) -> None:
    """Run a natural-language USD operation."""
    from usdagent.agent import run as agent_run

    console.print(Panel(f"[bold cyan]{prompt}[/]", title="Prompt"))
    result = agent_run(prompt=prompt, stage_path=stage, provider=provider, model=model)
    console.print(Panel(result, title="[green]Result[/]"))


@main.command()
@click.argument("stage_path")
def validate(stage_path: str) -> None:
    """Validate a USD stage and report issues."""
    from usdagent.tools.stage import open_stage
    from usdagent.tools.validate import validate_stage

    handle = open_stage(stage_path)
    report = validate_stage(handle)

    if report.is_valid:
        console.print("[green]Stage is valid.[/]")
    else:
        console.print(f"[red]Found {report.error_count} error(s).[/]")

    for issue in report.issues:
        color = {"error": "red", "warning": "yellow", "info": "blue"}.get(issue.severity, "white")
        console.print(f"  [{color}]{issue.severity.upper()}[/] {issue.path}: {issue.message}")

    if report.broken_references:
        console.print("\n[red]Broken references:[/]")
        for ref in report.broken_references:
            console.print(f"  {ref}")


@main.command()
@click.argument("stage_path")
def info(stage_path: str) -> None:
    """Print stage metadata."""
    from usdagent.tools.stage import get_stage_metadata, open_stage

    handle = open_stage(stage_path)
    meta = get_stage_metadata(handle)
    console.print(f"Path:           {meta.path}")
    console.print(f"Up axis:        {meta.up_axis}")
    console.print(f"Meters/unit:    {meta.meters_per_unit}")
    console.print(f"Layer count:    {meta.layer_count}")
    console.print(f"Prim count:     {meta.prim_count}")
