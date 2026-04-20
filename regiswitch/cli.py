import typer

from regiswitch.commands.profile import app as profile_app
from regiswitch.commands.register import app as register_app
from regiswitch.commands.snapshot import app as snapshot_app
from regiswitch.commands.status import app as status_app
from regiswitch.commands.switch import app as switch_app

app = typer.Typer(
    name="regiswitch",
    help="Switch registered files between named profiles.",
    no_args_is_help=True,
)

app.add_typer(profile_app, name="profile")

# Flatten single-command sub-apps as top-level commands
app.registered_commands += register_app.registered_commands
app.registered_commands += switch_app.registered_commands
app.registered_commands += snapshot_app.registered_commands
app.registered_commands += status_app.registered_commands
