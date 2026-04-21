import typer
from .commands import init, run, config

app = typer.Typer(help="Regiswitch - Manage environment file profiles")

app.add_typer(config.app, name="config")
app.command()(run.run)
app.command()(init.init)

if __name__ == "__main__":
    app()
