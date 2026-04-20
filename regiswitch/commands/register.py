from pathlib import Path
from typing import Annotated

import typer

from regiswitch import core
from regiswitch.output.console import err_console
from regiswitch.utils.errors import RegiswitchError

app = typer.Typer()


@app.command("register")
def register(
    path: Annotated[Path, typer.Argument(help="File path to register.")],
) -> None:
    """Register a file to be managed by regiswitch.

    The file will be snapshotted into every existing profile immediately
    if it is present on disk.
    """
    try:
        core.engine.register_file(path)
    except RegiswitchError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code)
    typer.echo(f"Registered '{path.resolve()}'.")


@app.command("unregister")
def unregister(
    path: Annotated[Path, typer.Argument(help="File path to unregister.")],
) -> None:
    """Unregister a file from regiswitch management.

    Stored profile copies are kept; only the registration is removed.
    """
    try:
        core.engine.unregister_file(path)
    except RegiswitchError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code)
    typer.echo(f"Unregistered '{path.resolve()}'.")
