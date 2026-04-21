"""Entry point for the regiswitch CLI.

This module creates a Typer application that aggregates all subcommands
defined in the `commands` package.  The commands are discovered at
runtime by importing the package, which allows the test suite to
exercise them without manual imports.

Running `python -m regiswitch` or installing with the console script
defined in the project metadata will invoke this file.
"""

import typer
from pathlib import Path
import importlib
import pkgutil

app = typer.Typer()

# Dynamically register all command modules in the commands package
PACKAGE_NAME = "commands"
package = importlib.import_module(PACKAGE_NAME)
for _, modname, _ in pkgutil.iter_modules(package.__path__):
    module = importlib.import_module(f"{PACKAGE_NAME}.{modname}")
    if hasattr(module, "switch_app"):
        # Register the sub-CLI under the module's name
        app.add_typer(module.switch_app, name=modname)

if __name__ == "__main__":
    app()
