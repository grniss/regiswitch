from __future__ import annotations

import typer

from regiswitch.commands.config import app as config_app
from regiswitch.commands.init import init
from regiswitch.commands.profile import app as profile_app
from regiswitch.commands.register import register, unregister
from regiswitch.commands.save import save
from regiswitch.commands.status import status
from regiswitch.commands.switch import switch

app = typer.Typer(
    name="regiswitch",
    help="Switch registered files between named profiles.",
    no_args_is_help=True,
)

app.command("init")(init)
app.add_typer(config_app, name="config")
app.add_typer(profile_app, name="profile")
app.command("register")(register)
app.command("unregister")(unregister)
app.command("save")(save)
app.command("switch")(switch)
app.command("status")(status)
