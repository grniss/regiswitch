import typer
from rich.panel import Panel

from regiswitch.core.engine import list_files, list_profiles
from regiswitch.core.registry import load_registry
from regiswitch.output.console import console, err_console
from regiswitch.output.tables import files_table, profiles_table
from regiswitch.utils.errors import RegiswitchError, RegistryNotInitializedError

app = typer.Typer()


@app.command()
def status() -> None:
    """Show the active profile and all registered files."""
    try:
        registry = load_registry()
        active = registry.current_profile or "[dim]none[/dim]"
        console.print(Panel(f"Active profile: [bold cyan]{active}[/bold cyan]", title="regiswitch"))

        profiles = list_profiles(registry)
        if profiles:
            console.print(profiles_table(profiles))

        files = list_files(registry)
        if files:
            console.print(files_table(files, registry.current_profile))
        else:
            console.print("[dim]No files registered. Use `regiswitch register <path>` to add files.[/dim]")
    except RegistryNotInitializedError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
