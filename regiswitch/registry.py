import json
import os
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _default_config() -> dict:
    return {"current_profile": None, "profiles": {}, "files": []}


class Registry:
    """
    Profiles store manifests: { file_path: sha256 }.
    Blobs live in a shared content-addressable store: base/store/<sha[:2]>/<sha[2:]>.
    Identical content is stored once across all profiles.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            env = os.environ.get("REGISWITCH_DIR")
            base_dir = Path(env) if env else Path.home() / ".regiswitch"
        self._base = base_dir
        self._config_file = self._base / "config.json"
        self._blob_dir = self._base / "store"

        if self._config_file.exists():
            self._cfg = json.loads(self._config_file.read_text())
        else:
            self._cfg = _default_config()

    # ------------------------------------------------------------------ persist

    def _save(self):
        self._base.mkdir(parents=True, exist_ok=True)
        self._config_file.write_text(json.dumps(self._cfg, indent=2))

    # ------------------------------------------------------------------ blobs

    def _blob_path(self, sha256: str) -> Path:
        return self._blob_dir / sha256[:2] / sha256[2:]

    def _store_blob(self, file_path: str) -> str:
        data = Path(file_path).read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        blob = self._blob_path(sha256)
        if not blob.exists():
            blob.parent.mkdir(parents=True, exist_ok=True)
            blob.write_bytes(data)
        return sha256

    def _restore_blob(self, sha256: str, dest: str):
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self._blob_path(sha256), dest)

    def _gc(self):
        """Remove blobs unreferenced by any profile manifest."""
        referenced = {sha for m in self.profiles.values() for sha in m.values()}
        if not self._blob_dir.exists():
            return
        for prefix_dir in list(self._blob_dir.iterdir()):
            for blob in list(prefix_dir.iterdir()):
                if (prefix_dir.name + blob.name) not in referenced:
                    blob.unlink()
            if not any(prefix_dir.iterdir()):
                prefix_dir.rmdir()

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

        sha256 = self._store_blob(target)
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
                sha256 = self._store_blob(fp)
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
            self._restore_blob(sha256, fp)
            applied.append(fp)

        self._cfg["current_profile"] = profile
        self._save()
        return applied, missing

    # ------------------------------------------------------------------ query

    def has_stored(self, profile: str, file_path: str) -> bool:
        return file_path in self.profiles.get(profile, {})

    def stored_sha(self, profile: str, file_path: str) -> Optional[str]:
        return self.profiles.get(profile, {}).get(file_path)
