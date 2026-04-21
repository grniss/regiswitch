from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from regiswitch.models.config import Registry, ProfileMeta, RegisteredFile
from regiswitch.utils.fs import REGISTRY_FILE, CONFIG_DIR, PROFILES_DIR


def load_registry() -> Registry:
    if not REGISTRY_FILE.exists():
        from regiswitch.utils.errors import RegistryNotInitializedError
        raise RegistryNotInitializedError(
            "Registry not initialized. Run `regiswitch init` first."
        )
    with REGISTRY_FILE.open("rb") as f:
        data = tomllib.load(f)
    if data.get("current_profile") == "":
        data["current_profile"] = None
    return Registry.model_validate(data)


def save_registry(registry: Registry) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    raw: dict = {
        "current_profile": registry.current_profile or "",
        "profiles": {
            name: {"created_at": meta.created_at.isoformat()}
            for name, meta in registry.profiles.items()
        },
        "files": {
            path: {"path": rf.path, "registered_at": rf.registered_at.isoformat()}
            for path, rf in registry.files.items()
        },
    }
    with REGISTRY_FILE.open("wb") as f:
        tomli_w.dump(raw, f)


def init_registry() -> Registry:
    registry = Registry()
    save_registry(registry)
    return registry


def is_initialized() -> bool:
    return REGISTRY_FILE.exists()
