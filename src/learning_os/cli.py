"""Learning OS CLI — entry point for all commands."""

import click
from rich.console import Console
from rich.panel import Panel

from learning_os import __version__
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
            f"[bold cyan]Learning OS[/bold cyan] [dim]v{__version__}[/dim]\n"
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


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True))
def validate(directory):
    """Validate workspace structure and all COURSE.yaml files.

    Checks that required directories exist, all COURSE.yaml files are
    well-formed, referenced content files are present, and progress
    tracking fields are consistent.

    Examples:\n
      learning-os validate\n
      learning-os validate ~/my-learning
    """
    from learning_os.validate import validate_workspace

    errors, warnings = validate_workspace(directory)

    if warnings:
        for w in warnings:
            console.print(f"  [yellow]![/yellow]  {w}")
    if errors:
        for e in errors:
            console.print(f"  [red]x[/red]  {e}")
        console.print()
        console.print(
            f"[red]Validation failed:[/red] {len(errors)} error(s), "
            f"{len(warnings)} warning(s)"
        )
        raise SystemExit(1)
    else:
        if warnings:
            console.print()
        console.print(
            f"[bold green]Validation passed[/bold green] "
            f"({len(warnings)} warning(s))"
        )


@main.command("list")
@click.argument("directory", default=".", type=click.Path(exists=True))
def list_cmd(directory):
    """List all courses and show learning progress.

    Reads courses/ and .learning-progress to display a table of all
    courses with their completion status.

    Examples:\n
      learning-os list\n
      learning-os list ~/my-learning
    """
    from learning_os.status import list_courses

    list_courses(directory, console)


@main.command("export")
@click.argument("course_id")
@click.option(
    "--dir",
    "directory",
    default=".",
    type=click.Path(exists=True),
    help="Workspace directory (default: current).",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (default: <course-id>.zip in current directory).",
)
def export_cmd(course_id, directory, output):
    """Export a course as a shareable .zip file.

    Examples:\n
      learning-os export python-basics\n
      learning-os export python-basics -o ~/shared/python.zip
    """
    from learning_os.course_io import export_course

    export_course(directory, course_id, output, console)


@main.command("import")
@click.argument("archive", type=click.Path(exists=True))
@click.option(
    "--dir",
    "directory",
    default=".",
    type=click.Path(exists=True),
    help="Workspace directory (default: current).",
)
def import_cmd(archive, directory):
    """Import a course from a .zip file.

    Examples:\n
      learning-os import python-basics.zip\n
      learning-os import ~/shared/python.zip --dir ~/my-learning
    """
    from learning_os.course_io import import_course

    import_course(directory, archive, console)
