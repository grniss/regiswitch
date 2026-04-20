from typing import Annotated

import typer

from regiswitch import core
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import RegiswitchError

app = typer.Typer()


@app.command("snapshot")
def snapshot(
    profile: Annotated[str | None, typer.Argument(help="Profile to snapshot into (defaults to active profile).")] = None,
) -> None:
    """Save current state of all registered files into a profile.

    Defaults to the active profile when no profile name is given.
    """
    try:
        missing = core.engine.snapshot(profile)
    except RegiswitchError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code)
    console.print("[green]Snapshot saved.[/green]")
    if missing:
        console.print("[yellow]Warning: these files do not exist on disk and were skipped:[/yellow]")
        for f in missing:
            console.print(f"  [dim]{f}[/dim]")
