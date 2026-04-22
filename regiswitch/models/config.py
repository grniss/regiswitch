from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, field_validator


class ProfileMeta(BaseModel):
    created_at: datetime = datetime.now()


class RegisteredFile(BaseModel):
    path: str
    registered_at: datetime = datetime.now()

    @field_validator("path")
    @classmethod
    def must_be_absolute(cls, v: str) -> str:
        if not Path(v).is_absolute():
            raise ValueError(f"path must be absolute, got: {v}")
        return v


class Registry(BaseModel):
    current_profile: Optional[str] = None
    profiles: dict[str, ProfileMeta] = {}
    files: dict[str, RegisteredFile] = {}
    auto_save: bool = False
