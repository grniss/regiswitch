from __future__ import annotations

from pathlib import Path

import typer

from regiswitch.core.engine import get_status
from regiswitch.output.console import err_console
from regiswitch.output.tables import print_status_table
from regiswitch.utils.errors import NotInitializedError
from regiswitch.utils.fs import find_project_root, load_storage_backend

EXIT_INPUT_ERROR = 1

app = typer.Typer()


@app.command()
def status() -> None:
    """Show the current regiswitch state.

    Displays the active profile, all profiles, registered files, and any registered
    files that have been modified since the last save (drift detection).
    """
    try:
        root = find_project_root(Path.cwd())
        storage = load_storage_backend(root)
        result = get_status(root, storage)
    except NotInitializedError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    print_status_table(
        current_profile=result.current_profile,
        profiles=result.profiles,
        registered_files=result.registered_files,
        drift=result.drift,
    )
