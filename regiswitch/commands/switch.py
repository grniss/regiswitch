from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from regiswitch.core.engine import switch_profile
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import NotInitializedError, ProfileNotFoundError
from regiswitch.utils.fs import find_project_root, load_storage_backend

EXIT_OK = 0
EXIT_INPUT_ERROR = 1

app = typer.Typer()


@app.command()
def switch(
    profile: Annotated[str, typer.Argument(help="Name of the profile to switch to.")],
) -> None:
    """Switch to a profile by restoring its stored files.

    All registered files that have a stored copy in the named profile are overwritten
    with the profile's version. The profile is then set as the active profile.
    Files without a stored copy in the target profile are left unchanged.
    """
    try:
        root = find_project_root(Path.cwd())
        storage = load_storage_backend(root)
        applied = switch_profile(root, profile, storage)
    except (NotInitializedError, ProfileNotFoundError) as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    if applied:
        console.print(f"[green]Switched[/green] to profile [bold]{profile}[/bold]")
        for f in applied:
            console.print(f"  [dim]restored[/dim] {f}")
    else:
        console.print(
            f"[yellow]Switched[/yellow] to profile [bold]{profile}[/bold] "
            "(no stored files were found to restore)"
        )
