from contextlib import contextmanager
from typing import Generator

from rich.progress import Progress, SpinnerColumn, TextColumn

from regiswitch.output.console import console


@contextmanager
def spinner(message: str) -> Generator[None, None, None]:
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        progress.add_task(message)
        yield
