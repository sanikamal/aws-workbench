from __future__ import annotations
import subprocess
import sys
from typing import Any

from core.aws_session import create_session
from aws.s3.objects import list_objects

try:
    from aws.s3.buckets import list_buckets
except ImportError:
    # If your existing bucket function has another location,
    # change this import only.
    list_buckets = None


def print_header(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def choose_from_list(
    title: str,
    items: list[Any],
    display_func=None,
    allow_back: bool = False,
):
    """Display numbered options and return the selected item."""

    if not items:
        print(f"\nNo {title.lower()} found.")
        return None

    while True:
        print()
        print(title)
        print("-" * 60)

        for index, item in enumerate(items, start=1):
            display = display_func(item) if display_func else str(item)
            print(f"{index}. {display}")

        if allow_back:
            print("0. Back")

        try:
            choice = input("\nChoice: ").strip()

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            choice = int(choice)

            if allow_back and choice == 0:
                return None

            if 1 <= choice <= len(items):
                return items[choice - 1]

            print(f"Please select a number between 1 and {len(items)}.")

        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)


def get_aws_profiles() -> list[str]:
    """
    Return locally configured AWS profiles.

    This uses boto3's profile discovery rather than requiring
    profiles to be manually entered in this CLI.
    """
    import boto3

    session = boto3.Session()
    profiles = session.available_profiles

    if not profiles:
        # boto3 may still have credentials under the default profile.
        return ["default"]

    return sorted(set(profiles))


import subprocess


def add_aws_profile() -> str | None:
    """Create and validate a new AWS CLI SSO profile."""

    print()
    print("=" * 60)
    print("Add AWS account")
    print("=" * 60)

    profile_name = input(
        "\nEnter a profile name: "
    ).strip()

    if not profile_name:
        print("Profile name cannot be empty.")
        return None

    # Don't overwrite an existing profile.
    if profile_name in get_aws_profiles():
        print(
            f"\nProfile '{profile_name}' already exists."
        )
        return profile_name

    print()
    print(
        f"Starting AWS SSO configuration for "
        f"'{profile_name}'..."
    )
    print()

    try:
        result = subprocess.run(
            [
                "aws",
                "configure",
                "sso",
                "--profile",
                profile_name,
            ],
            check=False,
        )

    except FileNotFoundError:
        print(
            "\nAWS CLI was not found."
            "\nPlease install AWS CLI and make sure "
            "'aws' is available in PATH."
        )
        return None

    if result.returncode != 0:
        print(
            "\nAWS profile configuration failed."
        )
        return None

    # ---------------------------------------------------------
    # Verify that the profile was actually created
    # ---------------------------------------------------------

    profiles = get_aws_profiles()

    if profile_name not in profiles:
        print(
            f"\nProfile '{profile_name}' was not found "
            "after configuration."
        )
        return None

    print()
    print(
        f"✓ Profile '{profile_name}' created successfully."
    )

    # ---------------------------------------------------------
    # Authenticate and validate the profile
    # ---------------------------------------------------------

    try:
        session = create_session(profile_name)

        sts = session.client("sts")

        identity = sts.get_caller_identity()

        account_id = identity["Account"]

        print(
            f"✓ AWS authentication successful."
        )
        print(
            f"  Account ID : {account_id}"
        )

    except Exception as exc:
        print(
            "\nProfile was created, but authentication "
            "failed."
        )
        print(f"Error: {exc}")

        return None

    return profile_name


