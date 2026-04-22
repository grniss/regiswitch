from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import tomli_w

from regiswitch.core.backends.base import StorageBackend
from regiswitch.models.config import Registry
from regiswitch.utils.errors import RegistryNotInitializedError

_DEFAULT_STORAGE = Path.home() / ".config" / "regiswitch"


def _encode_path(absolute_path: Path) -> Path:
    return Path(str(absolute_path).lstrip("/"))


class LocalBackend(StorageBackend):
    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path or _DEFAULT_STORAGE
        self.registry_file = self.storage_path / "registry.toml"
        self.profiles_dir = self.storage_path / "profiles"

    def is_initialized(self) -> bool:
        return self.registry_file.exists()

    def init(self) -> Registry:
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        registry = Registry()
        self.save_registry(registry)
        return registry

    def load_registry(self) -> Registry:
        if not self.registry_file.exists():
            raise RegistryNotInitializedError(
                "Registry not initialized. Run `regiswitch init` first."
            )
        with self.registry_file.open("rb") as f:
            data = tomllib.load(f)
        if data.get("current_profile") == "":
            data["current_profile"] = None
        return Registry.model_validate(data)

    def save_registry(self, registry: Registry) -> None:
        self.storage_path.mkdir(parents=True, exist_ok=True)
        raw: dict = {
            "current_profile": registry.current_profile or "",
            "auto_save": registry.auto_save,
            "profiles": {
                name: {"created_at": meta.created_at.isoformat()}
                for name, meta in registry.profiles.items()
            },
            "files": {
                path: {"path": rf.path, "registered_at": rf.registered_at.isoformat()}
                for path, rf in registry.files.items()
            },
        }
        with self.registry_file.open("wb") as f:
            tomli_w.dump(raw, f)

    def _stored_path(self, profile_name: str, absolute_path: Path) -> Path:
        return self.profiles_dir / profile_name / _encode_path(absolute_path)

    def copy_to_profile(self, src: Path, profile_name: str) -> None:
        dest = self._stored_path(profile_name, src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    def restore_from_profile(self, profile_name: str, absolute_path: Path) -> None:
        src = self._stored_path(profile_name, absolute_path)
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, absolute_path)

    def has_stored_version(self, profile_name: str, absolute_path: Path) -> bool:
        return self._stored_path(profile_name, absolute_path).exists()

    def delete_profile(self, name: str) -> None:
        shutil.rmtree(self.profiles_dir / name, ignore_errors=True)
