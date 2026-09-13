from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound


@dataclass(frozen=True)
class AWSProfile:
    """Information about an AWS CLI profile."""

    name: str
    account_id: str | None = None
    role_name: str | None = None
    sso_session: str | None = None
    region: str | None = None
    auth_type: str = "unknown"
    authenticated: bool = False


def _aws_config_path() -> Path:
    """Return the path to the local AWS CLI config file."""
    return Path.home() / ".aws" / "config"


def _load_aws_config() -> ConfigParser:
    """Load the local AWS CLI configuration."""
    config = ConfigParser()
    config.read(_aws_config_path())
    return config


def _detect_auth_type(
    config: ConfigParser,
    section: str,
) -> str:
    """Detect the configured authentication mechanism for a profile."""

    if config.has_option(section, "sso_session"):
        return "sso"

    if config.has_option(section, "sso_start_url"):
        return "sso"

    if config.has_option(section, "credential_process"):
        return "credential_process"

    if config.has_option(section, "role_arn"):
        return "role"

    if config.has_option(section, "aws_access_key_id"):
        return "static_credentials"

    return "unknown"


def list_profiles() -> list[AWSProfile]:
    """
    Return all AWS CLI profiles available on the local machine.

    Authentication is not performed here.
    """
    session = boto3.Session()
    available_profiles = session.available_profiles
    config = _load_aws_config()

    profiles: list[AWSProfile] = []

    for profile_name in sorted(available_profiles):
        section = (
            f"profile {profile_name}"
            if profile_name != "default"
            else "default"
        )

        if config.has_section(section):
            profiles.append(
                AWSProfile(
                    name=profile_name,
                    account_id=config.get(
                        section,
                        "sso_account_id",
                        fallback=None,
                    ),
                    role_name=config.get(
                        section,
                        "sso_role_name",
                        fallback=None,
                    ),
                    sso_session=config.get(
                        section,
                        "sso_session",
                        fallback=None,
                    ),
                    region=config.get(
                        section,
                        "region",
                        fallback=None,
                    ),
                    auth_type=_detect_auth_type(
                        config,
                        section,
                    ),
                )
            )
        else:
            profiles.append(
                AWSProfile(name=profile_name)
            )

    return profiles


def profile_exists(profile_name: str) -> bool:
    """Check whether an AWS CLI profile exists locally."""
    return profile_name in boto3.Session().available_profiles


def get_profile(profile_name: str) -> AWSProfile:
    """Return metadata for a configured AWS CLI profile."""

    for profile in list_profiles():
        if profile.name == profile_name:
            return profile

    raise ProfileNotFound(profile=profile_name)


def get_profile_identity(profile_name: str) -> AWSProfile:
    """
    Resolve the AWS identity associated with a profile.

    Boto3 handles the configured authentication mechanism,
    whether it is SSO, credentials, role assumption,
    credential_process, or another supported mechanism.
    """
    profile = get_profile(profile_name)

    session = boto3.Session(profile_name=profile_name)
    sts = session.client("sts")

    identity = sts.get_caller_identity()

    return AWSProfile(
        name=profile.name,
        account_id=identity.get(
            "Account",
            profile.account_id,
        ),
        role_name=profile.role_name,
        sso_session=profile.sso_session,
        region=profile.region,
        auth_type=profile.auth_type,
        authenticated=True,
    )


def check_profile(profile_name: str) -> tuple[bool, str]:
    """
    Check whether an AWS profile can currently be used.

    Returns:
        A tuple containing:
        - True/False indicating whether the profile is usable.
        - A human-readable status message.
    """
    if not profile_exists(profile_name):
        return False, (
            f"AWS profile '{profile_name}' was not found "
            "in the local AWS CLI configuration."
        )

    try:
        profile = get_profile_identity(profile_name)

        return True, (
            f"Authenticated successfully. "
            f"Account: {profile.account_id}, "
            f"Authentication: {profile.auth_type}, "
            f"Role: {profile.role_name or 'N/A'}"
        )

    except ProfileNotFound:
        return False, (
            f"AWS profile '{profile_name}' was not found."
        )

    except ClientError as exc:
        error = exc.response.get("Error", {})
        code = error.get("Code", "Unknown")
        message = error.get("Message", str(exc))

        return False, (
            f"Profile '{profile_name}' is configured, but AWS "
            f"authentication is unavailable. {code}: {message}"
        )

    except BotoCoreError as exc:
        return False, (
            f"Profile '{profile_name}' could not be used: {exc}"
        )


def get_profile_account_id(profile_name: str) -> str:
    """Return the AWS account ID associated with a usable profile."""

    profile = get_profile_identity(profile_name)

    if profile.account_id is None:
        raise RuntimeError(
            f"Unable to determine AWS account ID "
            f"for profile '{profile_name}'."
        )

    return profile.account_id