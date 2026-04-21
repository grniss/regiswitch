from abc import ABC, abstractmethod
from pathlib import Path

from regiswitch.models.config import Registry


class StorageBackend(ABC):
    @abstractmethod
    def is_initialized(self) -> bool: ...

    @abstractmethod
    def init(self) -> Registry: ...

    @abstractmethod
    def load_registry(self) -> Registry: ...

    @abstractmethod
    def save_registry(self, registry: Registry) -> None: ...

    @abstractmethod
    def copy_to_profile(self, src: Path, profile_name: str) -> None: ...

    @abstractmethod
    def restore_from_profile(self, profile_name: str, absolute_path: Path) -> None: ...

    @abstractmethod
    def has_stored_version(self, profile_name: str, absolute_path: Path) -> bool: ...

    @abstractmethod
    def delete_profile(self, name: str) -> None: ...
