import hashlib
import shutil
import tomllib
from pathlib import Path

import tomli_w

from regiswitch.models.config import RegiswitchConfig

CONFIG_DIR = Path.home() / ".config" / "regiswitch"
CONFIG_FILE = CONFIG_DIR / "config.toml"
PROFILES_DIR = CONFIG_DIR / "profiles"


def _encode_path(path: Path) -> str:
    """Return a filesystem-safe name for a registered file path."""
    digest = hashlib.sha1(str(path).encode()).hexdigest()[:8]
    safe = str(path).replace("/", "_").replace("\\", "_").lstrip("_")
    return f"{safe}__{digest}"


def profile_dir(profile: str) -> Path:
    return PROFILES_DIR / profile


def stored_file_path(profile: str, target: Path) -> Path:
    return profile_dir(profile) / _encode_path(target)


def load_config() -> RegiswitchConfig:
    if not CONFIG_FILE.exists():
        return RegiswitchConfig()
    with CONFIG_FILE.open("rb") as fh:
        data = tomllib.load(fh)
    return RegiswitchConfig(**data)


def save_config(config: RegiswitchConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("wb") as fh:
        tomli_w.dump(config.model_dump(exclude_none=True), fh)


def list_profiles() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.name for p in PROFILES_DIR.iterdir() if p.is_dir())


def create_profile(name: str) -> None:
    profile_dir(name).mkdir(parents=True, exist_ok=True)


def delete_profile(name: str) -> None:
    d = profile_dir(name)
    if d.exists():
        shutil.rmtree(d)


def snapshot_file(profile: str, target: Path) -> None:
    """Copy the live target file into the profile store."""
    dest = stored_file_path(profile, target)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, dest)


def restore_file(profile: str, target: Path) -> None:
    """Copy the stored profile version to the live target path."""
    src = stored_file_path(profile, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)


def stored_file_exists(profile: str, target: Path) -> bool:
    return stored_file_path(profile, target).exists()
