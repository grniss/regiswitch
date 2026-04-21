from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from regiswitch.core.backends.base import StorageBackend
from regiswitch.core.backends.local import LocalBackend
from regiswitch.utils.errors import RegiswitchError

_BOOTSTRAP_CONFIG = Path.home() / ".config" / "regiswitch" / "backend.toml"


def get_backend() -> StorageBackend:
    if not _BOOTSTRAP_CONFIG.exists():
        return LocalBackend()
    with _BOOTSTRAP_CONFIG.open("rb") as f:
        data = tomllib.load(f)
    backend_type = data.get("type", "local")
    if backend_type == "local":
        path = data.get("path")
        return LocalBackend(Path(path) if path else None)
    if backend_type == "s3":
        from regiswitch.core.backends.s3 import S3Backend
        return S3Backend(
            bucket=data["bucket"],
            prefix=data.get("prefix", "regiswitch/"),
            region=data.get("region"),
        )
    raise RegiswitchError(f"Unknown backend type: '{backend_type}'")


def write_backend_config(config: dict) -> None:
    _BOOTSTRAP_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with _BOOTSTRAP_CONFIG.open("wb") as f:
        tomli_w.dump(config, f)


def read_backend_config() -> dict:
    if not _BOOTSTRAP_CONFIG.exists():
        return {"type": "local", "path": None}
    with _BOOTSTRAP_CONFIG.open("rb") as f:
        return tomllib.load(f)
