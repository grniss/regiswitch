from pathlib import Path

from regiswitch.utils.errors import EXIT_INPUT_ERROR, RegiswitchError


def require_existing_file(path: Path) -> None:
    if not path.exists():
        raise RegiswitchError(f"'{path}' does not exist.", EXIT_INPUT_ERROR)
    if not path.is_file():
        raise RegiswitchError(f"'{path}' is not a file.", EXIT_INPUT_ERROR)
