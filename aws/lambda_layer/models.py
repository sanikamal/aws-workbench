from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuildResult:
    layer_name: str
    runtime: str
    architecture: str
    packages: list[str]
    bucket_name: str
    object_key: str
    metadata_key: str
    uncompressed_size_mb: float
    compressed_size_mb: float


@dataclass(frozen=True)
class PublishedLayer:
    layer_name: str
    layer_arn: str
    version: int
    runtime: str
    architecture: str
    region: str
