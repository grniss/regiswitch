"""Profile switching command for regiswitch.
It reads a configuration mapping profile names to a directory containing the versioned files.
Usage: regiswitch switch --profile <name>
"""

from pathlib import Path
import shutil
import typer
from typing import Annotated

from ..output.console import console

def load_profiles() -> dict[str, str]:
    """Load profiles mapping from a JSON file in the project root.
    Expected format: {"profile_name": "path/to/profile_dir", ...}
    """
    config_path = Path(__file__).resolve().parents[2] / "profiles.json"
    if not config_path.is_file():
        console.print(f"[red]Error:[/red] profiles.json not found at {config_path}", stderr=True)
        raise typer.Exit(code=1)
    import json
    with config_path.open() as f:
        return json.load(f)

def switch_profile(profile: Annotated[str, typer.Option("--profile", "-p", help="Profile name to switch to")]):
    """Switch the current working directory files to the selected profile version.
    Files from the profile directory are copied over, overwriting existing ones.
    """
    profiles = load_profiles()
    if profile not in profiles:
        console.print(f"[red]Error:[/red] Unknown profile '{profile}'", stderr=True)
        raise typer.Exit(code=1)
    src_dir = Path(profiles[profile])
    if not src_dir.is_dir():
        console.print(f"[red]Error:[/red] Profile directory '{src_dir}' does not exist", stderr=True)
        raise typer.Exit(code=1)
    cwd = Path.cwd()
    for item in src_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src_dir)
            dest = cwd / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
    console.print(f"Switched to profile '{profile}'", style="green")

# Typer subcommand registration
switch_app = typer.Typer()
switch_app.command()(switch_profile)
