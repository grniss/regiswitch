from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from regiswitch.models.config import RegiswitchConfig, REGISWITCH_DIR, PROFILES_DIR
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoActiveProfileError,
    NotInitializedError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from regiswitch.utils.fs import (
    copy_file_from_profile,
    copy_file_to_profile,
    load_config,
    profile_has_file,
    save_config,
)


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
    (regiswitch_dir / PROFILES_DIR).mkdir()
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


def create_profile(root: Path, name: str) -> None:
    """Create a new empty profile directory."""
    config = load_config(root)
    profile_dir = RegiswitchConfig.profile_dir(root, name)
    if profile_dir.exists():
        raise ProfileAlreadyExistsError(f"Profile '{name}' already exists.")
    profile_dir.mkdir(parents=True)
    if config.current_profile is None:
        config.current_profile = name
        save_config(root, config)


def delete_profile(root: Path, name: str) -> None:
    """Delete a profile directory and clear active profile if needed."""
    profile_dir = RegiswitchConfig.profile_dir(root, name)
    if not profile_dir.exists():
        raise ProfileNotFoundError(f"Profile '{name}' does not exist.")
    shutil.rmtree(profile_dir)
    config = load_config(root)
    if config.current_profile == name:
        config.current_profile = None
        save_config(root, config)


def list_profiles(root: Path) -> list[str]:
    """Return sorted list of profile names."""
    profiles_dir = RegiswitchConfig.profiles_dir(root)
    if not profiles_dir.exists():
        return []
    return sorted(p.name for p in profiles_dir.iterdir() if p.is_dir())


def save_to_profile(root: Path, profile: str | None = None) -> str:
    """Copy all registered files into the profile's storage. Returns profile name used."""
    config = load_config(root)
    target = profile or config.current_profile
    if target is None:
        raise NoActiveProfileError(
            "No active profile. Specify a profile with --profile or run 'regiswitch profile create'."
        )
    profile_dir = RegiswitchConfig.profile_dir(root, target)
    if not profile_dir.exists():
        raise ProfileNotFoundError(f"Profile '{target}' does not exist.")
    for rel_path in config.registered_files:
        src = root / rel_path
        if src.exists():
            copy_file_to_profile(root, rel_path, target)
    return target


def switch_profile(root: Path, name: str) -> list[str]:
    """Replace registered files with versions from the named profile. Returns applied files."""
    config = load_config(root)
    profile_dir = RegiswitchConfig.profile_dir(root, name)
    if not profile_dir.exists():
        raise ProfileNotFoundError(f"Profile '{name}' does not exist.")
    applied: list[str] = []
    for rel_path in config.registered_files:
        if profile_has_file(root, rel_path, name):
            copy_file_from_profile(root, rel_path, name)
            applied.append(rel_path)
    config.current_profile = name
    save_config(root, config)
    return applied


def get_status(root: Path) -> StatusResult:
    """Collect current project state for display."""
    config = load_config(root)
    profiles = list_profiles(root)
    drift: list[str] = []
    if config.current_profile:
        for rel_path in config.registered_files:
            stored = RegiswitchConfig.profile_dir(root, config.current_profile) / rel_path
            working = root / rel_path
            if working.exists() and stored.exists():
                if working.read_bytes() != stored.read_bytes():
                    drift.append(rel_path)
            elif working.exists() and not stored.exists():
                drift.append(rel_path)
    return StatusResult(
        root=root,
        current_profile=config.current_profile,
        profiles=profiles,
        registered_files=config.registered_files,
        drift=drift,
    )
