import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class Store(ABC):
    """Content-addressable blob store. Backends: local filesystem or S3."""

    def put(self, data: bytes) -> str:
        sha256 = hashlib.sha256(data).hexdigest()
        if not self.exists(sha256):
            self._write(sha256, data)
        return sha256

    @abstractmethod
    def _write(self, sha256: str, data: bytes): ...

    @abstractmethod
    def get(self, sha256: str) -> bytes: ...

    @abstractmethod
    def exists(self, sha256: str) -> bool: ...

    @abstractmethod
    def delete(self, sha256: str): ...

    @abstractmethod
    def list_all(self) -> List[str]: ...

    def migrate_to(self, target: "Store") -> int:
        """Copy all blobs from this store to target. Returns count transferred."""
        count = 0
        for sha256 in self.list_all():
            if not target.exists(sha256):
                target._write(sha256, self.get(sha256))
                count += 1
        return count


# --------------------------------------------------------------------------- local


class LocalStore(Store):
    def __init__(self, blob_dir: Path):
        self._dir = blob_dir

    def _path(self, sha256: str) -> Path:
        return self._dir / sha256[:2] / sha256[2:]

    def _write(self, sha256: str, data: bytes):
        p = self._path(sha256)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def get(self, sha256: str) -> bytes:
        return self._path(sha256).read_bytes()

    def exists(self, sha256: str) -> bool:
        return self._path(sha256).exists()

    def delete(self, sha256: str):
        p = self._path(sha256)
        if p.exists():
            p.unlink()
            if not any(p.parent.iterdir()):
                p.parent.rmdir()

    def list_all(self) -> List[str]:
        if not self._dir.exists():
            return []
        return [
            d.name + b.name
            for d in self._dir.iterdir() if d.is_dir()
            for b in d.iterdir() if b.is_file()
        ]


# --------------------------------------------------------------------------- s3


class S3Store(Store):
    def __init__(
        self,
        bucket: str,
        prefix: str = "regiswitch/",
        region: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        try:
            import boto3
        except ImportError:
            raise ImportError("S3 store requires boto3: pip install 'regiswitch[s3]'")

        self._bucket = bucket
        self._prefix = prefix.rstrip("/") + "/"

        kwargs = {}
        if region:
            kwargs["region_name"] = region
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._s3 = boto3.client("s3", **kwargs)

    def _key(self, sha256: str) -> str:
        return f"{self._prefix}{sha256[:2]}/{sha256[2:]}"

    def _sha_from_key(self, key: str) -> str:
        rel = key[len(self._prefix):]
        return rel.replace("/", "")

    def _write(self, sha256: str, data: bytes):
        self._s3.put_object(Bucket=self._bucket, Key=self._key(sha256), Body=data)

    def get(self, sha256: str) -> bytes:
        resp = self._s3.get_object(Bucket=self._bucket, Key=self._key(sha256))
        return resp["Body"].read()

    def exists(self, sha256: str) -> bool:
        from botocore.exceptions import ClientError
        try:
            self._s3.head_object(Bucket=self._bucket, Key=self._key(sha256))
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return False
            raise

    def delete(self, sha256: str):
        self._s3.delete_object(Bucket=self._bucket, Key=self._key(sha256))

    def list_all(self) -> List[str]:
        paginator = self._s3.get_paginator("list_objects_v2")
        result = []
        for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
            for obj in page.get("Contents", []):
                result.append(self._sha_from_key(obj["Key"]))
        return result


# --------------------------------------------------------------------------- factory


def build_store(store_cfg: dict, local_dir: Path) -> Store:
    kind = store_cfg.get("type", "local")
    if kind == "local":
        return LocalStore(local_dir)
    if kind == "s3":
        return S3Store(
            bucket=store_cfg["bucket"],
            prefix=store_cfg.get("prefix", "regiswitch/"),
            region=store_cfg.get("region"),
            endpoint_url=store_cfg.get("endpoint_url"),
        )
    raise ValueError(f"Unknown store type '{kind}'. Valid: local, s3")