def select_account(label: str):
    while True:
        profiles = get_aws_profiles()

        print()
        print(f"Select {label} account")
        print("-" * 60)

        for index, profile in enumerate(
            profiles,
            start=1,
        ):
            print(f"{index}. {profile}")

        add_option = len(profiles) + 1

        print(f"{add_option}. + Add AWS account")

        choice = input("\nChoice: ").strip()

        if not choice.isdigit():
            print("Please enter a number.")
            continue

        choice = int(choice)

        # -----------------------------------------------------
        # CREATE NEW PROFILE
        # -----------------------------------------------------

        if choice == add_option:
            new_profile = add_aws_profile()

            if not new_profile:
                continue

            # Profile now exists, so immediately create session.
            try:
                session = create_session(new_profile)

                sts = session.client("sts")
                identity = sts.get_caller_identity()

                return {
                    "profile": new_profile,
                    "session": session,
                    "account_id": identity["Account"],
                }

            except Exception as exc:
                print(
                    f"\nUnable to use profile "
                    f"'{new_profile}': {exc}"
                )

                continue

        # -----------------------------------------------------
        # EXISTING PROFILE
        # -----------------------------------------------------

        if not 1 <= choice <= len(profiles):
            print("Invalid selection.")
            continue

        profile = profiles[choice - 1]

        try:
            print(
                f"\nConnecting to profile '{profile}'..."
            )

            session = create_session(profile)

            sts = session.client("sts")

            identity = sts.get_caller_identity()

            account_id = identity["Account"]

            print(
                f"✓ Connected to AWS account "
                f"{account_id}"
            )

            return {
                "profile": profile,
                "session": session,
                "account_id": account_id,
            }

        except Exception as exc:
            print(
                f"\nUnable to connect to "
                f"'{profile}': {exc}"
            )

def get_buckets(session) -> list[str]:
    """
    Get buckets using the existing project implementation.
    """

    if list_buckets is not None:
        result = list_buckets(session)

        if result is None:
            return []

        buckets = []

        for bucket in result:
            if isinstance(bucket, str):
                buckets.append(bucket)
            elif isinstance(bucket, dict):
                name = bucket.get("Name") or bucket.get("name")
                if name:
                    buckets.append(name)
            else:
                name = getattr(bucket, "name", None)
                if name:
                    buckets.append(name)

        return buckets

    # Fallback if the existing project does not have list_buckets().
    s3 = session.client("s3")
    response = s3.list_buckets()

    return [
        bucket["Name"]
        for bucket in response.get("Buckets", [])
    ]

def create_bucket(
    session,
    bucket_name: str | None = None,
    region: str | None = None,
) -> str | None:
    """Create an S3 bucket in the selected AWS account."""

    s3 = session.client("s3")

    if region is None:
        region = session.region_name

    while True:
        if not bucket_name:
            bucket_name = input(
                "\nEnter new bucket name: "
            ).strip()

        if not bucket_name:
            print("Bucket name cannot be empty.")
            bucket_name = None
            continue

        try:
            # us-east-1 does not use LocationConstraint.
            if region and region != "us-east-1":
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": region,
                    },
                )
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                )

            print()
            print(
                f"✓ Bucket created successfully: "
                f"{bucket_name}"
            )

            return bucket_name

        except Exception as exc:
            error_code = getattr(
                exc,
                "response",
                {},
            ).get(
                "Error",
                {},
            ).get(
                "Code"
            )

            if error_code == "BucketAlreadyExists":
                print()
                print(
                    f"✗ Bucket '{bucket_name}' is already "
                    "owned by another AWS account."
                )
                print(
                    "S3 bucket names are globally unique."
                )

                bucket_name = input(
                    "\nEnter a different bucket name "
                    "(or press Enter to cancel): "
                ).strip()

                if not bucket_name:
                    return None

                continue

            if error_code == "BucketAlreadyOwnedByYou":
                print()
                print(
                    f"✓ Bucket '{bucket_name}' already "
                    "exists in this account."
                )

                return bucket_name

            print()
            print(
                f"✗ Unable to create bucket "
                f"'{bucket_name}'."
            )
            print(f"Error: {exc}")

            return None

