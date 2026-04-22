from typing import Annotated, Optional

import typer

from regiswitch.core.engine import save_to_profile
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import (
    NoProfilesError,
    ProfileNotFoundError,
    RegiswitchError,
    RegistryNotInitializedError,
)

app = typer.Typer()


@app.command()
def save(
    profile: Annotated[Optional[str], typer.Argument(help="Profile to save into. Defaults to the active profile.")] = None,
) -> None:
    """Save current registered files into a profile.

    Copies the current on-disk state of all registered files into the specified
    profile (or the active profile if none is given). Use this before switching
    away to preserve your changes.
    """
    try:
        _, target = save_to_profile(profile)
        console.print(f"[green]Saved current files to profile '{target}'.[/green]")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except (ProfileNotFoundError, NoProfilesError) as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
