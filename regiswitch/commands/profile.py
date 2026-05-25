from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from regiswitch.core.engine import create_profile, delete_profile, list_profiles
from regiswitch.core.validator import validate_profile_name
from regiswitch.output.console import console, err_console
from regiswitch.output.tables import print_profiles_table
from regiswitch.utils.errors import (
    NotInitializedError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    RegiswitchError,
)
from regiswitch.utils.fs import find_project_root, load_config, load_storage_backend

EXIT_OK = 0
EXIT_INPUT_ERROR = 1

app = typer.Typer(help="Manage profiles.")


@app.command("create")
def profile_create(
    name: Annotated[str, typer.Argument(help="Name of the profile to create.")],
) -> None:
    """Create a new profile.

    If no profile is currently active, the new profile becomes the active one.
    """
    try:
        validate_profile_name(name)
        root = find_project_root(Path.cwd())
        storage = load_storage_backend(root)
        create_profile(root, name, storage)
    except (NotInitializedError, ProfileAlreadyExistsError, RegiswitchError) as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    console.print(f"[green]Created[/green] profile [bold]{name}[/bold]")


@app.command("list")
def profile_list() -> None:
    """List all profiles, highlighting the currently active one."""
    try:
        root = find_project_root(Path.cwd())
        config = load_config(root)
        storage = load_storage_backend(root)
        profiles = list_profiles(storage)
    except NotInitializedError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    if not profiles:
        console.print("[dim]No profiles found. Run 'regiswitch profile create <name>'.[/dim]")
        return
    print_profiles_table(profiles, config.current_profile)


@app.command("delete")
def profile_delete(
    name: Annotated[str, typer.Argument(help="Name of the profile to delete.")],
    yes: Annotated[
        bool,
        typer.Option("--yes / --no-yes", "-y", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """Delete a profile and all its stored files.

    If the deleted profile is currently active, the active profile is cleared.
    """
    if not yes:
        confirmed = typer.confirm(f"Delete profile '{name}' and all its stored files?")
        if not confirmed:
            console.print("Aborted.")
            raise typer.Exit(code=EXIT_OK)
    try:
        root = find_project_root(Path.cwd())
        storage = load_storage_backend(root)
        delete_profile(root, name, storage)
    except (NotInitializedError, ProfileNotFoundError) as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    console.print(f"[red]Deleted[/red] profile [bold]{name}[/bold]")
