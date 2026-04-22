import shutil
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "regiswitch"
REGISTRY_FILE = CONFIG_DIR / "registry.toml"
PROFILES_DIR = CONFIG_DIR / "profiles"


def encode_path(absolute_path: Path) -> Path:
    """Convert an absolute path to a relative storage path inside a profile dir."""
    return Path(str(absolute_path).lstrip("/"))


def profile_dir(profile_name: str) -> Path:
    return PROFILES_DIR / profile_name


def stored_file_path(profile_name: str, absolute_path: Path) -> Path:
    return profile_dir(profile_name) / encode_path(absolute_path)


def copy_to_profile(src: Path, profile_name: str) -> None:
    dest = stored_file_path(profile_name, src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def restore_from_profile(profile_name: str, absolute_path: Path) -> None:
    src = stored_file_path(profile_name, absolute_path)
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, absolute_path)


def has_stored_version(profile_name: str, absolute_path: Path) -> bool:
    return stored_file_path(profile_name, absolute_path).exists()
