from pydantic import BaseModel, Field
from typing import Dict, List
from pathlib import Path

class FileMapping(BaseModel):
    target: Path
    source: Path

class Profile(BaseModel):
    name: str
    mappings: List[FileMapping]

class AppConfig(BaseModel):
    profiles: Dict[str, Profile] = Field(default_factory=dict)
    active_profile: str | None = None
