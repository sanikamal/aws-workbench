from __future__ import annotations

import uuid
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from aws.lambda_layer.models import PublishedLayer


def create_temp_bucket(s3_client: Any, region: str) -> str:
    bucket_name = f"aws-workbench-layer-{uuid.uuid4().hex}"
    if region == "us-east-1":
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
    return bucket_name


def publish_layer(
    session: Any,
    layer_name: str,
    runtime: str,
    architecture: str,
    bucket_name: str,
    object_key: str,
    region: str,
    description: str = "Built by AWS Workbench",
) -> PublishedLayer:
    lambda_client = session.client("lambda", region_name=region)
    try:
        response = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Description=description,
            Content={"S3Bucket": bucket_name, "S3Key": object_key},
            CompatibleRuntimes=[runtime],
            CompatibleArchitectures=[architecture],
        )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"Unable to publish Lambda Layer: {exc}") from exc

    return PublishedLayer(
        layer_name=layer_name,
        layer_arn=response["LayerVersionArn"],
        version=response["Version"],
        runtime=runtime,
        architecture=architecture,
        region=region,
    )


def cleanup_bucket(
    session: Any,
    bucket_name: str,
    object_keys: list[str],
    region: str,
) -> list[str]:
    """Delete temporary objects/bucket and return cleanup warnings."""
    s3 = session.client("s3", region_name=region)
    warnings: list[str] = []

    for key in object_keys:
        try:
            s3.delete_object(Bucket=bucket_name, Key=key)
        except Exception as exc:
            warnings.append(f"Could not delete S3 object {key}: {exc}")

    try:
        s3.delete_bucket(Bucket=bucket_name)
    except Exception as exc:
        warnings.append(f"Could not delete temporary bucket {bucket_name}: {exc}")

    return warnings
