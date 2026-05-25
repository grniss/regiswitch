from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from regiswitch.core.engine import register_file, unregister_file
from regiswitch.core.validator import validate_file_exists, validate_rel_path
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NotInitializedError,
    RegiswitchError,
)
from regiswitch.utils.fs import find_project_root

EXIT_OK = 0
EXIT_INPUT_ERROR = 1

app = typer.Typer()


@app.command()
def register(
    file: Annotated[str, typer.Argument(help="Relative path of the file to register.")],
) -> None:
    """Register a file to be tracked across profiles.

    The path must be relative to the project root (the directory containing .regiswitch/).
    Once registered, the file can be saved into profiles and restored via 'switch'.
    """
    try:
        root = find_project_root(Path.cwd())
        validate_rel_path(file)
        validate_file_exists(root, file)
        register_file(root, file)
    except (NotInitializedError, FileAlreadyRegisteredError, RegiswitchError) as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    console.print(f"[green]Registered[/green] [bold]{file}[/bold]")


@app.command()
def unregister(
    file: Annotated[str, typer.Argument(help="Relative path of the file to unregister.")],
) -> None:
    """Unregister a file so it is no longer tracked across profiles.

    Stored copies in profiles are NOT deleted; only the tracking entry is removed.
    """
    try:
        root = find_project_root(Path.cwd())
        validate_rel_path(file)
        unregister_file(root, file)
    except (NotInitializedError, FileNotRegisteredError, RegiswitchError) as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    console.print(f"[yellow]Unregistered[/yellow] [bold]{file}[/bold]")
