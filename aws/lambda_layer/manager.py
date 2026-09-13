from __future__ import annotations

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError


def get_account_layers(
    session: Any,
    region: str,
) -> list[str]:
    """Fetch all Lambda layer names in the specified account and region."""
    lambda_client = session.client(
        "lambda",
        region_name=region,
    )

    layers: list[str] = []

    try:
        paginator = lambda_client.get_paginator(
            "list_layers"
        )

        for page in paginator.paginate():
            for layer in page.get("Layers", []):
                layer_name = layer.get("LayerName")

                if layer_name:
                    layers.append(layer_name)

        return sorted(layers)

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Unable to list Lambda layers: {exc}"
        ) from exc


def get_layer_versions(
    session: Any,
    layer_name: str,
    region: str,
) -> list[dict[str, Any]]:
    """Fetch all versions for a specific Lambda layer."""
    lambda_client = session.client(
        "lambda",
        region_name=region,
    )

    try:
        paginator = lambda_client.get_paginator(
            "list_layer_versions"
        )

        versions: list[dict[str, Any]] = []

        for page in paginator.paginate(
            LayerName=layer_name
        ):
            versions.extend(
                page.get("Versions", [])
            )

        # Never depend on API response ordering.
        versions.sort(
            key=lambda item: item.get("Version", 0),
            reverse=True,
        )

        return versions

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Unable to list versions for "
            f"'{layer_name}': {exc}"
        ) from exc


def delete_layer_version(
    session: Any,
    layer_name: str,
    version: int,
    region: str,
) -> None:
    """Delete a specific version of a Lambda layer."""
    lambda_client = session.client(
        "lambda",
        region_name=region,
    )

    try:
        lambda_client.delete_layer_version(
            LayerName=layer_name,
            VersionNumber=version,
        )

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Failed to delete layer "
            f"'{layer_name}' v{version}: {exc}"
        ) from exc