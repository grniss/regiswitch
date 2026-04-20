from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from regiswitch.core.storage import StorageBackend, build_storage_backend
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


def _strip_none(obj: Any) -> Any:
    """Recursively remove None values so tomli_w can serialize the dict."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj]
    return obj


def save_config(root: Path, config: RegiswitchConfig) -> None:
    """Persist RegiswitchConfig to config.toml."""
    path = RegiswitchConfig.config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _strip_none(config.model_dump())
    with path.open("wb") as f:
        tomli_w.dump(data, f)


def load_storage_backend(root: Path) -> StorageBackend:
    """Load config and construct the configured storage backend."""
    config = load_config(root)
    return build_storage_backend(config.storage, root)
