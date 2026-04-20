from pathlib import Path

from regiswitch.models.config import RegiswitchConfig
from regiswitch.utils import fs
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoActiveProfileError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)


def create_profile(name: str) -> None:
    existing = fs.list_profiles()
    if name in existing:
        raise ProfileAlreadyExistsError(name)
    fs.create_profile(name)


def delete_profile(name: str) -> None:
    existing = fs.list_profiles()
    if name not in existing:
        raise ProfileNotFoundError(name)
    config = fs.load_config()
    fs.delete_profile(name)
    if config.active_profile == name:
        config.active_profile = None
        fs.save_config(config)


def list_profiles() -> list[str]:
    return fs.list_profiles()


def register_file(path: Path) -> None:
    path = path.resolve()
    config = fs.load_config()
    if not config.add_file(path):
        raise FileAlreadyRegisteredError(str(path))
    fs.save_config(config)
    # snapshot into every existing profile that doesn't have it yet
    if path.exists():
        for profile in fs.list_profiles():
            if not fs.stored_file_exists(profile, path):
                fs.snapshot_file(profile, path)


def unregister_file(path: Path) -> None:
    path = path.resolve()
    config = fs.load_config()
    if not config.remove_file(path):
        raise FileNotRegisteredError(str(path))
    fs.save_config(config)


def switch_profile(name: str) -> list[str]:
    """Switch to profile, returning list of files that had no stored version."""
    if name not in fs.list_profiles():
        raise ProfileNotFoundError(name)
    config = fs.load_config()
    missing: list[str] = []
    for file_str in config.registered_files:
        target = Path(file_str)
        if fs.stored_file_exists(name, target):
            fs.restore_file(name, target)
        else:
            missing.append(file_str)
    config.active_profile = name
    fs.save_config(config)
    return missing


def snapshot(profile: str | None = None) -> list[str]:
    """Save current live files into a profile. Returns list of missing live files."""
    config = fs.load_config()
    effective = profile or config.active_profile
    if effective is None:
        raise NoActiveProfileError()
    if effective not in fs.list_profiles():
        raise ProfileNotFoundError(effective)
    missing: list[str] = []
    for file_str in config.registered_files:
        target = Path(file_str)
        if target.exists():
            fs.snapshot_file(effective, target)
        else:
            missing.append(file_str)
    return missing


def get_status() -> tuple[str | None, list[dict]]:
    """Return (active_profile, file_status_list)."""
    config = fs.load_config()
    rows: list[dict] = []
    for file_str in config.registered_files:
        target = Path(file_str)
        live = target.exists()
        stored = (
            fs.stored_file_exists(config.active_profile, target)
            if config.active_profile
            else False
        )
        rows.append({"path": file_str, "live": live, "stored": stored})
    return config.active_profile, rows
