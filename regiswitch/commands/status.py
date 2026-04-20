import typer

from regiswitch import core
from regiswitch.output.tables import print_status

app = typer.Typer()


@app.command("status")
def status() -> None:
    """Show the active profile and sync state of all registered files."""
    active_profile, rows = core.engine.get_status()
    print_status(active_profile, rows)
