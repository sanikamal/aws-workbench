from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from aws.s3.buckets import get_s3_client


@dataclass(frozen=True)
class S3Object:
    """Information about an S3 object."""

    key: str
    size: int
    last_modified: datetime | None = None
    etag: str | None = None
    storage_class: str | None = None


def list_objects(
    session: Any,
    bucket_name: str,
    prefix: str | None = None,
) -> list[S3Object]:
    """
    List all objects in an S3 bucket.

    Pagination is handled automatically, so buckets containing
    more than 1,000 objects are fully traversed.

    Args:
        session: Authenticated Boto3 session.
        bucket_name: Name of the S3 bucket.
        prefix: Optional object-key prefix to filter by.

    Returns:
        A list of S3Object instances.
    """
    s3 = get_s3_client(session)

    paginator = s3.get_paginator("list_objects_v2")

    pagination_config = {}

    if prefix:
        pagination_config["Prefix"] = prefix

    objects: list[S3Object] = []

    try:
        pages = paginator.paginate(
            Bucket=bucket_name,
            **pagination_config,
        )

        for page in pages:
            for item in page.get("Contents", []):
                objects.append(
                    S3Object(
                        key=item["Key"],
                        size=item.get("Size", 0),
                        last_modified=item.get("LastModified"),
                        etag=item.get("ETag"),
                        storage_class=item.get("StorageClass"),
                    )
                )

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Unable to list objects in S3 bucket "
            f"'{bucket_name}': {exc}"
        ) from exc

    return objects


def count_objects(
    session: Any,
    bucket_name: str,
    prefix: str | None = None,
) -> int:
    """Return the total number of objects in an S3 bucket."""

    return len(
        list_objects(
            session=session,
            bucket_name=bucket_name,
            prefix=prefix,
        )
    )