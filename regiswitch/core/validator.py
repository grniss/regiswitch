from __future__ import annotations

from pathlib import Path

from regiswitch.utils.errors import RegiswitchError


def validate_file_exists(root: Path, rel_path: str) -> None:
    """Raise if the file does not exist on disk."""
    full = root / rel_path
    if not full.exists():
        raise RegiswitchError(f"File not found: {full}")


def validate_profile_name(name: str) -> None:
    """Raise if the profile name contains invalid characters."""
    if not name.strip():
        raise RegiswitchError("Profile name cannot be empty.")
    invalid = set(r'/\:*?"<>|')
    bad = invalid.intersection(name)
    if bad:
        raise RegiswitchError(
            f"Profile name '{name}' contains invalid characters: {', '.join(sorted(bad))}"
        )


def validate_rel_path(rel_path: str) -> None:
    """Raise if the path looks absolute or tries to escape the project root."""
    p = Path(rel_path)
    if p.is_absolute():
        raise RegiswitchError(f"Path must be relative, got: {rel_path}")
    if ".." in p.parts:
        raise RegiswitchError(f"Path must not escape the project root: {rel_path}")
