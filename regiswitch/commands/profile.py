from typing import Annotated

import typer

from regiswitch.core.engine import create_profile, delete_profile, list_profiles
from regiswitch.output.console import console, err_console
from regiswitch.output.tables import profiles_table
from regiswitch.utils.errors import (
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    RegiswitchError,
    RegistryNotInitializedError,
)

app = typer.Typer(help="Manage profiles.")


@app.command("create")
def profile_create(
    name: Annotated[str, typer.Argument(help="Profile name to create.")],
) -> None:
    """Create a new profile.

    Copies current registered files into the new profile so it starts with the
    same file versions as the currently active profile.
    """
    try:
        create_profile(name)
        console.print(f"[green]Profile '{name}' created.[/green]")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except ProfileAlreadyExistsError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@app.command("list")
def profile_list() -> None:
    """List all profiles."""
    try:
        profiles = list_profiles()
        if not profiles:
            console.print("[dim]No profiles yet. Create one with `regiswitch profile create <name>`.[/dim]")
            return
        console.print(profiles_table(profiles))
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("delete")
def profile_delete(
    name: Annotated[str, typer.Argument(help="Profile name to delete.")],
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Delete a profile and its stored files."""
    if not yes:
        typer.confirm(f"Delete profile '{name}' and all its stored files?", abort=True)
    try:
        delete_profile(name)
        console.print(f"[green]Profile '{name}' deleted.[/green]")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except ProfileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