def select_bucket(
    session,
    account_name: str,
    source_bucket: str | None = None,
    allow_create: bool = False,
):
    """
    Select an S3 bucket.

    For destination buckets:
    - Press Enter to use the source bucket name.
    - If it does not exist, offer to create it.
    - Existing buckets can still be selected manually.
    """

    print_header(f"Select {account_name} bucket")

    try:
        buckets = get_buckets(session)
    except Exception as exc:
        print("\nUnable to list buckets.")
        print(f"Error: {exc}")
        return None

    # ---------------------------------------------------------
    # DESTINATION BUCKET
    # ---------------------------------------------------------

    if allow_create:
        default_bucket = source_bucket or ""

        print("\nAvailable buckets")
        print("-" * 60)

        if buckets:
            for index, bucket in enumerate(buckets, start=1):
                print(f"{index}. {bucket}")

            create_option = len(buckets) + 1
            print(f"{create_option}. + Create new bucket")

        else:
            print("No buckets found.")

            create_option = 1
            print(f"{create_option}. + Create new bucket")

        if default_bucket:
            print()
            print(
                "Press Enter to use source bucket:"
            )
            print(f"  {default_bucket}")

        while True:
            try:
                choice = input("\nChoice: ").strip()

            except KeyboardInterrupt:
                print("\nCancelled.")
                sys.exit(0)

            # -------------------------------------------------
            # ENTER = SOURCE BUCKET
            # -------------------------------------------------

            if choice == "":
                if not default_bucket:
                    print(
                        "Please enter a number."
                    )
                    continue

                print()
                print(
                    f"Checking destination for "
                    f"'{default_bucket}'..."
                )

                if default_bucket in buckets:
                    print()
                    print(
                        "✓ Using source bucket as "
                        "destination bucket:"
                    )
                    print(
                        f"  {default_bucket}"
                    )

                    return default_bucket

                # -------------------------------------------------
                # SOURCE BUCKET DOES NOT EXIST
                # -------------------------------------------------

                print()
                print(
                    f"Bucket '{default_bucket}' does not "
                    "exist in the destination account."
                )

                print()
                print("1. Create this bucket")
                print("2. Select another bucket")
                print("3. Cancel")

                while True:
                    action = input("\nChoice: ").strip()

                    if action == "1":
                        created = create_bucket(
                            session=session,
                            bucket_name=default_bucket,
                        )

                        if created:
                            return created

                        # Creation failed.
                        # Go back to destination bucket menu.
                        break

                    if action == "2":
                        break

                    if action == "3":
                        return None

                    print(
                        "Please select 1, 2 or 3."
                    )

                continue

            # -------------------------------------------------
            # NUMBER SELECTION
            # -------------------------------------------------

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            choice_number = int(choice)

            # Existing bucket
            if 1 <= choice_number <= len(buckets):
                selected = buckets[choice_number - 1]

                print()
                print(
                    f"✓ Selected destination bucket: "
                    f"{selected}"
                )

                return selected

            # Create new bucket
            if choice_number == create_option:
                created = create_bucket(
                    session=session,
                )

                if created:
                    return created

                continue

            max_choice = create_option

            print(
                f"Please select a number between "
                f"1 and {max_choice}."
            )

    # ---------------------------------------------------------
    # SOURCE BUCKET
    # ---------------------------------------------------------

    return choose_from_list(
        "Available buckets",
        buckets,
    )

def normalize_object_key(item: Any) -> str:
    """Convert different object formats into an S3 key."""

    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        return (
            item.get("Key")
            or item.get("key")
            or item.get("Name")
            or item.get("name")
        )

    return (
        getattr(item, "key", None)
        or getattr(item, "Key", None)
        or str(item)
    )


def get_objects(session, bucket: str) -> list[str]:
    result = list_objects(session, bucket)

    if result is None:
        return []

    return [
        normalize_object_key(item)
        for item in result
        if normalize_object_key(item)
    ]


