from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from aws.s3.buckets import get_s3_client


def copy_object(
    source_session: Any,
    destination_session: Any,
    source_bucket: str,
    destination_bucket: str,
    object_key: str,
) -> None:
    """
    Copy a single S3 object between independently authenticated
    source and destination AWS sessions.

    The object is downloaded to a temporary local file and then
    uploaded to the destination bucket.

    Args:
        source_session: Authenticated source Boto3 session.
        destination_session: Authenticated destination Boto3 session.
        source_bucket: Source S3 bucket name.
        destination_bucket: Destination S3 bucket name.
        object_key: S3 object key to copy.
    """
    source_s3 = get_s3_client(source_session)
    destination_s3 = get_s3_client(destination_session)

    try:
        with tempfile.TemporaryDirectory(
            prefix="aws-workbench-s3-"
        ) as temp_dir:
            local_path = Path(temp_dir) / "object"

            source_s3.download_file(
                source_bucket,
                object_key,
                str(local_path),
            )

            destination_s3.upload_file(
                str(local_path),
                destination_bucket,
                object_key,
            )

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Unable to copy S3 object "
            f"'{source_bucket}/{object_key}' "
            f"to '{destination_bucket}/{object_key}': {exc}"
        ) from exc