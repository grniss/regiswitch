from typing import Annotated, Optional

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
    auto_save: Annotated[
        Optional[bool],
        typer.Option(
            "--auto-save/--no-auto-save",
            help="Save current profile before switching. Overrides registry auto_save setting.",
        ),
    ] = None,
) -> None:
    """Switch to a profile, replacing registered files with that profile's versions.

    Each registered file on disk is overwritten with the version stored in the
    target profile. The active profile in the registry is updated.
    """
    try:
        registry = switch_profile(profile, auto_save=auto_save)
        effective_save = auto_save if auto_save is not None else registry.auto_save
        if effective_save:
            console.print("[dim]Saved current profile before switching.[/dim]")
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
