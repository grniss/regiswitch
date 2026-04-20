from typing import Annotated

import typer

from regiswitch import core
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import RegiswitchError

app = typer.Typer()


@app.command("switch")
def switch(
    profile: Annotated[str, typer.Argument(help="Profile to switch to.")],
) -> None:
    """Switch all registered files to the versions stored in a profile."""
    try:
        missing = core.engine.switch_profile(profile)
    except RegiswitchError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code)
    console.print(f"[green]Switched to profile '[bold]{profile}[/bold]'.[/green]")
    if missing:
        console.print("[yellow]Warning: the following files had no stored version and were skipped:[/yellow]")
        for f in missing:
            console.print(f"  [dim]{f}[/dim]")
