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

from aws.lambda_layer.inspector import (
    inspect_layer_version,
)

from aws.lambda_layer.manager import (
    get_account_layers,
    get_layer_versions,
    delete_layer_version,
)

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

def _package_name(requirement: str) -> str:
    """
    Extract the package name from a pip requirement.

    Examples:
        pandas
        pandas==2.2.3
        pandas>=2.2
        pandas~=2.2
    """
    requirement = requirement.strip()

    for operator in (
        "==",
        ">=",
        "<=",
        "~=",
        "!=",
        ">",
        "<",
    ):
        if operator in requirement:
            return requirement.split(
                operator,
                1,
            )[0].strip()

    return requirement


def _add_or_upgrade_package(
    packages: list[str],
    package: str,
) -> list[str]:
    """
    Add a package or replace its existing requirement.

    This means:

        requests==2.31.0

    followed by:

        requests==2.32.5

    becomes only:

        requests==2.32.5
    """
    package = package.strip()

    if not package:
        return packages

    new_name = _package_name(package).lower()

    updated: list[str] = []

    for existing in packages:
        if _package_name(existing).lower() != new_name:
            updated.append(existing)

    updated.append(package)

    return sorted(
        updated,
        key=str.lower,
    )

def run_modify_layer() -> int:
    print_header("Modify / Upgrade Lambda Layer")

    target_account = select_account("TARGET")

    if not target_account:
        return 1

    base_session = target_account["session"]

    region = select_region(base_session)

    session = boto3.Session(
        profile_name=base_session.profile_name,
        region_name=region,
    )

    try:
        layers = get_account_layers(
            session,
            region,
        )
    except Exception as exc:
        print(f"\n✗ Unable to list Lambda layers: {exc}")
        return 1

    if not layers:
        print(
            "\n✗ No Lambda layers found "
            "in this account/region."
        )
        return 1

    layer_name = choose_from_list(
        "Select Layer to Modify",
        layers,
    )

    if not layer_name:
        return 0

    try:
        versions = get_layer_versions(
            session,
            layer_name,
            region,
        )

        if not versions:
            raise RuntimeError(
                "No versions found."
            )

        latest_version = versions[0]["Version"]

        print(
            f"\nDownloading and inspecting "
            f"'{layer_name}' "
            f"(v{latest_version})..."
        )

        inspection = inspect_layer_version(
            session,
            layer_name,
            latest_version,
        )

    except Exception as exc:
        print(
            f"\n✗ Inspection failed: {exc}"
        )
        return 1

    packages = list(
        inspection.packages
    )

    runtime = inspection.runtime
    architecture = inspection.architecture

    if not runtime:
        print(
            "\n✗ Unable to determine "
            "the layer runtime."
        )
        print(
            "The layer cannot be safely rebuilt."
        )
        return 1

    if not architecture:
        print(
            "\n✗ Unable to determine "
            "the layer architecture."
        )
        print(
            "The layer cannot be safely rebuilt."
        )
        return 1

    if not inspection.managed_by_workbench:
        print(
            "\n⚠ Warning: This layer was "
            "not created by AWS Workbench."
        )
        print(
            "Packages were auto-discovered "
            "from .dist-info/METADATA."
        )

    while True:
        print(
            f"\nCurrent Packages "
            f"(Runtime: {runtime} | "
            f"Arch: {architecture}):"
        )

        if not packages:
            print("  (No packages found)")
        else:
            for index, package in enumerate(
                packages,
                start=1,
            ):
                print(
                    f"  {index}. {package}"
                )

        print("\nOptions:")
        print("  [A] Add / Upgrade package")
        print("  [R] Remove package")
        print("  [C] Continue to build")
        print("  [Q] Quit")

        choice = input(
            "\nAction: "
        ).strip().upper()

        if choice == "A":
            package = input(
                "Enter package "
                "(e.g., pandas==2.2.3): "
            ).strip()

            if package:
                packages = _add_or_upgrade_package(
                    packages,
                    package,
                )

                print(
                    f"✓ Added/upgraded: "
                    f"{package}"
                )

        elif choice == "R":
            if not packages:
                print(
                    "\nNo packages available "
                    "to remove."
                )
                continue

            index_text = input(
                "Enter package number to remove: "
            ).strip()

            if not index_text.isdigit():
                print(
                    "✗ Invalid package number."
                )
                continue

            index = int(index_text)

            if not 1 <= index <= len(packages):
                print(
                    "✗ Invalid package number."
                )
                continue

            removed = packages.pop(
                index - 1
            )

            print(
                f"✓ Removed: {removed}"
            )

        elif choice == "C":
            break

        elif choice == "Q":
            print(
                "\nOperation cancelled."
            )
            return 0

        else:
            print(
                "✗ Invalid option."
            )

    if not packages:
        print(
            "\n✗ Cannot deploy an empty layer."
        )
        return 1

    print(
        f"\nBuilding new version of "
        f"'{layer_name}'..."
    )

    bucket_name: str | None = None

    object_key = (
        f"lambda-layers/"
        f"{layer_name}/"
        f"{uuid.uuid4().hex}.zip"
    )

    metadata_key = (
        f"lambda-layers/"
        f"{layer_name}/"
        f"{uuid.uuid4().hex}.json"
    )

    try:
        s3 = session.client(
            "s3",
            region_name=region,
        )

        bucket_name = create_temp_bucket(
            s3,
            region,
        )

        role_arn = ensure_codebuild_role(
            session,
            bucket_name,
        )

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

        print(
            "\nPublishing Next Layer Version..."
        )

        published = publish_layer(
            session=session,
            layer_name=layer_name,
            runtime=runtime,
            architecture=architecture,
            bucket_name=bucket_name,
            object_key=object_key,
            region=region,
        )

        print_header(
            "Layer Update Complete"
        )

        print(
            f"Previous Version : "
            f"v{latest_version}"
        )
        print(
            f"New Version      : "
            f"v{published.version}"
        )
        print(
            f"Layer ARN        : "
            f"{published.layer_arn}"
        )

        return 0

    except Exception as exc:
        print(
            f"\n✗ Deployment failed: {exc}"
        )
        return 1

    finally:
        if bucket_name:
            cleanup_bucket(
                session,
                bucket_name,
                [
                    object_key,
                    metadata_key,
                ],
                region,
            )


