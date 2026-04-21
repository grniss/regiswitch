import io
import pytest
from pathlib import Path

boto3 = pytest.importorskip("boto3")
moto = pytest.importorskip("moto")

from moto import mock_aws

from regiswitch.core.backends.s3 import S3Backend
from regiswitch.utils.errors import RegistryNotInitializedError

BUCKET = "test-regiswitch"
PREFIX = "test/"


@pytest.fixture
def s3_backend(tmp_path: Path):
    with mock_aws():
        import boto3 as _boto3
        _boto3.client("s3", region_name="us-east-1").create_bucket(Bucket=BUCKET)
        b = S3Backend(bucket=BUCKET, prefix=PREFIX, region="us-east-1")
        yield b


class TestS3Backend:
    def test_is_initialized_false(self, s3_backend: S3Backend):
        assert s3_backend.is_initialized() is False

    def test_init_and_is_initialized(self, s3_backend: S3Backend):
        s3_backend.init()
        assert s3_backend.is_initialized() is True

    def test_load_registry_raises_before_init(self, s3_backend: S3Backend):
        with pytest.raises(RegistryNotInitializedError):
            s3_backend.load_registry()

    def test_save_and_load_roundtrip(self, s3_backend: S3Backend):
        s3_backend.init()
        registry = s3_backend.load_registry()
        registry.current_profile = "work"
        from regiswitch.models.config import ProfileMeta
        from datetime import datetime
        registry.profiles["work"] = ProfileMeta(created_at=datetime(2026, 1, 1))
        s3_backend.save_registry(registry)
        loaded = s3_backend.load_registry()
        assert loaded.current_profile == "work"

    def test_copy_to_profile_and_has_stored_version(self, s3_backend: S3Backend, tmp_path: Path):
        s3_backend.init()
        src = tmp_path / "file.txt"
        src.write_text("content")
        assert s3_backend.has_stored_version("work", src) is False
        s3_backend.copy_to_profile(src, "work")
        assert s3_backend.has_stored_version("work", src) is True

    def test_restore_from_profile(self, s3_backend: S3Backend, tmp_path: Path):
        s3_backend.init()
        src = tmp_path / "file.txt"
        src.write_text("original")
        s3_backend.copy_to_profile(src, "work")
        src.write_text("modified")
        s3_backend.restore_from_profile("work", src)
        assert src.read_text() == "original"

    def test_delete_profile(self, s3_backend: S3Backend, tmp_path: Path):
        s3_backend.init()
        src = tmp_path / "file.txt"
        src.write_text("data")
        s3_backend.copy_to_profile(src, "work")
        s3_backend.delete_profile("work")
        assert s3_backend.has_stored_version("work", src) is False
