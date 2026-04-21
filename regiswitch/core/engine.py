from __future__ import annotations

from datetime import datetime
from pathlib import Path

from regiswitch.core.backends import get_backend
from regiswitch.core.backends.base import StorageBackend
from regiswitch.models.config import ProfileMeta, RegisteredFile, Registry
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoProfilesError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    RegiswitchError,
)


def _b(backend: StorageBackend | None) -> StorageBackend:
    return backend or get_backend()


def create_profile(name: str, backend: StorageBackend | None = None) -> Registry:
    b = _b(backend)
    registry = b.load_registry()
    if name in registry.profiles:
        raise ProfileAlreadyExistsError(name)
    registry.profiles[name] = ProfileMeta(created_at=datetime.now())
    for file_path in registry.files:
        if b.has_stored_version(registry.current_profile or "", Path(file_path)):
            b.copy_to_profile(Path(file_path), name)
    b.save_registry(registry)
    return registry


def delete_profile(name: str, backend: StorageBackend | None = None) -> Registry:
    b = _b(backend)
    registry = b.load_registry()
    if name not in registry.profiles:
        raise ProfileNotFoundError(name)
    if registry.current_profile == name:
        raise RegiswitchError(
            f"Cannot delete the active profile '{name}'. Switch to another first."
        )
    b.delete_profile(name)
    del registry.profiles[name]
    b.save_registry(registry)
    return registry


def list_profiles(
    registry: Registry | None = None, backend: StorageBackend | None = None
) -> list[tuple[str, bool]]:
    if registry is None:
        registry = _b(backend).load_registry()
    return [(name, name == registry.current_profile) for name in registry.profiles]


def register_file(file_path: Path, backend: StorageBackend | None = None) -> Registry:
    b = _b(backend)
    registry = b.load_registry()
    abs_path = str(file_path.resolve())
    if abs_path in registry.files:
        raise FileAlreadyRegisteredError(abs_path)
    if not file_path.exists():
        raise RegiswitchError(f"File does not exist: {abs_path}")
    registry.files[abs_path] = RegisteredFile(path=abs_path, registered_at=datetime.now())
    for profile_name in registry.profiles:
        b.copy_to_profile(Path(abs_path), profile_name)
    b.save_registry(registry)
    return registry


def unregister_file(file_path: Path, backend: StorageBackend | None = None) -> Registry:
    b = _b(backend)
    registry = b.load_registry()
    abs_path = str(file_path.resolve())
    if abs_path not in registry.files:
        raise FileNotRegisteredError(abs_path)
    del registry.files[abs_path]
    b.save_registry(registry)
    return registry


def switch_profile(name: str, backend: StorageBackend | None = None) -> Registry:
    b = _b(backend)
    registry = b.load_registry()
    if name not in registry.profiles:
        raise ProfileNotFoundError(name)
    for file_path in registry.files:
        path = Path(file_path)
        if b.has_stored_version(name, path):
            b.restore_from_profile(name, path)
    registry.current_profile = name
    b.save_registry(registry)
    return registry


def save_to_profile(
    profile_name: str | None = None, backend: StorageBackend | None = None
) -> tuple[Registry, str]:
    b = _b(backend)
    registry = b.load_registry()
    if not registry.profiles:
        raise NoProfilesError(
            "No profiles exist. Create one with `regiswitch profile create <name>`."
        )
    target = profile_name or registry.current_profile
    if target is None:
        raise NoProfilesError("No active profile. Use `regiswitch switch <profile>` first.")
    if target not in registry.profiles:
        raise ProfileNotFoundError(target)
    for file_path in registry.files:
        path = Path(file_path)
        if path.exists():
            b.copy_to_profile(path, target)
    return registry, target


def list_files(
    registry: Registry | None = None, backend: StorageBackend | None = None
) -> list[RegisteredFile]:
    if registry is None:
        registry = _b(backend).load_registry()
    return list(registry.files.values())
