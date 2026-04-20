from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from regiswitch.core.engine import save_to_profile
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import (
    NoActiveProfileError,
    NotInitializedError,
    ProfileNotFoundError,
)
from regiswitch.utils.fs import find_project_root

EXIT_OK = 0
EXIT_INPUT_ERROR = 1

app = typer.Typer()


@app.command()
def save(
    profile: Annotated[
        str | None,
        typer.Option("--profile", "-p", help="Profile to save into. Defaults to active profile."),
    ] = None,
) -> None:
    """Save current registered files into a profile.

    Copies all registered files into the profile's stored directory so they can be
    restored later with 'switch'. Defaults to the currently active profile.
    """
    try:
        root = find_project_root(Path.cwd())
        used_profile = save_to_profile(root, profile)
    except (NotInitializedError, NoActiveProfileError, ProfileNotFoundError) as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    console.print(f"[green]Saved[/green] files to profile [bold]{used_profile}[/bold]")
