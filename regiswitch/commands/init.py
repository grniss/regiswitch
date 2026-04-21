import typer

from regiswitch.core.backends import get_backend
from regiswitch.output.console import console
from regiswitch.utils.errors import RegiswitchError

app = typer.Typer()


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Re-initialize even if already initialized."),
) -> None:
    """Initialize the regiswitch registry.

    Creates the storage directory and registry file. The storage location
    depends on the configured backend (local path or S3 bucket).
    """
    try:
        backend = get_backend()
        if backend.is_initialized() and not force:
            console.print("[yellow]Registry already initialized.[/yellow]")
            console.print("Use [bold]--force[/bold] to re-initialize.")
            raise typer.Exit(code=0)
        backend.init()
        console.print("[green]Registry initialized.[/green]")
    except RegiswitchError as e:
        from regiswitch.output.console import err_console
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
