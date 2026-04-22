from __future__ import annotations

import io
import tomllib
from pathlib import Path

import tomli_w

from regiswitch.core.backends.base import StorageBackend
from regiswitch.models.config import Registry
from regiswitch.utils.errors import RegiswitchError, RegistryNotInitializedError


def _encode_path(absolute_path: Path) -> str:
    return str(absolute_path).lstrip("/")


class S3Backend(StorageBackend):
    def __init__(self, bucket: str, prefix: str = "regiswitch/", region: str | None = None) -> None:
        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/"
        self.region = region
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError:
                raise RegiswitchError(
                    "boto3 is required for S3 storage. Install with: pip install regiswitch[s3]"
                )
            kwargs = {}
            if self.region:
                kwargs["region_name"] = self.region
            self._client = boto3.client("s3", **kwargs)
        return self._client

    def _registry_key(self) -> str:
        return self.prefix + "registry.toml"

    def _profile_key(self, profile_name: str, absolute_path: Path) -> str:
        return self.prefix + "profiles/" + profile_name + "/" + _encode_path(absolute_path)

    def _profile_prefix(self, profile_name: str) -> str:
        return self.prefix + "profiles/" + profile_name + "/"

    def is_initialized(self) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=self._registry_key())
            return True
        except self.client.exceptions.ClientError:
            return False
        except Exception:
            return False

    def init(self) -> Registry:
        registry = Registry()
        self.save_registry(registry)
        return registry

    def load_registry(self) -> Registry:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self._registry_key())
            data = tomllib.load(response["Body"])
        except self.client.exceptions.NoSuchKey:
            raise RegistryNotInitializedError(
                "Registry not initialized. Run `regiswitch init` first."
            )
        except Exception as e:
            raise RegiswitchError(f"Failed to load registry from S3: {e}") from e
        if data.get("current_profile") == "":
            data["current_profile"] = None
        return Registry.model_validate(data)

    def save_registry(self, registry: Registry) -> None:
        raw: dict = {
            "current_profile": registry.current_profile or "",
            "profiles": {
                name: {"created_at": meta.created_at.isoformat()}
                for name, meta in registry.profiles.items()
            },
            "files": {
                path: {"path": rf.path, "registered_at": rf.registered_at.isoformat()}
                for path, rf in registry.files.items()
            },
        }
        buf = io.BytesIO()
        tomli_w.dump(raw, buf)
        buf.seek(0)
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=self._registry_key(),
                Body=buf.read(),
                ContentType="application/toml",
            )
        except Exception as e:
            raise RegiswitchError(f"Failed to save registry to S3: {e}") from e

    def copy_to_profile(self, src: Path, profile_name: str) -> None:
        key = self._profile_key(profile_name, src)
        try:
            self.client.upload_file(str(src), self.bucket, key)
        except Exception as e:
            raise RegiswitchError(f"Failed to upload {src} to S3: {e}") from e

    def restore_from_profile(self, profile_name: str, absolute_path: Path) -> None:
        key = self._profile_key(profile_name, absolute_path)
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.client.download_file(self.bucket, key, str(absolute_path))
        except Exception as e:
            raise RegiswitchError(
                f"Failed to restore {absolute_path} from S3 profile '{profile_name}': {e}"
            ) from e

    def has_stored_version(self, profile_name: str, absolute_path: Path) -> bool:
        key = self._profile_key(profile_name, absolute_path)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def delete_profile(self, name: str) -> None:
        prefix = self._profile_prefix(name)
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            keys = [
                obj["Key"]
                for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix)
                for obj in page.get("Contents", [])
            ]
            if keys:
                self.client.delete_objects(
                    Bucket=self.bucket,
                    Delete={"Objects": [{"Key": k} for k in keys]},
                )
        except Exception as e:
            raise RegiswitchError(f"Failed to delete profile '{name}' from S3: {e}") from e
