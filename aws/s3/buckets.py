from __future__ import annotations

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError


def get_s3_client(session: Any):
    """Create an S3 client from a Boto3 session."""
    return session.client("s3")


def list_buckets(session: Any) -> list[str]:
    """
    Return the names of all S3 buckets accessible to the session.
    """
    s3 = get_s3_client(session)

    try:
        response = s3.list_buckets()

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Unable to list S3 buckets: {exc}"
        ) from exc

    return sorted(
        bucket["Name"]
        for bucket in response.get("Buckets", [])
    )


def bucket_exists(
    session: Any,
    bucket_name: str,
) -> bool:
    """
    Check whether an S3 bucket is accessible.

    Returns:
        True if the bucket is accessible.
        False if AWS reports that the bucket does not exist.

    Raises:
        RuntimeError: If access is denied or another AWS error occurs.
    """
    s3 = get_s3_client(session)

    try:
        s3.head_bucket(Bucket=bucket_name)
        return True

    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get(
            "Code",
            "",
        )

        if error_code in {"404", "NoSuchBucket", "NotFound"}:
            return False

        raise RuntimeError(
            f"Unable to check S3 bucket '{bucket_name}': {exc}"
        ) from exc

    except BotoCoreError as exc:
        raise RuntimeError(
            f"Unable to check S3 bucket '{bucket_name}': {exc}"
        ) from exc