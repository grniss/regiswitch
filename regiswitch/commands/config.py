from typing import Annotated

import typer

from regiswitch.core import engine
from regiswitch.output.console import console

app = typer.Typer(help="Manage regiswitch configuration.")


@app.command("auto-save")
def config_auto_save(
    enable: Annotated[
        bool,
        typer.Option(
            "--enable/--disable",
            help="Enable or disable auto-save before switching profiles.",
        ),
    ] = True,
) -> None:
    """Enable or disable auto-saving the current profile before switching."""
    engine.set_auto_save(enable)
    status = "enabled" if enable else "disabled"
    console.print(f"[green]Auto-save {status}.[/green]")
