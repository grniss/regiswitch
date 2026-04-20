from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Generator

from rich.progress import Progress, SpinnerColumn, TextColumn

from regiswitch.output.console import console


@contextmanager
def spinner(message: str) -> Generator[None, None, None]:
    """Context manager that displays a spinner while work is being done."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(message, total=None)
        yield
