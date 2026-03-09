"""Learning OS CLI — entry point for all commands."""

import click
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from learning_os.scaffold import scaffold_workspace, upgrade_workspace

console = Console()


@click.group()
@click.version_option(package_name="learning-os")
def main():
    """Learning OS — AI-native learning workspace for any topic.

    Turns any directory into a structured learning system powered by
    Agent Skills (open standard). Works with Cursor, Claude Code, and
    any compatible AI tool.
    """


@main.command()
@click.argument("directory", default=".", type=click.Path())
@click.option(
    "--with-sample",
    is_flag=True,
    default=False,
    help="Include a sample course as a reference/demo.",
)
@click.option(
    "--tool",
    type=click.Choice(["cursor", "claude", "both"], case_sensitive=False),
    default=None,
    help="Which AI tool to configure for (default: prompt interactively).",
)
def init(directory, with_sample, tool):
    """Scaffold a Learning OS workspace in DIRECTORY (default: current dir).

    Examples:\n
      learning-os init\n
      learning-os init ~/my-learning\n
      learning-os init --with-sample\n
      learning-os init --tool cursor
    """
    console.print(
        Panel.fit(
            "[bold cyan]Learning OS[/bold cyan] [dim]v1.0.0[/dim]\n"
            "AI-native learning workspace scaffold",
            border_style="cyan",
        )
    )
    console.print()

    if tool is None:
        tool = click.prompt(
            "Which AI tool do you primarily use",
            type=click.Choice(["cursor", "claude", "both"], case_sensitive=False),
            default="cursor",
        )

    scaffold_workspace(directory, tool=tool, with_sample=with_sample, console=console)


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True))
def upgrade(directory):
    """Upgrade an existing workspace to the latest Learning OS version.

    Updates skills, hooks, and scripts without touching your courses,
    notes, or progress.

    Examples:\n
      learning-os upgrade\n
      learning-os upgrade ~/my-learning
    """
    console.print(
        Panel.fit(
            "[bold cyan]Learning OS Upgrade[/bold cyan]\n"
            "Updating engine — your content will not be touched",
            border_style="cyan",
        )
    )
    console.print()
    upgrade_workspace(directory, console=console)
