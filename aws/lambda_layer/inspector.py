from __future__ import annotations

import io
import json
import urllib.request
import zipfile
from dataclasses import dataclass
from email.parser import Parser
from typing import Any


MANIFEST_PATH = "python/_aws_workbench_manifest.json"


@dataclass
class LayerInspectionResult:
    layer_name: str
    version: int

    runtime: str | None
    architecture: str | None

    packages: list[str]

    managed_by_workbench: bool
    manifest_found: bool


def _download_layer_zip(download_url: str) -> bytes:
    try:
        with urllib.request.urlopen(
            download_url,
            timeout=120,
        ) as response:
            return response.read()

    except Exception as exc:
        raise RuntimeError(
            f"Failed to download Lambda layer ZIP: {exc}"
        ) from exc


def _read_manifest(
    archive: zipfile.ZipFile,
) -> dict[str, Any] | None:
    try:
        raw = archive.read(MANIFEST_PATH)

    except KeyError:
        return None

    try:
        manifest = json.loads(
            raw.decode("utf-8")
        )

    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(manifest, dict):
        return None

    if manifest.get("managed_by") != "aws-workbench":
        return None

    if manifest.get("schema_version") != 1:
        return None

    packages = manifest.get("packages")

    if not isinstance(packages, list):
        return None

    if not all(
        isinstance(package, str)
        for package in packages
    ):
        return None

    return manifest


def _discover_packages(
    archive: zipfile.ZipFile,
) -> list[str]:
    packages: set[str] = set()

    for name in archive.namelist():
        if not name.startswith("python/"):
            continue

        if not name.endswith(".dist-info/METADATA"):
            continue

        try:
            raw = archive.read(name)

        except KeyError:
            continue

        try:
            metadata_text = raw.decode(
                "utf-8",
                errors="replace",
            )
            metadata = Parser().parsestr(
                metadata_text
            )

        except Exception:
            continue

        package_name = metadata.get("Name")
        package_version = metadata.get("Version")

        if not package_name or not package_version:
            continue

        packages.add(
            f"{package_name}=={package_version}"
        )

    return sorted(packages, key=str.lower)


def inspect_layer_zip(
    zip_bytes: bytes,
    layer_name: str,
    version: int,
    runtime: str | None = None,
    architecture: str | None = None,
) -> LayerInspectionResult:
    with zipfile.ZipFile(
        io.BytesIO(zip_bytes),
        "r",
    ) as archive:

        manifest = _read_manifest(archive)

        if manifest:
            packages = sorted(
                manifest["packages"],
                key=str.lower,
            )

            manifest_runtime = manifest.get(
                "runtime"
            )

            manifest_architecture = manifest.get(
                "architecture"
            )

            return LayerInspectionResult(
                layer_name=layer_name,
                version=version,
                runtime=(
                    manifest_runtime
                    if isinstance(
                        manifest_runtime,
                        str,
                    )
                    else runtime
                ),
                architecture=(
                    manifest_architecture
                    if isinstance(
                        manifest_architecture,
                        str,
                    )
                    else architecture
                ),
                packages=packages,
                managed_by_workbench=True,
                manifest_found=True,
            )

        packages = _discover_packages(
            archive
        )

        return LayerInspectionResult(
            layer_name=layer_name,
            version=version,
            runtime=runtime,
            architecture=architecture,
            packages=packages,
            managed_by_workbench=False,
            manifest_found=False,
        )


def inspect_layer_version(
    session: Any,
    layer_name: str,
    version: int,
) -> LayerInspectionResult:
    lambda_client = session.client("lambda")

    try:
        response = lambda_client.get_layer_version(
            LayerName=layer_name,
            VersionNumber=version,
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to inspect Lambda layer "
            f"'{layer_name}:{version}': {exc}"
        ) from exc

    content = response.get("Content", {})
    download_url = content.get("Location")

    if not download_url:
        raise RuntimeError(
            "Lambda layer version did not return "
            "a downloadable Content.Location URL."
        )

    compatible_runtimes = response.get(
        "CompatibleRuntimes",
        [],
    )

    compatible_architectures = response.get(
        "CompatibleArchitectures",
        [],
    )

    runtime = (
        compatible_runtimes[0]
        if compatible_runtimes
        else None
    )

    architecture = (
        compatible_architectures[0]
        if compatible_architectures
        else None
    )

    zip_bytes = _download_layer_zip(
        download_url
    )

    return inspect_layer_zip(
        zip_bytes=zip_bytes,
        layer_name=layer_name,
        version=version,
        runtime=runtime,
        architecture=architecture,
    )