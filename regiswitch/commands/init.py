from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from regiswitch.core.engine import init_project
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import NotInitializedError

app = typer.Typer()

EXIT_OK = 0
EXIT_INPUT_ERROR = 1


@app.command()
def init(
    path: Annotated[
        Path,
        typer.Argument(help="Directory to initialize. Defaults to current directory."),
    ] = Path("."),
) -> None:
    """Initialize regiswitch in a directory.

    Creates a .regiswitch/ directory with an empty config and profiles storage.
    Run this once per project before registering files or creating profiles.
    """
    target = path.resolve()
    try:
        init_project(target)
    except NotInitializedError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    console.print(f"[green]Initialized[/green] regiswitch in [bold]{target}[/bold]")
