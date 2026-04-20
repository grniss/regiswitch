import pytest
import boto3
from moto import mock_aws
from pathlib import Path

from regiswitch.store import LocalStore, S3Store, build_store


# ------------------------------------------------------------------ fixtures

@pytest.fixture
def local(tmp_path):
    return LocalStore(tmp_path / "store")


@pytest.fixture
def s3_store():
    with mock_aws():
        boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
        yield S3Store("test-bucket", prefix="rs/", region="us-east-1")


# ================================================================== LocalStore


class TestLocalStore:
    def test_put_returns_sha256(self, local):
        sha = local.put(b"hello")
        assert len(sha) == 64

    def test_put_deduplicates(self, local):
        sha1 = local.put(b"same")
        sha2 = local.put(b"same")
        assert sha1 == sha2
        blobs = [b for b in (local._dir).rglob("*") if b.is_file()]
        assert len(blobs) == 1

    def test_get_roundtrip(self, local):
        data = b"roundtrip data"
        sha = local.put(data)
        assert local.get(sha) == data

    def test_exists_true(self, local):
        sha = local.put(b"x")
        assert local.exists(sha)

    def test_exists_false(self, local):
        assert not local.exists("a" * 64)

    def test_delete(self, local):
        sha = local.put(b"delete me")
        local.delete(sha)
        assert not local.exists(sha)

    def test_delete_removes_empty_prefix_dir(self, local):
        sha = local.put(b"lonely")
        prefix_dir = local._path(sha).parent
        local.delete(sha)
        assert not prefix_dir.exists()

    def test_delete_nonexistent_noop(self, local):
        local.delete("b" * 64)  # no error

    def test_list_all_empty(self, local):
        assert local.list_all() == []

    def test_list_all(self, local):
        sha1 = local.put(b"one")
        sha2 = local.put(b"two")
        assert set(local.list_all()) == {sha1, sha2}


# ================================================================== S3Store


class TestS3Store:
    def test_put_returns_sha256(self, s3_store):
        sha = s3_store.put(b"hello")
        assert len(sha) == 64

    def test_put_deduplicates(self, s3_store):
        sha1 = s3_store.put(b"same")
        sha2 = s3_store.put(b"same")
        assert sha1 == sha2

    def test_get_roundtrip(self, s3_store):
        data = b"s3 roundtrip"
        sha = s3_store.put(data)
        assert s3_store.get(sha) == data

    def test_exists_true(self, s3_store):
        sha = s3_store.put(b"exists")
        assert s3_store.exists(sha)

    def test_exists_false(self, s3_store):
        assert not s3_store.exists("c" * 64)

    def test_delete(self, s3_store):
        sha = s3_store.put(b"remove")
        s3_store.delete(sha)
        assert not s3_store.exists(sha)

    def test_list_all_empty(self, s3_store):
        assert s3_store.list_all() == []

    def test_list_all(self, s3_store):
        sha1 = s3_store.put(b"alpha")
        sha2 = s3_store.put(b"beta")
        assert set(s3_store.list_all()) == {sha1, sha2}

    def test_key_uses_prefix(self, s3_store):
        sha = s3_store.put(b"prefix check")
        key = s3_store._key(sha)
        assert key.startswith("rs/")


# ================================================================== migrate


class TestMigrate:
    def test_local_to_s3(self, local, s3_store):
        sha1 = local.put(b"file a")
        sha2 = local.put(b"file b")
        count = local.migrate_to(s3_store)
        assert count == 2
        assert s3_store.exists(sha1)
        assert s3_store.exists(sha2)

    def test_migrate_skips_existing(self, local, s3_store):
        data = b"already there"
        sha = local.put(data)
        s3_store.put(data)  # pre-populate
        count = local.migrate_to(s3_store)
        assert count == 0

    def test_s3_to_local(self, local, s3_store):
        sha = s3_store.put(b"from s3")
        s3_store.migrate_to(local)
        assert local.exists(sha)
        assert local.get(sha) == b"from s3"


# ================================================================== build_store


class TestBuildStore:
    def test_build_local(self, tmp_path):
        s = build_store({"type": "local"}, tmp_path / "store")
        assert isinstance(s, LocalStore)

    def test_build_s3(self):
        with mock_aws():
            boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bkt")
            s = build_store({"type": "s3", "bucket": "test-bkt", "region": "us-east-1"}, Path("/unused"))
            assert isinstance(s, S3Store)

    def test_build_unknown_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Unknown store type"):
            build_store({"type": "gcs"}, tmp_path)
