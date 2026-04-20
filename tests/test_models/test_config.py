from pathlib import Path

from regiswitch.models.config import RegiswitchConfig, REGISWITCH_DIR, CONFIG_FILE, PROFILES_DIR


def test_config_defaults():
    config = RegiswitchConfig()
    assert config.current_profile is None
    assert config.registered_files == []


def test_config_path(tmp_path: Path):
    expected = tmp_path / REGISWITCH_DIR / CONFIG_FILE
    assert RegiswitchConfig.config_path(tmp_path) == expected


def test_profiles_dir(tmp_path: Path):
    expected = tmp_path / REGISWITCH_DIR / PROFILES_DIR
    assert RegiswitchConfig.profiles_dir(tmp_path) == expected


def test_profile_dir(tmp_path: Path):
    expected = tmp_path / REGISWITCH_DIR / PROFILES_DIR / "dev"
    assert RegiswitchConfig.profile_dir(tmp_path, "dev") == expected


def test_config_roundtrip():
    config = RegiswitchConfig(current_profile="dev", registered_files=[".env", "config.toml"])
    dumped = config.model_dump()
    restored = RegiswitchConfig(**dumped)
    assert restored == config
