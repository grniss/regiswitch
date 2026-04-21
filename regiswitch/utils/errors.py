class RegiswitchError(Exception):
    pass


class RegistryNotInitializedError(RegiswitchError):
    pass


class ProfileNotFoundError(RegiswitchError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Profile '{name}' does not exist")
        self.name = name


class ProfileAlreadyExistsError(RegiswitchError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Profile '{name}' already exists")
        self.name = name


class FileNotRegisteredError(RegiswitchError):
    def __init__(self, path: str) -> None:
        super().__init__(f"File '{path}' is not registered")
        self.path = path


class FileAlreadyRegisteredError(RegiswitchError):
    def __init__(self, path: str) -> None:
        super().__init__(f"File '{path}' is already registered")
        self.path = path


class NoProfilesError(RegiswitchError):
    pass
