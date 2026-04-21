import typer

app = typer.Typer(help="Manage configuration profiles")

@app.command()
def list():
    """List all available profiles"""
    print("Profiles list")
