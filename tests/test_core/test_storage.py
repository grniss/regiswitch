from pathlib import Path

import pytest

from regiswitch.core.storage import LocalStorageBackend, build_storage_backend
from regiswitch.models.config import LocalStorageConfig, S3StorageConfig


class TestLocalStorageBackend:
    def test_create_and_exists(self, tmp_path: Path):
        storage = LocalStorageBackend(tmp_path / "profiles")
        storage.create_profile("dev")
        assert storage.profile_exists("dev")

    def test_not_exists(self, tmp_path: Path):
        storage = LocalStorageBackend(tmp_path / "profiles")
        assert not storage.profile_exists("dev")

    def test_put_and_has_file(self, tmp_path: Path):
        profiles = tmp_path / "profiles"
        storage = LocalStorageBackend(profiles)
        storage.create_profile("dev")
        src = tmp_path / ".env"
        src.write_text("K=V")
        storage.put_file(src, ".env", "dev")
        assert storage.has_file(".env", "dev")

    def test_has_file_false_when_missing(self, tmp_path: Path):
        storage = LocalStorageBackend(tmp_path / "profiles")
        storage.create_profile("dev")
        assert not storage.has_file(".env", "dev")

    def test_get_file_restores_content(self, tmp_path: Path):
        profiles = tmp_path / "profiles"
        storage = LocalStorageBackend(profiles)
        storage.create_profile("dev")
        src = tmp_path / ".env"
        src.write_text("K=original")
        storage.put_file(src, ".env", "dev")
        src.write_text("K=changed")
        dest = tmp_path / ".env"
        storage.get_file(dest, ".env", "dev")
        assert dest.read_text() == "K=original"

    def test_delete_profile(self, tmp_path: Path):
        storage = LocalStorageBackend(tmp_path / "profiles")
        storage.create_profile("dev")
        storage.delete_profile("dev")
        assert not storage.profile_exists("dev")

    def test_list_profiles_empty(self, tmp_path: Path):
        storage = LocalStorageBackend(tmp_path / "profiles")
        assert storage.list_profiles() == []

    def test_list_profiles_sorted(self, tmp_path: Path):
        storage = LocalStorageBackend(tmp_path / "profiles")
        storage.create_profile("prod")
        storage.create_profile("dev")
        storage.create_profile("staging")
        assert storage.list_profiles() == ["dev", "prod", "staging"]

    def test_nested_file_path(self, tmp_path: Path):
        profiles = tmp_path / "profiles"
        storage = LocalStorageBackend(profiles)
        storage.create_profile("dev")
        src = tmp_path / "config" / "app.toml"
        src.parent.mkdir()
        src.write_text("key = 1")
        storage.put_file(src, "config/app.toml", "dev")
        assert storage.has_file("config/app.toml", "dev")


class TestBuildStorageBackend:
    def test_local_default_path(self, tmp_path: Path):
        config = LocalStorageConfig()
        backend = build_storage_backend(config, tmp_path)
        assert isinstance(backend, LocalStorageBackend)

    def test_local_custom_path(self, tmp_path: Path):
        custom = tmp_path / "custom_store"
        config = LocalStorageConfig(path=str(custom))
        backend = build_storage_backend(config, tmp_path)
        assert isinstance(backend, LocalStorageBackend)
        backend.create_profile("dev")
        assert (custom / "dev").exists()

    def test_s3_returns_s3_backend(self, tmp_path: Path):
        from regiswitch.core.storage import S3StorageBackend
        config = S3StorageConfig(bucket="my-bucket", prefix="proj", region="us-east-1")
        backend = build_storage_backend(config, tmp_path)
        assert isinstance(backend, S3StorageBackend)
