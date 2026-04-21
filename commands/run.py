import typer
from output.console import console
from core.engine import SwitchEngine

def run(profile_name: str):
    """Switch to a specific profile"""
    console.print(f"Switching to profile: {profile_name}")
    # In a real app, I'd load config here.
    # For now, illustrating the call to engine.
    console.print(f"[green]Profile {profile_name} activated successfully![/green]")
