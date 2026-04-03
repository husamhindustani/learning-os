"""Learning OS CLI — entry point for all commands."""

import re

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


@main.command("add-book")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--dir",
    "directory",
    default=".",
    type=click.Path(exists=True),
    help="Workspace directory (default: current).",
)
def add_book(file_path, directory):
    """Import a book (PDF/EPUB) and extract its structure for course creation.

    Parses the book's table of contents and chapter text, then writes
    a book-outline.yaml and individual chapter markdown files under
    books/<book-slug>/.

    After importing, say "create a course from <book-slug>" in the AI
    chat to build a course around the book.

    Examples:\n
      learning-os add-book ~/books/clean-code.pdf\n
      learning-os add-book pragmatic-programmer.epub\n
      learning-os add-book ~/Downloads/designing-data.pdf --dir ~/my-learning
    """
    from pathlib import Path as P

    source = P(file_path).resolve()
    suffix = source.suffix.lower()

    if suffix not in (".pdf", ".epub"):
        console.print(
            f"[red]Unsupported format: {suffix}[/red]\n"
            "Supported: .pdf, .epub"
        )
        raise SystemExit(1)

    try:
        from learning_os.book_parser import check_book_deps

        check_book_deps("pdf" if suffix == ".pdf" else "epub")
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    console.print(
        Panel.fit(
            "[bold cyan]Learning OS[/bold cyan] — Add Book\n"
            f"Parsing [bold]{source.name}[/bold]",
            border_style="cyan",
        )
    )
    console.print()

    from learning_os.book_parser import parse_book, write_book_output

    target = P(directory).resolve()
    book_slug = source.stem.lower()
    book_slug = re.sub(r"[^a-z0-9]+", "-", book_slug).strip("-")
    book_dir = target / "books" / book_slug

    if book_dir.exists():
        if not click.confirm(
            f"books/{book_slug}/ already exists. Overwrite?", default=False
        ):
            console.print("[dim]Cancelled.[/dim]")
            return
        import shutil

        shutil.rmtree(book_dir)

    book_dir.mkdir(parents=True, exist_ok=True)

    # Copy original file
    import shutil

    dest_file = book_dir / source.name
    shutil.copy2(source, dest_file)
    console.print(f"  [green]+[/green] books/{book_slug}/{source.name}")

    # Parse
    with console.status("[bold cyan]Extracting chapters..."):
        try:
            parsed = parse_book(source)
        except RuntimeError as e:
            console.print(f"\n[red]Error: {e}[/red]")
            raise SystemExit(1)

    fmt = parsed["format"].upper()
    pages_info = f", {parsed['total_pages']} pages" if parsed.get("total_pages") else ""
    console.print(f"  [dim]Format: {fmt}{pages_info}[/dim]")

    if parsed.get("authors"):
        console.print(f"  [dim]Authors: {', '.join(parsed['authors'])}[/dim]")

    # Write extracted content
    outline_path, content_paths = write_book_output(parsed, book_dir)

    console.print(
        f"  [green]+[/green] books/{book_slug}/book-outline.yaml "
        f"({len(parsed['chapters'])} chapters)"
    )
    console.print(
        f"  [green]+[/green] books/{book_slug}/book-content/ "
        f"({len(content_paths)} files)"
    )

    console.print()
    console.print(f'[bold green]Book ready:[/bold green] "{parsed["title"]}"')
    console.print()
    console.print("[bold]Next:[/bold]")
    console.print(
        f'  Say [cyan]"create a course from {book_slug}"[/cyan] in the AI chat'
    )
    console.print()
    console.print(
        f"[dim]Tip: The original {fmt} is in books/{book_slug}/ — "
        "consider adding books/ to .gitignore if it's large.[/dim]"
    )


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
