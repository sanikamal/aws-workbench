from __future__ import annotations

import json
import shlex
import time
import uuid
from typing import Any

from botocore.exceptions import ClientError

CODEBUILD_ROLE_NAME = "aws-workbench-codebuild-lambda-layer"
INLINE_POLICY_NAME = "aws-workbench-lambda-layer-build"

_RUNTIME_VERSIONS = {
    "python3.10": "310",
    "python3.11": "311",
    "python3.12": "312",
    "python3.13": "313",
    "python3.14": "314",
}


def _platform_for(architecture: str) -> tuple[str, str, str]:
    if architecture == "arm64":
        return (
            "ARM_CONTAINER",
            "aws/codebuild/amazonlinux2-aarch64-standard:3.0",
            "manylinux2014_aarch64",
        )
    if architecture == "x86_64":
        return (
            "LINUX_CONTAINER",
            "aws/codebuild/standard:7.0",
            "manylinux2014_x86_64",
        )
    raise ValueError(f"Unsupported architecture: {architecture}")


def _python_version(runtime: str) -> str:
    try:
        return _RUNTIME_VERSIONS[runtime]
    except KeyError as exc:
        raise ValueError(f"Unsupported Python runtime: {runtime}") from exc


def generate_project_name(layer_name: str) -> str:
    safe_name = "".join(
        ch if ch.isalnum() or ch in "-_" else "-" for ch in layer_name
    ).strip("-") or "layer"
    return f"aws-workbench-layer-{safe_name[:35]}-{uuid.uuid4().hex[:8]}"


def _role_trust_policy() -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "codebuild.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }


def ensure_codebuild_role(
    session: Any,
    bucket_name: str,
) -> str:
    """Create/reuse the CodeBuild role and scope its S3 access to one temp bucket."""
    iam = session.client("iam")
    # bucket_arn = f"arn:aws:s3:::{bucket_name}"
    # object_arn = f"{bucket_arn}/*"
    bucket_arn = "arn:aws:s3:::aws-workbench-layer-*"
    object_arn = "arn:aws:s3:::aws-workbench-layer-*/*"

    try:
        role = iam.get_role(RoleName=CODEBUILD_ROLE_NAME)["Role"]
        role_arn = role["Arn"]
    except iam.exceptions.NoSuchEntityException:
        role = iam.create_role(
            RoleName=CODEBUILD_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(_role_trust_policy()),
            Description="AWS Workbench CodeBuild role for Lambda layer builds",
        )["Role"]
        role_arn = role["Arn"]
        # IAM can take a few seconds before the new role can be assumed.
        time.sleep(5)

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": bucket_arn,
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:PutObject",
                    "s3:DeleteObject",
                ],
                "Resource": object_arn,
            },
        ],
    }

    iam.put_role_policy(
        RoleName=CODEBUILD_ROLE_NAME,
        PolicyName=INLINE_POLICY_NAME,
        PolicyDocument=json.dumps(policy),
    )
    return role_arn


