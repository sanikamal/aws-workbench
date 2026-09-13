from __future__ import annotations

import subprocess

from botocore.exceptions import BotoCoreError, ClientError, TokenRetrievalError

from core.aws_profiles import (
    AWSProfile,
    get_profile,
    get_profile_identity,
)


def login_sso(profile_name: str) -> None:
    """
    Start AWS SSO login for the specified AWS CLI profile.

    The AWS CLI handles the browser-based SSO authentication.
    """
    profile = get_profile(profile_name)

    if profile.auth_type != "sso":
        raise RuntimeError(
            f"Profile '{profile_name}' does not use AWS SSO."
        )

    try:
        subprocess.run(
            [
                "aws",
                "sso",
                "login",
                "--profile",
                profile_name,
            ],
            check=True,
        )

    except FileNotFoundError as exc:
        raise RuntimeError(
            "AWS CLI was not found. Please install AWS CLI "
            "and make sure 'aws' is available in PATH."
        ) from exc

    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"AWS SSO login failed for profile "
            f"'{profile_name}' with exit code {exc.returncode}."
        ) from exc


def authenticate_profile(profile_name: str) -> AWSProfile:
    """
    Authenticate an AWS profile.

    If the profile uses SSO and its cached token has expired,
    automatically start AWS SSO login and retry authentication.

    Returns:
        Authenticated AWS profile information.
    """
    profile = get_profile(profile_name)

    try:
        return get_profile_identity(profile_name)

    except TokenRetrievalError:
        if profile.auth_type != "sso":
            raise

        print(
            f"\nAWS SSO session for '{profile_name}' has expired."
        )
        print("Starting AWS SSO login...\n")

        login_sso(profile_name)

        print(
            f"\nSSO login successful for '{profile_name}'."
        )
        print("Retrying AWS authentication...\n")

        return get_profile_identity(profile_name)

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Unable to authenticate AWS profile "
            f"'{profile_name}': {exc}"
        ) from exc


def ensure_authenticated(profile_name: str) -> bool:
    """
    Ensure an AWS profile is authenticated.

    Returns:
        True when authentication succeeds.
    """
    authenticate_profile(profile_name)
    return True