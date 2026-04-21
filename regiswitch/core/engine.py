from __future__ import annotations

from datetime import datetime
from pathlib import Path

from regiswitch.core.registry import load_registry, save_registry
from regiswitch.models.config import ProfileMeta, RegisteredFile, Registry
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoProfilesError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from regiswitch.utils.fs import (
    copy_to_profile,
    has_stored_version,
    profile_dir,
    restore_from_profile,
)


def create_profile(name: str) -> Registry:
    registry = load_registry()
    if name in registry.profiles:
        raise ProfileAlreadyExistsError(name)
    registry.profiles[name] = ProfileMeta(created_at=datetime.now())
    profile_dir(name).mkdir(parents=True, exist_ok=True)
    for file_path in registry.files:
        if has_stored_version(registry.current_profile or "", Path(file_path)):
            copy_to_profile(Path(file_path), name)
    save_registry(registry)
    return registry


def delete_profile(name: str) -> Registry:
    registry = load_registry()
    if name not in registry.profiles:
        raise ProfileNotFoundError(name)
    if registry.current_profile == name:
        from regiswitch.utils.errors import RegiswitchError
        raise RegiswitchError(f"Cannot delete the active profile '{name}'. Switch to another first.")
    import shutil
    shutil.rmtree(profile_dir(name), ignore_errors=True)
    del registry.profiles[name]
    save_registry(registry)
    return registry


def list_profiles(registry: Registry | None = None) -> list[tuple[str, bool]]:
    if registry is None:
        registry = load_registry()
    return [
        (name, name == registry.current_profile)
        for name in registry.profiles
    ]


def register_file(file_path: Path) -> Registry:
    registry = load_registry()
    abs_path = str(file_path.resolve())
    if abs_path in registry.files:
        raise FileAlreadyRegisteredError(abs_path)
    if not file_path.exists():
        from regiswitch.utils.errors import RegiswitchError
        raise RegiswitchError(f"File does not exist: {abs_path}")
    registry.files[abs_path] = RegisteredFile(path=abs_path, registered_at=datetime.now())
    for profile_name in registry.profiles:
        copy_to_profile(Path(abs_path), profile_name)
    save_registry(registry)
    return registry


def unregister_file(file_path: Path) -> Registry:
    registry = load_registry()
    abs_path = str(file_path.resolve())
    if abs_path not in registry.files:
        raise FileNotRegisteredError(abs_path)
    del registry.files[abs_path]
    save_registry(registry)
    return registry


def switch_profile(name: str) -> Registry:
    registry = load_registry()
    if name not in registry.profiles:
        raise ProfileNotFoundError(name)
    for file_path in registry.files:
        path = Path(file_path)
        if has_stored_version(name, path):
            restore_from_profile(name, path)
    registry.current_profile = name
    save_registry(registry)
    return registry


def save_to_profile(profile_name: str | None = None) -> tuple[Registry, str]:
    registry = load_registry()
    if not registry.profiles:
        raise NoProfilesError("No profiles exist. Create one with `regiswitch profile create <name>`.")
    target = profile_name or registry.current_profile
    if target is None:
        raise NoProfilesError("No active profile. Use `regiswitch switch <profile>` first.")
    if target not in registry.profiles:
        raise ProfileNotFoundError(target)
    for file_path in registry.files:
        path = Path(file_path)
        if path.exists():
            copy_to_profile(path, target)
    return registry, target


def list_files(registry: Registry | None = None) -> list[RegisteredFile]:
    if registry is None:
        registry = load_registry()
    return list(registry.files.values())
