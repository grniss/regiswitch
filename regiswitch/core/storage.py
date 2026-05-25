from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from regiswitch.models.config import LocalStorageConfig, S3StorageConfig, StorageConfig


class StorageBackend(ABC):
    """Abstract interface for profile file storage."""

    @abstractmethod
    def put_file(self, src: Path, rel_path: str, profile: str) -> None:
        """Copy src into storage under the given profile."""

    @abstractmethod
    def get_file(self, dest: Path, rel_path: str, profile: str) -> None:
        """Restore rel_path from storage into dest."""

    @abstractmethod
    def has_file(self, rel_path: str, profile: str) -> bool:
        """Return True if the profile has a stored copy of rel_path."""

    @abstractmethod
    def profile_exists(self, profile: str) -> bool:
        """Return True if the profile has been created."""

    @abstractmethod
    def create_profile(self, profile: str) -> None:
        """Create storage space for a profile."""

    @abstractmethod
    def delete_profile(self, profile: str) -> None:
        """Delete all stored files for a profile."""

    @abstractmethod
    def list_profiles(self) -> list[str]:
        """Return sorted list of existing profile names."""


class LocalStorageBackend(StorageBackend):
    """Stores profile files on the local filesystem."""

    def __init__(self, base_path: Path) -> None:
        self._base = base_path

    def _profile_dir(self, profile: str) -> Path:
        return self._base / profile

    def _file_path(self, rel_path: str, profile: str) -> Path:
        return self._profile_dir(profile) / rel_path

    def put_file(self, src: Path, rel_path: str, profile: str) -> None:
        dest = self._file_path(rel_path, profile)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    def get_file(self, dest: Path, rel_path: str, profile: str) -> None:
        src = self._file_path(rel_path, profile)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    def has_file(self, rel_path: str, profile: str) -> bool:
        return self._file_path(rel_path, profile).exists()

    def profile_exists(self, profile: str) -> bool:
        return self._profile_dir(profile).exists()

    def create_profile(self, profile: str) -> None:
        self._profile_dir(profile).mkdir(parents=True, exist_ok=True)

    def delete_profile(self, profile: str) -> None:
        shutil.rmtree(self._profile_dir(profile))

    def list_profiles(self) -> list[str]:
        if not self._base.exists():
            return []
        return sorted(p.name for p in self._base.iterdir() if p.is_dir())


class S3StorageBackend(StorageBackend):
    """Stores profile files in an S3 bucket using the ambient boto3 session."""

    def __init__(self, bucket: str, prefix: str = "", region: str = "us-east-1") -> None:
        self._bucket = bucket
        self._prefix = prefix.rstrip("/")
        self._region = region
        self.__client = None

    @property
    def _client(self):
        if self.__client is None:
            try:
                import boto3
            except ImportError as exc:
                raise ImportError(
                    "boto3 is required for S3 storage. "
                    "Install it with: pip install regiswitch[s3]"
                ) from exc
            self.__client = boto3.client("s3", region_name=self._region)
        return self.__client

    def _key(self, rel_path: str, profile: str) -> str:
        parts = [p for p in [self._prefix, profile, rel_path] if p]
        return "/".join(parts)

    def _profile_prefix(self, profile: str) -> str:
        parts = [p for p in [self._prefix, profile] if p]
        return "/".join(parts) + "/"

    def put_file(self, src: Path, rel_path: str, profile: str) -> None:
        self._client.upload_file(str(src), self._bucket, self._key(rel_path, profile))

    def get_file(self, dest: Path, rel_path: str, profile: str) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        self._client.download_file(self._bucket, self._key(rel_path, profile), str(dest))

    def has_file(self, rel_path: str, profile: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=self._key(rel_path, profile))
            return True
        except self._client.exceptions.ClientError:
            return False

    def profile_exists(self, profile: str) -> bool:
        resp = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=self._profile_prefix(profile),
            MaxKeys=1,
        )
        return resp.get("KeyCount", 0) > 0 or self._profile_dir_marker_exists(profile)

    def _profile_dir_marker_exists(self, profile: str) -> bool:
        marker = self._profile_prefix(profile)
        try:
            self._client.head_object(Bucket=self._bucket, Key=marker)
            return True
        except Exception:
            return False

    def create_profile(self, profile: str) -> None:
        marker = self._profile_prefix(profile)
        self._client.put_object(Bucket=self._bucket, Key=marker, Body=b"")

    def delete_profile(self, profile: str) -> None:
        prefix = self._profile_prefix(profile)
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
            objects = [{"Key": obj["Key"]} for obj in page.get("Contents", [])]
            if objects:
                self._client.delete_objects(
                    Bucket=self._bucket, Delete={"Objects": objects}
                )

    def list_profiles(self) -> list[str]:
        base_prefix = (self._prefix + "/") if self._prefix else ""
        resp = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=base_prefix,
            Delimiter="/",
        )
        profiles = []
        for cp in resp.get("CommonPrefixes", []):
            name = cp["Prefix"].removeprefix(base_prefix).rstrip("/")
            if name:
                profiles.append(name)
        return sorted(profiles)


def build_storage_backend(config: StorageConfig, root: Path) -> StorageBackend:
    """Construct the appropriate backend from a storage config."""
    if isinstance(config, S3StorageConfig):
        return S3StorageBackend(
            bucket=config.bucket,
            prefix=config.prefix,
            region=config.region,
        )
    # LocalStorageConfig
    base = Path(config.path) if config.path else root / ".regiswitch" / "profiles"
    return LocalStorageBackend(base)