def select_source_objects(session, bucket: str):
    print_header("Select objects")

    try:
        objects = get_objects(session, bucket)
    except Exception as exc:
        print(f"\nUnable to list objects.")
        print(f"Error: {exc}")
        return None

    if not objects:
        print(f"\nNo objects found in '{bucket}'.")
        return None

    print(f"\nFound {len(objects)} object(s).")

    print("\n1. Copy all objects")
    print("2. Copy objects under a prefix")
    print("3. Select individual objects")

    while True:
        choice = input("\nChoice: ").strip()

        if choice == "1":
            return {
                "mode": "all",
                "objects": objects,
                "prefix": "",
            }

        if choice == "2":
            prefix = input("\nEnter source prefix: ").strip()

            selected = [
                key
                for key in objects
                if key.startswith(prefix)
            ]

            if not selected:
                print(f"No objects found for prefix '{prefix}'.")
                continue

            print(
                f"\nFound {len(selected)} object(s) "
                f"under '{prefix}'."
            )

            return {
                "mode": "prefix",
                "objects": selected,
                "prefix": prefix,
            }

        if choice == "3":
            selected = []

            print()

            for index, key in enumerate(objects, start=1):
                print(f"{index}. {key}")

            raw = input(
                "\nEnter object numbers separated by commas: "
            ).strip()

            try:
                indexes = [
                    int(value.strip())
                    for value in raw.split(",")
                    if value.strip()
                ]

                for index in indexes:
                    if not 1 <= index <= len(objects):
                        raise ValueError

                selected = [
                    objects[index - 1]
                    for index in indexes
                ]

                if not selected:
                    print("No objects selected.")
                    continue

                return {
                    "mode": "selected",
                    "objects": selected,
                    "prefix": "",
                }

            except ValueError:
                print("Invalid object selection.")
                continue

        else:
            print("Please select 1, 2 or 3.")


def build_destination_key(
    source_key: str,
    source_prefix: str,
    destination_prefix: str,
) -> str:
    destination_prefix = destination_prefix.strip("/")

    if source_prefix:
        relative_key = source_key[len(source_prefix):].lstrip("/")
    else:
        relative_key = source_key

    if destination_prefix:
        return f"{destination_prefix}/{relative_key}"

    return relative_key


def copy_object(
    source_session,
    source_bucket: str,
    source_key: str,
    destination_session,
    destination_bucket: str,
    destination_key: str,
) -> None:
    """
    Copy one object between AWS accounts.

    This downloads from the source account and uploads to
    the destination account. This works even when the accounts
    do not have direct cross-account S3 copy permissions.
    """

    source_s3 = source_session.client("s3")
    destination_s3 = destination_session.client("s3")

    response = source_s3.get_object(
        Bucket=source_bucket,
        Key=source_key,
    )

    body = response["Body"]

    destination_s3.upload_fileobj(
        body,
        destination_bucket,
        destination_key,
    )


def confirm_copy(
    source_account,
    source_bucket: str,
    destination_account,
    destination_bucket: str,
    objects: list[str],
    destination_prefix: str,
) -> bool:

    print_header("Copy Summary")

    print(f"Source account      : {source_account['profile']}")
    print(f"Source AWS account  : {source_account['account_id']}")
    print(f"Source bucket       : {source_bucket}")
    print()
    print(
        f"Destination account : "
        f"{destination_account['profile']}"
    )
    print(
        f"Destination AWS ID  : "
        f"{destination_account['account_id']}"
    )
    print(f"Destination bucket  : {destination_bucket}")
    print(f"Destination prefix  : {destination_prefix or '(root)'}")
    print()
    print(f"Objects to copy     : {len(objects)}")

    print("\nFirst objects:")

    for key in objects[:10]:
        destination_key = build_destination_key(
            key,
            "",
            destination_prefix,
        )

        print(f"  {key}")
        print(f"    -> {destination_key}")

    if len(objects) > 10:
        print(f"  ... and {len(objects) - 10} more")

    print()

    answer = input(
        "Proceed with copy? [y/N]: "
    ).strip().lower()

    return answer in ("y", "yes")


