from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import tomli_w

from regiswitch.models.config import RegiswitchConfig, REGISWITCH_DIR
from regiswitch.utils.errors import NotInitializedError


def find_project_root(start: Path) -> Path:
    """Walk up from start until .regiswitch/ is found, or raise."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / REGISWITCH_DIR).is_dir():
            return candidate
    raise NotInitializedError(
        f"No .regiswitch/ directory found in {start} or any parent directory. "
        "Run 'regiswitch init' first."
    )


def load_config(root: Path) -> RegiswitchConfig:
    """Read config.toml and return a RegiswitchConfig."""
    path = RegiswitchConfig.config_path(root)
    if not path.exists():
        raise NotInitializedError(f"Config file not found: {path}")
    with path.open("rb") as f:
        data = tomllib.load(f)
    return RegiswitchConfig(**data)


def save_config(root: Path, config: RegiswitchConfig) -> None:
    """Persist RegiswitchConfig to config.toml."""
    path = RegiswitchConfig.config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {k: v for k, v in config.model_dump().items() if v is not None}
    with path.open("wb") as f:
        tomli_w.dump(data, f)


def copy_file_to_profile(root: Path, rel_path: str, profile: str) -> None:
    """Copy a registered file into the profile's storage directory."""
    src = root / rel_path
    dest = RegiswitchConfig.profile_dir(root, profile) / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_file_from_profile(root: Path, rel_path: str, profile: str) -> None:
    """Restore a file from a profile's storage directory to the working tree."""
    src = RegiswitchConfig.profile_dir(root, profile) / rel_path
    dest = root / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def profile_has_file(root: Path, rel_path: str, profile: str) -> bool:
    """Return True if the profile has a stored copy of rel_path."""
    return (RegiswitchConfig.profile_dir(root, profile) / rel_path).exists()
