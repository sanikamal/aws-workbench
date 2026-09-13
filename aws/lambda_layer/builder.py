from __future__ import annotations

import json
from typing import Any

from aws.lambda_layer.codebuild import (
    create_codebuild_project,
    delete_codebuild_project,
    generate_project_name,
    start_build,
    wait_for_build,
)
from aws.lambda_layer.models import BuildResult


def build_layer(
    session: Any,
    layer_name: str,
    packages: list[str],
    runtime: str,
    architecture: str,
    bucket_name: str,
    object_key: str,
    metadata_key: str,
    service_role_arn: str,
) -> BuildResult:
    region = session.region_name
    if not region:
        raise ValueError("AWS region is required for CodeBuild.")

    codebuild = session.client("codebuild", region_name=region)
    project_name = generate_project_name(layer_name)

    try:
        print("\nCreating temporary CodeBuild project...")
        create_codebuild_project(
            client=codebuild,
            project_name=project_name,
            service_role_arn=service_role_arn,
            bucket_name=bucket_name,
            object_key=object_key,
            metadata_key=metadata_key,
            packages=packages,
            runtime=runtime,
            architecture=architecture,
        )
        print(f"✓ CodeBuild project created: {project_name}")

        print("\nStarting Linux build...")
        build_id = start_build(codebuild, project_name)
        print(f"✓ Build started: {build_id}")
        wait_for_build(codebuild, build_id)
        print("✓ CodeBuild completed successfully")

        s3 = session.client("s3", region_name=region)
        metadata = json.loads(
            s3.get_object(Bucket=bucket_name, Key=metadata_key)["Body"].read()
        )

        return BuildResult(
            layer_name=layer_name,
            runtime=runtime,
            architecture=architecture,
            packages=packages,
            bucket_name=bucket_name,
            object_key=object_key,
            metadata_key=metadata_key,
            uncompressed_size_mb=round(metadata["uncompressed_bytes"] / 1024 / 1024, 2),
            compressed_size_mb=round(metadata["compressed_bytes"] / 1024 / 1024, 2),
        )
    finally:
        delete_codebuild_project(codebuild, project_name)
