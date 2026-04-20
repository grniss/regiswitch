from pathlib import Path
from pydantic import BaseModel, field_validator


class RegiswitchConfig(BaseModel):
    active_profile: str | None = None
    registered_files: list[str] = []

    @field_validator("registered_files")
    @classmethod
    def deduplicate(cls, v: list[str]) -> list[str]:
        seen: dict[str, None] = {}
        for item in v:
            seen[item] = None
        return list(seen)

    def add_file(self, path: Path) -> bool:
        key = str(path)
        if key in self.registered_files:
            return False
        self.registered_files.append(key)
        return True

    def remove_file(self, path: Path) -> bool:
        key = str(path)
        if key not in self.registered_files:
            return False
        self.registered_files.remove(key)
        return True
