from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field


REGISWITCH_DIR = ".regiswitch"
CONFIG_FILE = "config.toml"
PROFILES_DIR = "profiles"


class RegiswitchConfig(BaseModel):
    """Stored in .regiswitch/config.toml."""

    current_profile: str | None = None
    registered_files: list[str] = Field(default_factory=list)

    @classmethod
    def config_path(cls, root: Path) -> Path:
        return root / REGISWITCH_DIR / CONFIG_FILE

    @classmethod
    def profiles_dir(cls, root: Path) -> Path:
        return root / REGISWITCH_DIR / PROFILES_DIR

    @classmethod
    def profile_dir(cls, root: Path, profile: str) -> Path:
        return cls.profiles_dir(root) / profile
