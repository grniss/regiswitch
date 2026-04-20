from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from regiswitch.core.storage import StorageBackend
from regiswitch.models.config import RegiswitchConfig, REGISWITCH_DIR
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoActiveProfileError,
    NotInitializedError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from regiswitch.utils.fs import load_config, save_config


@dataclass
class StatusResult:
    root: Path
    current_profile: str | None
    profiles: list[str]
    registered_files: list[str]
    drift: list[str]


def init_project(root: Path) -> None:
    """Create .regiswitch/ directory and empty config in root."""
    regiswitch_dir = root / REGISWITCH_DIR
    if regiswitch_dir.exists():
        raise NotInitializedError(
            f"{regiswitch_dir} already exists. Project is already initialized."
        )
    regiswitch_dir.mkdir(parents=True)
    config = RegiswitchConfig()
    save_config(root, config)


def register_file(root: Path, rel_path: str) -> None:
    """Add rel_path to the registered files list."""
    config = load_config(root)
    if rel_path in config.registered_files:
        raise FileAlreadyRegisteredError(f"'{rel_path}' is already registered.")
    config.registered_files.append(rel_path)
    save_config(root, config)


def unregister_file(root: Path, rel_path: str) -> None:
    """Remove rel_path from the registered files list."""
    config = load_config(root)
    if rel_path not in config.registered_files:
        raise FileNotRegisteredError(f"'{rel_path}' is not registered.")
    config.registered_files.remove(rel_path)
    save_config(root, config)


def create_profile(root: Path, name: str, storage: StorageBackend) -> None:
    """Create a new empty profile in the configured storage."""
    if storage.profile_exists(name):
        raise ProfileAlreadyExistsError(f"Profile '{name}' already exists.")
    storage.create_profile(name)
    config = load_config(root)
    if config.current_profile is None:
        config.current_profile = name
        save_config(root, config)


def delete_profile(root: Path, name: str, storage: StorageBackend) -> None:
    """Delete a profile and clear active profile if needed."""
    if not storage.profile_exists(name):
        raise ProfileNotFoundError(f"Profile '{name}' does not exist.")
    storage.delete_profile(name)
    config = load_config(root)
    if config.current_profile == name:
        config.current_profile = None
        save_config(root, config)


def list_profiles(storage: StorageBackend) -> list[str]:
    """Return sorted list of profile names from storage."""
    return storage.list_profiles()


def save_to_profile(
    root: Path, storage: StorageBackend, profile: str | None = None
) -> str:
    """Copy all registered files into the profile's storage. Returns profile name used."""
    config = load_config(root)
    target = profile or config.current_profile
    if target is None:
        raise NoActiveProfileError(
            "No active profile. Specify --profile or run 'regiswitch profile create'."
        )
    if not storage.profile_exists(target):
        raise ProfileNotFoundError(f"Profile '{target}' does not exist.")
    for rel_path in config.registered_files:
        src = root / rel_path
        if src.exists():
            storage.put_file(src, rel_path, target)
    return target


def switch_profile(
    root: Path, name: str, storage: StorageBackend
) -> list[str]:
    """Replace registered files with versions from the named profile. Returns applied files."""
    if not storage.profile_exists(name):
        raise ProfileNotFoundError(f"Profile '{name}' does not exist.")
    config = load_config(root)
    applied: list[str] = []
    for rel_path in config.registered_files:
        if storage.has_file(rel_path, name):
            storage.get_file(root / rel_path, rel_path, name)
            applied.append(rel_path)
    config.current_profile = name
    save_config(root, config)
    return applied


def get_status(root: Path, storage: StorageBackend) -> StatusResult:
    """Collect current project state for display."""
    config = load_config(root)
    profiles = list_profiles(storage)
    drift: list[str] = []
    if config.current_profile and storage.profile_exists(config.current_profile):
        for rel_path in config.registered_files:
            working = root / rel_path
            if not storage.has_file(rel_path, config.current_profile):
                if working.exists():
                    drift.append(rel_path)
            elif working.exists():
                import tempfile, shutil
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                try:
                    storage.get_file(tmp_path, rel_path, config.current_profile)
                    if working.read_bytes() != tmp_path.read_bytes():
                        drift.append(rel_path)
                finally:
                    tmp_path.unlink(missing_ok=True)
    return StatusResult(
        root=root,
        current_profile=config.current_profile,
        profiles=profiles,
        registered_files=config.registered_files,
        drift=drift,
    )