def run_delete_layer() -> int:
    print_header("Delete / Prune Lambda Layer")

    target_account = select_account("TARGET")

    if not target_account:
        return 1

    base_session = target_account["session"]

    region = select_region(base_session)

    session = boto3.Session(
        profile_name=base_session.profile_name,
        region_name=region,
    )

    try:
        layers = get_account_layers(
            session,
            region,
        )
    except Exception as exc:
        print(
            f"\n✗ Unable to list layers: {exc}"
        )
        return 1

    if not layers:
        print(
            "\n✗ No Lambda layers found."
        )
        return 0

    layer_name = choose_from_list(
        "Select Layer",
        layers,
    )

    if not layer_name:
        return 0

    try:
        versions = get_layer_versions(
            session,
            layer_name,
            region,
        )
    except Exception as exc:
        print(
            f"\n✗ Unable to list versions: {exc}"
        )
        return 1

    if not versions:
        print(
            "\n✗ No versions found."
        )
        return 0

    print(
        f"\nFound {len(versions)} "
        f"version(s) for "
        f"'{layer_name}'."
    )

    print("\nVersions:")

    for version in versions:
        version_number = version.get(
            "Version"
        )

        created = version.get(
            "CreatedDate",
            "",
        )

        print(
            f"  v{version_number}"
            f"  {created}"
        )

    print("\nOptions:")
    print("  1. Delete ALL versions")
    print("  2. Prune old versions (keep latest)")
    print("  3. Delete specific version")
    print("  0. Cancel")

    choice = (
        input("\nChoice [0]: ")
        .strip()
        or "0"
    )

    if choice == "0":
        return 0

    if choice == "1":
        confirm = input(
            f"\n⚠ Delete ALL versions of "
            f"'{layer_name}'? "
            "[y/N]: "
        ).strip().lower()

        if confirm != "y":
            print(
                "\nOperation cancelled."
            )
            return 0

        for version in versions:
            version_number = version[
                "Version"
            ]

            print(
                f"Deleting v{version_number}..."
            )

            delete_layer_version(
                session,
                layer_name,
                version_number,
                region,
            )

        print(
            "\n✓ All layer versions deleted."
        )

        return 0

    if choice == "2":
        if len(versions) <= 1:
            print(
                "\nOnly one version exists. "
                "Nothing to prune."
            )
            return 0

        latest_version = versions[0][
            "Version"
        ]

        print(
            f"\nKeeping v{latest_version}."
        )

        confirm = input(
            "Delete all older versions? "
            "[y/N]: "
        ).strip().lower()

        if confirm != "y":
            print(
                "\nOperation cancelled."
            )
            return 0

        for version in versions[1:]:
            version_number = version[
                "Version"
            ]

            print(
                f"Deleting v{version_number}..."
            )

            delete_layer_version(
                session,
                layer_name,
                version_number,
                region,
            )

        print("\n✓ Pruning complete.")

        return 0

    if choice == "3":
        version_text = input("\nEnter version number: ").strip()

        if not version_text.isdigit():
            print("\n✗ Invalid version.")
            return 1

        version_number = int(
            version_text
        )

        existing_versions = { item["Version"] for item in versions }

        if version_number not in existing_versions:
            print(
                f"\n✗ Version "
                f"v{version_number} "
                f"does not exist."
            )
            return 1

        confirm = input(
            f"\nDelete "
            f"'{layer_name}' "
            f"v{version_number}? "
            "[y/N]: "
        ).strip().lower()

        if confirm != "y":
            print(
                "\nOperation cancelled."
            )
            return 0

        delete_layer_version(
            session,
            layer_name,
            version_number,
            region,
        )

        print(f"\n✓ Deleted '{layer_name}' v{version_number}.")

        return 0

    print("\n✗ Invalid choice.")

    return 1

def run_menu() -> int:
    while True:
        print_header("AWS Lambda Layer Operations Hub")

        print("1. Build & Publish New Layer")
        print("2. Modify / Upgrade Existing Layer")
        print("3. Delete / Prune Layer Versions")
        print("0. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            return run_create_layer()

        if choice == "2":
            return run_modify_layer()

        if choice == "3":
            return run_delete_layer()

        if choice == "0":
            return 0

        print("\n✗ Invalid choice.")

def main() -> int:
    try:
        return run_menu()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        return 130

    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