def execute_copy(
    source_account,
    source_bucket,
    source_selection,
    destination_account,
    destination_bucket,
    destination_prefix,
):
    objects = source_selection["objects"]
    source_prefix = source_selection.get("prefix", "")

    total = len(objects)
    successful = 0
    failed = []

    print_header("Copying Objects")

    for index, source_key in enumerate(objects, start=1):

        destination_key = build_destination_key(
            source_key,
            source_prefix,
            destination_prefix,
        )

        print(
            f"[{index}/{total}] "
            f"{source_key} -> {destination_key}"
        )

        try:
            copy_object(
                source_session=source_account["session"],
                source_bucket=source_bucket,
                source_key=source_key,
                destination_session=destination_account["session"],
                destination_bucket=destination_bucket,
                destination_key=destination_key,
            )

            successful += 1
            print("    ✓ Success")

        except Exception as exc:
            failed.append(
                {
                    "source": source_key,
                    "destination": destination_key,
                    "error": str(exc),
                }
            )

            print(f"    ✗ Failed: {exc}")

    print_header("Copy Result")

    print(f"Total objects : {total}")
    print(f"Successful    : {successful}")
    print(f"Failed        : {len(failed)}")

    if failed:
        print("\nFailed objects:")

        for item in failed:
            print(f"\nSource: {item['source']}")
            print(f"Error : {item['error']}")

    return len(failed) == 0


def run_s3_copy() -> int:
    print_header("AWS S3 Cross-Account Copy")

    # ---------------------------------------------------------
    # SOURCE ACCOUNT
    # ---------------------------------------------------------

    source_account = select_account("SOURCE")

    if not source_account:
        return 1

    # ---------------------------------------------------------
    # SOURCE BUCKET
    # ---------------------------------------------------------

    source_bucket = select_bucket(
        source_account["session"],
        "SOURCE",
    )

    if not source_bucket:
        return 1

    print(f"\nSelected source bucket: {source_bucket}")

    # ---------------------------------------------------------
    # SOURCE OBJECTS
    # ---------------------------------------------------------

    source_selection = select_source_objects(
        source_account["session"],
        source_bucket,
    )

    if not source_selection:
        return 1

    # ---------------------------------------------------------
    # DESTINATION ACCOUNT
    # ---------------------------------------------------------

    destination_account = select_account("DESTINATION")

    if not destination_account:
        return 1

    # ---------------------------------------------------------
    # DESTINATION BUCKET
    # ---------------------------------------------------------

    destination_bucket = select_bucket(
    session=destination_account["session"],
    account_name="DESTINATION",
    source_bucket=source_bucket,
    allow_create=True,
)

    if not destination_bucket:
        return 1

    print(
        f"\nSelected destination bucket: "
        f"{destination_bucket}"
    )

    # ---------------------------------------------------------
    # DESTINATION PREFIX
    # ---------------------------------------------------------

    destination_prefix = input(
        "\nDestination prefix "
        "(press Enter for bucket root): "
    ).strip()

    # ---------------------------------------------------------
    # CONFIRM
    # ---------------------------------------------------------

    if not confirm_copy(
        source_account=source_account,
        source_bucket=source_bucket,
        destination_account=destination_account,
        destination_bucket=destination_bucket,
        objects=source_selection["objects"],
        destination_prefix=destination_prefix,
    ):
        print("\nCopy cancelled.")
        return 0

    # ---------------------------------------------------------
    # COPY
    # ---------------------------------------------------------

    success = execute_copy(
        source_account=source_account,
        source_bucket=source_bucket,
        source_selection=source_selection,
        destination_account=destination_account,
        destination_bucket=destination_bucket,
        destination_prefix=destination_prefix,
    )

    if success:
        print("\n✓ S3 copy completed successfully.")
        return 0

    print("\n⚠ S3 copy completed with errors.")
    return 1


def main():
    try:
        return run_s3_copy()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        return 130

    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())