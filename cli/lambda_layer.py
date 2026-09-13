from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

import boto3

from aws.lambda_layer.builder import build_layer
from aws.lambda_layer.codebuild import ensure_codebuild_role
from aws.lambda_layer.publisher import cleanup_bucket, create_temp_bucket, publish_layer
from cli.s3_copy import choose_from_list, print_header, select_account

SUPPORTED_RUNTIMES = ["python3.14","python3.13", "python3.12", "python3.11", "python3.10"]
SUPPORTED_ARCHITECTURES = ["x86_64", "arm64"]


def validate_layer_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9-_]{1,140}", name))


def collect_packages() -> list[str]:
    print("\nPackage Input")
    print("1. Enter packages")
    print("2. Import requirements.txt")
    choice = input("\nChoice [1]: ").strip() or "1"

    if choice == "2":
        path = Path(input("\nEnter requirements.txt path: ").strip())
        if not path.is_file():
            print(f"✗ File not found: {path}")
            return []
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    packages: list[str] = []
    print("\nEnter package names one at a time.")
    print("Press Enter on an empty line when finished.\n")
    while True:
        package = input("Package: ").strip()
        if not package:
            break
        packages.append(package)
    return packages


def select_region(session) -> str:
    default = session.region_name or "us-east-1"
    return input(f"\nAWS Region [{default}]: ").strip() or default


def run_create_layer() -> int:
    print_header("AWS Lambda Layer Builder & Deployer")

    layer_name = input("\nEnter layer name: ").strip()
    if not validate_layer_name(layer_name):
        print(
            "✗ Layer name must contain only letters, numbers, "
            "hyphens, or underscores (max 140 characters)."
        )
        return 1

    packages = collect_packages()
    if not packages:
        print("✗ No packages specified.")
        return 1

    runtime = choose_from_list("Select Python runtime", SUPPORTED_RUNTIMES)
    if not runtime:
        return 1

    architecture = choose_from_list("Select architecture", SUPPORTED_ARCHITECTURES)
    if not architecture:
        return 1

    target_account = select_account("TARGET")
    if not target_account:
        return 1

    base_session = target_account["session"]
    region = select_region(base_session)
    session = boto3.Session(
        profile_name=base_session.profile_name,
        region_name=region,
    )

    print("\nLayer Configuration")
    print(f"  Name         : {layer_name}")
    print(f"  Runtime      : {runtime}")
    print(f"  Architecture : {architecture}")
    print(f"  Region       : {region}")
    print(f"  Account      : {target_account['account_id']}")
    print("\nPackages:")
    for package in packages:
        print(f"  - {package}")

    confirm = input("\nCreate and deploy this layer? [Y/n]: ").strip().lower()
    if confirm in {"n", "no"}:
        print("Operation cancelled.")
        return 0

    bucket_name: str | None = None
    object_key = f"lambda-layers/{layer_name}/{uuid.uuid4().hex}.zip"
    metadata_key = f"lambda-layers/{layer_name}/{uuid.uuid4().hex}.json"

    try:
        s3 = session.client("s3", region_name=region)

        print("\nCreating temporary S3 bucket...")
        bucket_name = create_temp_bucket(s3, region)
        print(f"✓ Temporary bucket: {bucket_name}")

        print("\nPreparing CodeBuild service role...")
        account_id = target_account["account_id"]
        role_arn = ensure_codebuild_role(session, bucket_name)
        print(f"✓ CodeBuild service role ready: {role_arn}")

        result = build_layer(
            session=session,
            layer_name=layer_name,
            packages=packages,
            runtime=runtime,
            architecture=architecture,
            bucket_name=bucket_name,
            object_key=object_key,
            metadata_key=metadata_key,
            service_role_arn=role_arn,
        )

        print("\nBuild Summary")
        print(f"  Uncompressed : {result.uncompressed_size_mb} MB")
        print(f"  ZIP size     : {result.compressed_size_mb} MB")

        print("\nPublishing Lambda Layer...")
        published = publish_layer(
            session=session,
            layer_name=layer_name,
            runtime=runtime,
            architecture=architecture,
            bucket_name=bucket_name,
            object_key=object_key,
            region=region,
        )

        print_header("Lambda Layer Deployment Complete")
        print(f"Layer name       : {published.layer_name}")
        print(f"Version          : {published.version}")
        print(f"Runtime          : {published.runtime}")
        print(f"Architecture     : {published.architecture}")
        print(f"AWS Account ID   : {account_id}")
        print(f"Region           : {region}")
        print(f"\nLayer Version ARN:\n{published.layer_arn}")
        return 0
    except Exception as exc:
        print(f"\n✗ Deployment failed: {exc}")
        return 1
    finally:
        if bucket_name:
            print("\nCleaning temporary S3 resources...")
            warnings = cleanup_bucket(
                session,
                bucket_name,
                [object_key, metadata_key],
                region,
            )
            if warnings:
                for warning in warnings:
                    print(f"⚠ {warning}")
            else:
                print("✓ Temporary S3 resources cleaned up")


def main() -> int:
    try:
        return run_create_layer()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        return 130
    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
