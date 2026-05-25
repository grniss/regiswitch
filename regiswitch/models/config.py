from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


REGISWITCH_DIR = ".regiswitch"
CONFIG_FILE = "config.toml"
PROFILES_DIR = "profiles"


class LocalStorageConfig(BaseModel):
    type: Literal["local"] = "local"
    path: str | None = None  # None = default .regiswitch/profiles/


class S3StorageConfig(BaseModel):
    type: Literal["s3"] = "s3"
    bucket: str
    prefix: str = ""
    region: str = "us-east-1"


StorageConfig = Annotated[
    Union[LocalStorageConfig, S3StorageConfig],
    Field(discriminator="type"),
]


class RegiswitchConfig(BaseModel):
    """Stored in .regiswitch/config.toml."""

    current_profile: str | None = None
    registered_files: list[str] = Field(default_factory=list)
    storage: StorageConfig = Field(default_factory=LocalStorageConfig)

    @classmethod
    def config_path(cls, root: Path) -> Path:
        return root / REGISWITCH_DIR / CONFIG_FILE

    @classmethod
    def default_profiles_dir(cls, root: Path) -> Path:
        return root / REGISWITCH_DIR / PROFILES_DIR
