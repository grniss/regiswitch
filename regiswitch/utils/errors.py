EXIT_OK = 0
EXIT_INPUT_ERROR = 1
EXIT_RUNTIME_ERROR = 2


class RegiswitchError(Exception):
    """Base error for all regiswitch failures."""

    def __init__(self, message: str, exit_code: int = EXIT_RUNTIME_ERROR) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class ProfileNotFoundError(RegiswitchError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Profile '{name}' does not exist.", EXIT_INPUT_ERROR)


class ProfileAlreadyExistsError(RegiswitchError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Profile '{name}' already exists.", EXIT_INPUT_ERROR)


class FileNotRegisteredError(RegiswitchError):
    def __init__(self, path: str) -> None:
        super().__init__(f"'{path}' is not a registered file.", EXIT_INPUT_ERROR)


class FileAlreadyRegisteredError(RegiswitchError):
    def __init__(self, path: str) -> None:
        super().__init__(f"'{path}' is already registered.", EXIT_INPUT_ERROR)


class NoActiveProfileError(RegiswitchError):
    def __init__(self) -> None:
        super().__init__("No active profile set. Run 'regiswitch switch <profile>' first.", EXIT_INPUT_ERROR)
