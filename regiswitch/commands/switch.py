from typing import Annotated

import typer

from regiswitch.core.engine import switch_profile
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import (
    ProfileNotFoundError,
    RegiswitchError,
    RegistryNotInitializedError,
)

app = typer.Typer()


@app.command()
def switch(
    profile: Annotated[str, typer.Argument(help="Name of the profile to activate.")],
) -> None:
    """Switch to a profile, replacing registered files with that profile's versions.

    Each registered file on disk is overwritten with the version stored in the
    target profile. The active profile in the registry is updated.
    """
    try:
        registry = switch_profile(profile)
        file_count = len(registry.files)
        console.print(f"[green]Switched to profile '{profile}'.[/green] ({file_count} file(s) restored)")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except ProfileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
