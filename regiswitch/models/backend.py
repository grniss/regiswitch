from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel


class LocalBackendConfig(BaseModel):
    type: Literal["local"] = "local"
    path: Optional[str] = None


class S3BackendConfig(BaseModel):
    type: Literal["s3"] = "s3"
    bucket: str
    prefix: str = "regiswitch/"
    region: Optional[str] = None


BackendConfig = Union[LocalBackendConfig, S3BackendConfig]
