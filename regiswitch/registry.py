import json
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional

CONFIG_DIR = Path.home() / ".regiswitch"
CONFIG_FILE = CONFIG_DIR / "config.json"
STORE_DIR = CONFIG_DIR / "profiles"


def _store_path(profile: str, file_path: str) -> Path:
    # Unique filename: short hash of full path + original basename
    digest = hashlib.sha256(file_path.encode()).hexdigest()[:12]
    name = f"{digest}_{Path(file_path).name}"
    return STORE_DIR / profile / name


def _default_config() -> dict:
    return {"current_profile": None, "profiles": {}, "files": []}


class Registry:
    def __init__(self):
        if CONFIG_FILE.exists():
            self._cfg = json.loads(CONFIG_FILE.read_text())
        else:
            self._cfg = _default_config()

    def _save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self._cfg, indent=2))

    # ------------------------------------------------------------------ props

    @property
    def current_profile(self) -> Optional[str]:
        return self._cfg.get("current_profile")

    @property
    def profiles(self) -> dict:
        return self._cfg.setdefault("profiles", {})

    @property
    def files(self) -> List[str]:
        return self._cfg.setdefault("files", [])

    # ---------------------------------------------------------- profile ops

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
        store = STORE_DIR / name
        if store.exists():
            shutil.rmtree(store)
        del self.profiles[name]
        if self.current_profile == name:
            self._cfg["current_profile"] = next(iter(self.profiles), None)
        self._save()

    # ---------------------------------------------------------- file ops

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

        self._copy_to_store(profile, target)
        self._save()

    def unregister(self, file_path: str):
        target = str(Path(file_path).resolve())
        if target in self.files:
            self.files.remove(target)
            for profile in self.profiles:
                sp = _store_path(profile, target)
                if sp.exists():
                    sp.unlink()
        self._save()

    def snapshot(self, profile: Optional[str] = None):
        profile = profile or self.current_profile
        if not profile:
            raise ValueError("No active profile")
        if profile not in self.profiles:
            raise ValueError(f"Profile '{profile}' does not exist")

        saved = []
        for fp in self.files:
            if Path(fp).exists():
                self._copy_to_store(profile, fp)
                saved.append(fp)
        self._save()
        return saved

    def switch(self, profile: str, force: bool = False):
        if profile not in self.profiles:
            raise ValueError(f"Profile '{profile}' does not exist")

        missing = [fp for fp in self.files if not _store_path(profile, fp).exists()]
        if missing and not force:
            raise ValueError(
                f"Profile '{profile}' has no stored version for:\n"
                + "\n".join(f"  {f}" for f in missing)
                + "\nRun with --force to skip missing, or snapshot first."
            )

        applied = []
        for fp in self.files:
            sp = _store_path(profile, fp)
            if not sp.exists():
                continue
            Path(fp).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sp, fp)
            applied.append(fp)

        self._cfg["current_profile"] = profile
        self._save()
        return applied, missing

    # ---------------------------------------------------------- helpers

    def _copy_to_store(self, profile: str, file_path: str):
        sp = _store_path(profile, file_path)
        sp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, sp)

    def has_stored(self, profile: str, file_path: str) -> bool:
        return _store_path(profile, file_path).exists()
