class RegiswitchError(Exception):
    """Base error for regiswitch."""


class NotInitializedError(RegiswitchError):
    """Raised when .regiswitch/ directory does not exist in the project."""


class ProfileNotFoundError(RegiswitchError):
    """Raised when the requested profile does not exist."""


class ProfileAlreadyExistsError(RegiswitchError):
    """Raised when trying to create a profile that already exists."""


class FileNotRegisteredError(RegiswitchError):
    """Raised when the file is not in the registered list."""


class FileAlreadyRegisteredError(RegiswitchError):
    """Raised when the file is already registered."""


class NoActiveProfileError(RegiswitchError):
    """Raised when an operation requires an active profile but none is set."""
