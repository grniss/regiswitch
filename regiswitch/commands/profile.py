from typing import Annotated

import typer

from regiswitch import core
from regiswitch.output.console import err_console
from regiswitch.output.tables import print_profiles
from regiswitch.utils import fs
from regiswitch.utils.errors import EXIT_INPUT_ERROR, EXIT_RUNTIME_ERROR, RegiswitchError

app = typer.Typer(help="Manage profiles.")


@app.command("create")
def profile_create(
    name: Annotated[str, typer.Argument(help="Name of the profile to create.")],
) -> None:
    """Create a new profile."""
    try:
        core.engine.create_profile(name)
    except RegiswitchError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code)
    typer.echo(f"Profile '{name}' created.")


@app.command("delete")
def profile_delete(
    name: Annotated[str, typer.Argument(help="Name of the profile to delete.")],
    yes: Annotated[bool, typer.Option("--yes / --no-yes", "-y", help="Skip confirmation.")] = False,
) -> None:
    """Delete a profile and its stored files."""
    if not yes:
        confirmed = typer.confirm(f"Delete profile '{name}' and all its stored files?")
        if not confirmed:
            raise typer.Abort()
    try:
        core.engine.delete_profile(name)
    except RegiswitchError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code)
    typer.echo(f"Profile '{name}' deleted.")


@app.command("list")
def profile_list() -> None:
    """List all profiles."""
    profiles = core.engine.list_profiles()
    config = fs.load_config()
    if not profiles:
        typer.echo("No profiles found. Create one with: regiswitch profile create <name>")
        return
    print_profiles(profiles, config.active_profile)