def get_buildspec(
    packages: list[str],
    runtime: str,
    architecture: str,
    bucket_name: str,
    object_key: str,
    metadata_key: str,
) -> str:
    python_version = _python_version(runtime)
    _, _, wheel_platform = _platform_for(architecture)

    package_args = " ".join(
        shlex.quote(package)
        for package in packages
    )

    bucket = shlex.quote(bucket_name)
    object_key_q = shlex.quote(object_key)
    metadata_key_q = shlex.quote(metadata_key)

    manifest = {
        "schema_version": 1,
        "packages": packages,
        "runtime": runtime,
        "architecture": architecture,
        "managed_by": "aws-workbench",
    }

    manifest_json = json.dumps(
        manifest,
        separators=(",", ":"),
    )
    manifest_json_q = shlex.quote(manifest_json)

    commands = [
        "set -e",

        "rm -rf python layer.zip metadata.json",

        "mkdir -p python",

        (
            "python3 -m pip install "
            "--disable-pip-version-check "
            "--no-cache-dir "
            f"--platform {wheel_platform} "
            "--implementation cp "
            f"--python-version {python_version} "
            "--only-binary=:all: "
            "--upgrade "
            f"--target python {package_args}"
        ),

        # Workbench metadata embedded inside the actual Lambda layer.
        (
            f"printf '%s\\n' {manifest_json_q} "
            "> python/_aws_workbench_manifest.json"
        ),

        "uncompressed_bytes=$(du -sb python | awk '{print $1}')",

        'export UNCOMPRESSED_BYTES="$uncompressed_bytes"',

        (
            'if [ "$uncompressed_bytes" -gt 262144000 ]; then '
            "echo 'Layer exceeds 250 MB uncompressed'; "
            "exit 1; "
            "fi"
        ),

        "zip -q -r9 layer.zip python",

        "compressed_bytes=$(stat -c%s layer.zip)",

        'export COMPRESSED_BYTES="$compressed_bytes"',

        (
            "python3 -c "
            "'import json, os; "
            "json.dump("
            "{\"uncompressed_bytes\": "
            "int(os.environ[\"UNCOMPRESSED_BYTES\"]), "
            "\"compressed_bytes\": "
            "int(os.environ[\"COMPRESSED_BYTES\"])}"
            ", open(\"metadata.json\", \"w\"))'"
        ),

        f"aws s3 cp layer.zip s3://{bucket}/{object_key_q}",

        f"aws s3 cp metadata.json s3://{bucket}/{metadata_key_q}",
    ]

    return json.dumps(
        {
            "version": 0.2,
            "phases": {
                "build": {
                    "commands": commands,
                }
            },
            "artifacts": {
                "files": [
                    "layer.zip",
                    "metadata.json",
                ]
            },
        }
    )


def create_codebuild_project(
    client: Any,
    project_name: str,
    service_role_arn: str,
    bucket_name: str,
    object_key: str,
    metadata_key: str,
    packages: list[str],
    runtime: str,
    architecture: str,
) -> None:
    container_type, image, _ = _platform_for(architecture)
    buildspec = get_buildspec(
        packages,
        runtime,
        architecture,
        bucket_name,
        object_key,
        metadata_key,
    )

    client.create_project(
        name=project_name,
        description="Temporary AWS Workbench Lambda Layer build",
        source={"type": "NO_SOURCE", "buildspec": buildspec},
        artifacts={"type": "NO_ARTIFACTS"},
        environment={
            "type": container_type,
            "image": image,
            "computeType": "BUILD_GENERAL1_SMALL",
            "imagePullCredentialsType": "CODEBUILD",
            "privilegedMode": False,
        },
        serviceRole=service_role_arn,
        timeoutInMinutes=30,
    )


def start_build(client: Any, project_name: str) -> str:
    return client.start_build(projectName=project_name)["build"]["id"]


def wait_for_build(client: Any, build_id: str, poll_seconds: int = 5) -> None:
    while True:
        response = client.batch_get_builds(ids=[build_id])
        builds = response.get("builds", [])
        if not builds:
            raise RuntimeError(f"CodeBuild build '{build_id}' was not found.")

        build = builds[0]
        status = build["buildStatus"]
        phase = build.get("currentPhase", "")
        print(f"  CodeBuild: {status} {phase}")

        if status == "SUCCEEDED":
            return

        if status in {"FAILED", "FAULT", "STOPPED", "TIMED_OUT"}:
            logs = build.get("logs", {})
            deep_link = logs.get("deepLink")
            message = f"CodeBuild failed with status: {status}"
            if deep_link:
                message += f"\nBuild logs: {deep_link}"
            raise RuntimeError(message)

        time.sleep(poll_seconds)


def delete_codebuild_project(client: Any, project_name: str) -> None:
    try:
        client.delete_project(name=project_name)
    except ClientError:
        pass
