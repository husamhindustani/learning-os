"""Course import and export."""

import shutil
import zipfile
from pathlib import Path

import click
from rich.console import Console


def export_course(directory: str, course_id: str, output: str, console: Console):
    """Export a course as a .zip file."""
    target = Path(directory).resolve()
    course_dir = target / "courses" / course_id

    if not course_dir.is_dir():
        console.print(f"[red]Course not found: courses/{course_id}/[/red]")
        available = _list_course_ids(target)
        if available:
            console.print(f"[dim]Available courses: {', '.join(available)}[/dim]")
        raise SystemExit(1)

    if not (course_dir / "COURSE.yaml").exists():
        console.print(
            f"[red]courses/{course_id}/ has no COURSE.yaml — not a valid course[/red]"
        )
        raise SystemExit(1)

    if output:
        out_path = Path(output).resolve()
    else:
        out_path = Path.cwd() / f"{course_id}.zip"

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(course_dir.rglob("*")):
            if file.is_file():
                arcname = f"{course_id}/{file.relative_to(course_dir)}"
                zf.write(file, arcname)

    file_count = sum(1 for f in course_dir.rglob("*") if f.is_file())
    console.print(f"[bold green]Exported:[/bold green] {out_path}")
    console.print(f"[dim]Contains: {course_id}/ ({file_count} files)[/dim]")


def import_course(directory: str, archive_path: str, console: Console):
    """Import a course from a .zip file."""
    target = Path(directory).resolve()
    archive = Path(archive_path).resolve()

    if not archive.exists():
        console.print(f"[red]File not found: {archive}[/red]")
        raise SystemExit(1)

    courses_dir = target / "courses"
    courses_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "r") as zf:
        names = zf.namelist()
        if not names:
            console.print("[red]Archive is empty[/red]")
            raise SystemExit(1)

        top_dirs = {n.split("/")[0] for n in names if "/" in n}
        if len(top_dirs) != 1:
            console.print(
                "[red]Archive structure not recognized — "
                "expected a single course directory[/red]"
            )
            raise SystemExit(1)

        course_id = top_dirs.pop()

        has_yaml = any(n.endswith("COURSE.yaml") for n in names)
        if not has_yaml:
            console.print("[yellow]Warning: No COURSE.yaml found in archive[/yellow]")

        dest_dir = courses_dir / course_id
        if dest_dir.exists():
            if not click.confirm(
                f"Course '{course_id}' already exists. Overwrite?", default=False
            ):
                console.print("[dim]Import cancelled.[/dim]")
                return
            shutil.rmtree(dest_dir)

        zf.extractall(courses_dir)

    console.print(f"[bold green]Imported:[/bold green] courses/{course_id}/")
    console.print("[dim]Run 'learning-os validate' to check the imported course.[/dim]")


def _list_course_ids(target: Path) -> list:
    """List available course IDs."""
    courses_dir = target / "courses"
    if not courses_dir.is_dir():
        return []
    return [
        d.name
        for d in sorted(courses_dir.iterdir())
        if d.is_dir() and (d / "COURSE.yaml").exists()
    ]
