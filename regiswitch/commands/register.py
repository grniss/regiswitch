from pathlib import Path
from typing import Annotated

import typer

from regiswitch.core.engine import register_file, unregister_file
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    RegiswitchError,
    RegistryNotInitializedError,
)

app = typer.Typer()


@app.command()
def register(
    path: Annotated[Path, typer.Argument(help="Absolute or relative path to the file to register.")],
) -> None:
    """Register a file to be managed by regiswitch.

    The file's current content is copied into all existing profiles. Future
    `switch` calls will replace this file with the profile's stored version.
    """
    try:
        register_file(path)
        console.print(f"[green]Registered:[/green] {path.resolve()}")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except FileAlreadyRegisteredError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@app.command()
def unregister(
    path: Annotated[Path, typer.Argument(help="Path to the file to remove from the registry.")],
) -> None:
    """Remove a file from the registry.

    The file on disk is not modified; only the registry entry is removed.
    Stored profile copies are kept on disk but are no longer managed.
    """
    try:
        unregister_file(path)
        console.print(f"[green]Unregistered:[/green] {path.resolve()}")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except FileNotRegisteredError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
