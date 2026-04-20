import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from regiswitch.store import Store, LocalStore, build_store


def _default_config() -> dict:
    return {
        "current_profile": None,
        "profiles": {},
        "files": [],
        "store": {"type": "local"},
    }


class Registry:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            env = os.environ.get("REGISWITCH_DIR")
            base_dir = Path(env) if env else Path.home() / ".regiswitch"
        self._base = base_dir
        self._config_file = self._base / "config.json"

        if self._config_file.exists():
            self._cfg = json.loads(self._config_file.read_text())
        else:
            self._cfg = _default_config()

        self._store: Store = build_store(
            self._cfg.get("store", {"type": "local"}),
            self._base / "store",
        )

    # ------------------------------------------------------------------ persist

    def _save(self):
        self._base.mkdir(parents=True, exist_ok=True)
        self._config_file.write_text(json.dumps(self._cfg, indent=2))

    # ------------------------------------------------------------------ gc

    def _gc(self):
        referenced = {sha for m in self.profiles.values() for sha in m.values()}
        for sha256 in list(self._store.list_all()):
            if sha256 not in referenced:
                self._store.delete(sha256)

    # ------------------------------------------------------------------ props

    @property
    def current_profile(self) -> Optional[str]:
        return self._cfg.get("current_profile")

    @property
    def profiles(self) -> Dict[str, Dict[str, str]]:
        return self._cfg.setdefault("profiles", {})

    @property
    def files(self) -> List[str]:
        return self._cfg.setdefault("files", [])

    @property
    def store_config(self) -> dict:
        return self._cfg.get("store", {"type": "local"})

    # ------------------------------------------------------------------ profile

    def profile_add(self, name: str):
        if name in self.profiles:
            raise ValueError(f"Profile '{name}' already exists")
        self.profiles[name] = {}
        if self.current_profile is None:
            self._cfg["current_profile"] = name
        self._save()

    def profile_remove(self, name: str):
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' does not exist")
        del self.profiles[name]
        if self.current_profile == name:
            self._cfg["current_profile"] = next(iter(self.profiles), None)
        self._gc()
        self._save()

    # ------------------------------------------------------------------ files

    def register(self, file_path: str, profile: Optional[str] = None):
        target = str(Path(file_path).resolve())
        if not Path(target).exists():
            raise FileNotFoundError(f"File not found: {target}")

        profile = profile or self.current_profile
        if not profile:
            raise ValueError("No active profile. Run: regiswitch profile add <name>")
        if profile not in self.profiles:
            raise ValueError(f"Profile '{profile}' does not exist")

        if target not in self.files:
            self.files.append(target)

        sha256 = self._store.put(Path(target).read_bytes())
        self.profiles[profile][target] = sha256
        self._save()

    def unregister(self, file_path: str):
        target = str(Path(file_path).resolve())
        if target in self.files:
            self.files.remove(target)
            for manifest in self.profiles.values():
                manifest.pop(target, None)
        self._gc()
        self._save()

    def snapshot(self, profile: Optional[str] = None) -> List[str]:
        profile = profile or self.current_profile
        if not profile:
            raise ValueError("No active profile")
        if profile not in self.profiles:
            raise ValueError(f"Profile '{profile}' does not exist")

        saved = []
        for fp in self.files:
            if Path(fp).exists():
                sha256 = self._store.put(Path(fp).read_bytes())
                self.profiles[profile][fp] = sha256
                saved.append(fp)
        self._save()
        return saved

    def switch(self, profile: str, force: bool = False) -> Tuple[List[str], List[str]]:
        if profile not in self.profiles:
            raise ValueError(f"Profile '{profile}' does not exist")

        manifest = self.profiles[profile]
        missing = [fp for fp in self.files if fp not in manifest]
        if missing and not force:
            raise ValueError(
                f"Profile '{profile}' has no stored version for:\n"
                + "\n".join(f"  {f}" for f in missing)
                + "\nRun with --force to skip missing, or snapshot first."
            )

        applied = []
        for fp in self.files:
            sha256 = manifest.get(fp)
            if sha256 is None:
                continue
            Path(fp).parent.mkdir(parents=True, exist_ok=True)
            Path(fp).write_bytes(self._store.get(sha256))
            applied.append(fp)

        self._cfg["current_profile"] = profile
        self._save()
        return applied, missing

    # ------------------------------------------------------------------ store management

    def set_store(self, store_cfg: dict, migrate: bool = False) -> int:
        """
        Reconfigure the backend store. If migrate=True, transfers all existing
        blobs to the new store before switching. Returns count of blobs migrated.
        """
        new_store = build_store(store_cfg, self._base / "store")
        migrated = 0
        if migrate:
            migrated = self._store.migrate_to(new_store)
        self._cfg["store"] = store_cfg
        self._store = new_store
        self._save()
        return migrated

    # ------------------------------------------------------------------ query

    def has_stored(self, profile: str, file_path: str) -> bool:
        return file_path in self.profiles.get(profile, {})

    def stored_sha(self, profile: str, file_path: str) -> Optional[str]:
        return self.profiles.get(profile, {}).get(file_path)
