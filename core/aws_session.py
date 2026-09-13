from __future__ import annotations

import boto3
from botocore.exceptions import BotoCoreError, ProfileNotFound

from core.aws_auth import authenticate_profile
from core.aws_profiles import profile_exists


def create_session(
    profile_name: str,
    region: str | None = None,
) -> boto3.Session:
    """
    Create an authenticated Boto3 session using an AWS CLI profile.

    If the profile uses SSO and the cached SSO token has expired,
    AWS SSO login is started automatically.
    """
    if not profile_exists(profile_name):
        raise ValueError(
            f"AWS profile '{profile_name}' was not found "
            "in the local AWS CLI configuration."
        )

    # Ensure credentials are available before creating the session.
    authenticate_profile(profile_name)

    try:
        return boto3.Session(
            profile_name=profile_name,
            region_name=region,
        )

    except ProfileNotFound as exc:
        raise ValueError(
            f"AWS profile '{profile_name}' was not found."
        ) from exc

    except BotoCoreError as exc:
        raise RuntimeError(
            f"Unable to create an AWS session for "
            f"profile '{profile_name}': {exc}"
        ) from exc


def get_region(
    profile_name: str,
    region: str | None = None,
) -> str | None:
    """
    Return the effective region for an AWS profile.

    An explicitly supplied region takes precedence.
    """
    if region:
        return region

    session = create_session(profile_name)

    return session.region_name