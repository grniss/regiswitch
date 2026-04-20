from pathlib import Path

from regiswitch.models.config import (
    LocalStorageConfig,
    RegiswitchConfig,
    S3StorageConfig,
    REGISWITCH_DIR,
    CONFIG_FILE,
)


def test_config_defaults():
    config = RegiswitchConfig()
    assert config.current_profile is None
    assert config.registered_files == []
    assert isinstance(config.storage, LocalStorageConfig)


def test_config_path(tmp_path: Path):
    expected = tmp_path / REGISWITCH_DIR / CONFIG_FILE
    assert RegiswitchConfig.config_path(tmp_path) == expected


def test_default_profiles_dir(tmp_path: Path):
    expected = tmp_path / REGISWITCH_DIR / "profiles"
    assert RegiswitchConfig.default_profiles_dir(tmp_path) == expected


def test_local_storage_default_path():
    storage = LocalStorageConfig()
    assert storage.type == "local"
    assert storage.path is None


def test_local_storage_custom_path():
    storage = LocalStorageConfig(path="/custom/path")
    assert storage.path == "/custom/path"


def test_s3_storage_config():
    storage = S3StorageConfig(bucket="my-bucket", prefix="proj", region="eu-west-1")
    assert storage.type == "s3"
    assert storage.bucket == "my-bucket"
    assert storage.prefix == "proj"
    assert storage.region == "eu-west-1"


def test_s3_storage_defaults():
    storage = S3StorageConfig(bucket="my-bucket")
    assert storage.prefix == ""
    assert storage.region == "us-east-1"


def test_config_roundtrip_local():
    config = RegiswitchConfig(
        current_profile="dev",
        registered_files=[".env"],
        storage=LocalStorageConfig(path="/shared"),
    )
    restored = RegiswitchConfig(**config.model_dump())
    assert restored == config


def test_config_roundtrip_s3():
    config = RegiswitchConfig(
        current_profile="prod",
        registered_files=[".env", "config.toml"],
        storage=S3StorageConfig(bucket="b", prefix="p", region="us-west-2"),
    )
    restored = RegiswitchConfig(**config.model_dump())
    assert restored == config
