import typer

from regiswitch.core.registry import init_registry, is_initialized
from regiswitch.output.console import console
from regiswitch.utils.fs import REGISTRY_FILE

app = typer.Typer()


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Re-initialize even if already initialized."),
) -> None:
    """Initialize the regiswitch registry.

    Creates the config directory and registry file at ~/.config/regiswitch/.
    """
    if is_initialized() and not force:
        console.print("[yellow]Registry already initialized.[/yellow]")
        console.print(f"Config: [dim]{REGISTRY_FILE}[/dim]")
        console.print("Use [bold]--force[/bold] to re-initialize.")
        raise typer.Exit(code=0)
    init_registry()
    console.print("[green]Registry initialized.[/green]")
    console.print(f"Config: [dim]{REGISTRY_FILE}[/dim]")
