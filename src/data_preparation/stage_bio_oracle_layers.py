"""Validate one complete Bio-ORACLE raw run and copy it to interim unchanged.

This is a source-validation handoff, not scientific processing. It checks the
catalogue run and per-layer receipts, verifies each NetCDF payload while
copying, and replaces the stable interim phase only after the full new copy is
ready. The publisher-delivered raw files are never changed or removed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
RAW_BIO_ORACLE_ROOT = (ROOT / "data" / "raw" / "bio_oracle").resolve()
RAW_RUNS_ROOT = RAW_BIO_ORACLE_ROOT / "_runs"
INTERIM_BIO_ORACLE_ROOT = ROOT / "data" / "interim" / "bio_oracle"
OUTPUT_DIR = INTERIM_BIO_ORACLE_ROOT / "source_validation"
OUTPUT_MANIFEST_NAME = "manifest.json"
COPIED_RUN_MANIFEST_NAME = "catalog_run_manifest.json"
MANIFEST_FORMAT = "oceavera-bio-oracle-interim-source-validation-v1"

EXPECTED_LONGITUDE_BOUNDS = (77.02333333333333, 85.23291666666667)
EXPECTED_LATITUDE_BOUNDS = (2.5665, 11.44883333333333)
EXPECTED_TIME_BOUNDS = ("2000-01-01T00:00:00Z", "2100-01-01T00:00:00Z")
NETCDF_SIGNATURES = (b"CDF\x01", b"CDF\x02", b"CDF\x05", b"\x89HDF\r\n\x1a\n")
DATASET_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
ProgressReporter = Callable[[str], None]
DISK_SPACE_BUFFER_BYTES = 64 * 1024 * 1024


class StageError(Exception):
    """Raised when a Bio-ORACLE raw run cannot be safely staged."""


def format_bytes(byte_count: int) -> str:
    amount = float(byte_count)
    for unit in ("bytes", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            if unit == "bytes":
                return f"{byte_count:,} bytes"
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{byte_count:,} bytes"


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes, remaining_seconds = divmod(int(seconds), 60)
    return f"{minutes:,} min {remaining_seconds:02d} sec"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def resolve_run_manifest(value: str) -> Path:
    """Resolve a catalogue run manifest inside data/raw/bio_oracle/_runs."""
    if not RAW_BIO_ORACLE_ROOT.is_relative_to(ROOT.resolve()):
        raise StageError("The Bio-ORACLE raw folder resolves outside the repository")
    supplied = Path(value)
    candidate = supplied if supplied.is_absolute() else ROOT / supplied
    resolved = candidate.resolve()
    if resolved.parent != RAW_RUNS_ROOT:
        raise StageError(
            "The run manifest must be a direct child of the repository's "
            "data/raw/bio_oracle/_runs directory"
        )
    if resolved.suffix.lower() != ".json":
        raise StageError("The selected run manifest must have a .json extension")
    if not resolved.is_file():
        raise StageError(f"Run manifest does not exist or is not a file: {value}")
    return resolved


def resolve_raw_reference(value: Any, *, label: str) -> Path:
    """Resolve a manifest path and keep it within the Bio-ORACLE raw folder."""
    if not isinstance(value, str) or not value:
        raise StageError(f"The run manifest has no valid {label} path")
    supplied = Path(value)
    if supplied.is_absolute():
        raise StageError(f"The {label} path in the run manifest must be repository-relative")
    resolved = (ROOT / supplied).resolve()
    if not resolved.is_relative_to(RAW_BIO_ORACLE_ROOT):
        raise StageError(f"The {label} path escapes data/raw/bio_oracle")
    if not resolved.is_file():
        raise StageError(f"The {label} file is missing: {value}")
    return resolved


def read_json_bytes(path: Path, *, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StageError(f"Cannot read {label} JSON at {path}: {error}") from error
    if not isinstance(value, dict):
        raise StageError(f"{label} JSON must contain an object")
    return value, raw


def require_count(value: Any, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StageError(f"The run manifest has an invalid {field}")
    return value


def bounds_match(value: Any, expected: tuple[float, float], *, label: str) -> None:
    if not isinstance(value, list) or len(value) != 2:
        raise StageError(f"The {label} must contain exactly two bounds")
    try:
        actual = tuple(float(item) for item in value)
    except (TypeError, ValueError) as error:
        raise StageError(f"The {label} contains a non-numeric bound") from error
    if not all(
        math.isclose(a, b, rel_tol=0.0, abs_tol=1e-12)
        for a, b in zip(actual, expected)
    ):
        raise StageError(f"The run does not use the configured Sri Lanka {label}")


def validate_scope(run: dict[str, Any]) -> dict[str, Any]:
    region = run.get("region")
    if not isinstance(region, dict) or region.get("preset") != "sri-lanka-custom":
        raise StageError("The run is not for the selected Sri Lanka rectangle")

    longitude_bounds = run.get("requested_longitude_bounds_degrees_east")
    latitude_bounds = run.get("requested_latitude_bounds_degrees_north")
    bounds_match(longitude_bounds, EXPECTED_LONGITUDE_BOUNDS, label="longitude bounds")
    bounds_match(latitude_bounds, EXPECTED_LATITUDE_BOUNDS, label="latitude bounds")
    bounds_match(
        region.get("longitude_bounds_degrees_east"),
        EXPECTED_LONGITUDE_BOUNDS,
        label="region longitude bounds",
    )
    bounds_match(
        region.get("latitude_bounds_degrees_north"),
        EXPECTED_LATITUDE_BOUNDS,
        label="region latitude bounds",
    )

    time_bounds = run.get("requested_time_bounds_utc")
    if not isinstance(time_bounds, list) or tuple(time_bounds) != EXPECTED_TIME_BOUNDS:
        raise StageError("The run does not request the selected 2000 to 2100 time window")
    return {
        "region_preset": region["preset"],
        "longitude_bounds_degrees_east": list(EXPECTED_LONGITUDE_BOUNDS),
        "latitude_bounds_degrees_north": list(EXPECTED_LATITUDE_BOUNDS),
        "requested_time_bounds_utc": list(EXPECTED_TIME_BOUNDS),
    }


def validate_receipt(
    *,
    run: dict[str, Any],
    layer: dict[str, Any],
    dataset_id: str,
    payload_path: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    receipt, receipt_bytes = read_json_bytes(receipt_path, label=f"{dataset_id} receipt")
    if receipt.get("status") != "complete":
        raise StageError(f"The {dataset_id} layer receipt is not complete")
    receipt_run_id = receipt.get("catalog_run_id")
    if layer.get("status") == "complete":
        if receipt_run_id != run.get("catalog_run_id"):
            raise StageError(f"The {dataset_id} receipt belongs to a different catalogue run")
    elif layer.get("status") == "reused":
        if (
            not isinstance(receipt_run_id, str)
            or not receipt_run_id
            or receipt_run_id == run.get("catalog_run_id")
        ):
            raise StageError(
                f"The {dataset_id} reused receipt does not identify "
                "its original catalogue run"
            )
    else:
        raise StageError(f"The {dataset_id} run entry has an unsupported status")
    if receipt.get("dataset_id") != dataset_id:
        raise StageError(f"The {dataset_id} receipt has a mismatched dataset ID")

    payload_relative = layer["payload_location"]
    receipt_relative = layer["manifest_location"]
    if receipt.get("payload_location") != payload_relative:
        raise StageError(f"The {dataset_id} receipt points to a different payload")

    run_bytes = require_count(layer.get("response_bytes"), field=f"{dataset_id} response_bytes")
    run_hash = layer.get("sha256")
    if not isinstance(run_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", run_hash):
        raise StageError(f"The {dataset_id} run entry has an invalid SHA-256")
    download = receipt.get("download")
    if not isinstance(download, dict):
        raise StageError(f"The {dataset_id} receipt has no download details")
    if download.get("response_bytes") != run_bytes or download.get("sha256") != run_hash:
        raise StageError(f"The {dataset_id} run entry and receipt disagree on payload size or hash")
    if payload_path.stat().st_size != run_bytes:
        raise StageError(f"The {dataset_id} payload size does not match its run manifest")

    variables = layer.get("variables")
    if (
        not isinstance(variables, list)
        or not variables
        or any(not isinstance(name, str) or not name for name in variables)
        or len(set(variables)) != len(variables)
    ):
        raise StageError(f"The {dataset_id} run entry has an invalid variable list")
    receipt_variables = receipt.get("variables")
    query = receipt.get("query")
    if not isinstance(receipt_variables, dict) or set(receipt_variables) != set(variables):
        raise StageError(f"The {dataset_id} receipt variable list does not match the run")
    query_variables = query.get("variables") if isinstance(query, dict) else None
    if (
        not isinstance(query_variables, list)
        or any(not isinstance(name, str) for name in query_variables)
        or set(query_variables) != set(variables)
    ):
        raise StageError(f"The {dataset_id} query variable list does not match the run")

    query_longitude = query.get("requested_longitude_bounds_degrees_east")
    query_latitude = query.get("requested_latitude_bounds_degrees_north")
    bounds_match(query_longitude, EXPECTED_LONGITUDE_BOUNDS, label=f"{dataset_id} query longitude bounds")
    bounds_match(query_latitude, EXPECTED_LATITUDE_BOUNDS, label=f"{dataset_id} query latitude bounds")
    query_time = query.get("requested_time_bounds_utc")
    if query_time is not None and (
        not isinstance(query_time, list) or tuple(query_time) != EXPECTED_TIME_BOUNDS
    ):
        raise StageError(f"The {dataset_id} receipt has a different requested time window")
    if receipt.get("requested_time_range_utc") != list(EXPECTED_TIME_BOUNDS):
        raise StageError(f"The {dataset_id} receipt has a different requested time window")

    receipt_region = receipt.get("region")
    if not isinstance(receipt_region, dict):
        raise StageError(f"The {dataset_id} receipt has no collection region")
    bounds_match(
        receipt_region.get("longitude_bounds_degrees_east"),
        EXPECTED_LONGITUDE_BOUNDS,
        label=f"{dataset_id} receipt longitude bounds",
    )
    bounds_match(
        receipt_region.get("latitude_bounds_degrees_north"),
        EXPECTED_LATITUDE_BOUNDS,
        label=f"{dataset_id} receipt latitude bounds",
    )

    return {
        "dataset_id": dataset_id,
        "payload_path": payload_path,
        "receipt_path": receipt_path,
        "payload_relative": payload_relative,
        "receipt_relative": receipt_relative,
        "payload_bytes": run_bytes,
        "payload_sha256": run_hash,
        "variables": variables,
        "receipt_sha256": sha256_bytes(receipt_bytes),
        "receipt_bytes": receipt_bytes,
    }


def inspect_run(
    run_manifest_path: Path,
    *,
    progress: ProgressReporter | None = None,
) -> tuple[dict[str, Any], bytes, list[dict[str, Any]], dict[str, Any]]:
    run, run_bytes = read_json_bytes(run_manifest_path, label="catalogue run manifest")
    if isinstance(run.get("schema_version"), bool) or run.get("schema_version") != 1:
        raise StageError("The catalogue run manifest has an unsupported schema version")
    if run.get("status") != "complete":
        raise StageError(
            "Only a complete catalogue run can be staged; "
            f"the selected run is {run.get('status')!r}"
        )
    run_id = run.get("catalog_run_id")
    if not isinstance(run_id, str) or not run_id:
        raise StageError("The catalogue run manifest has no run ID")

    layers = run.get("layers")
    if not isinstance(layers, list) or not layers:
        raise StageError("The catalogue run manifest has no planned layers")
    planned = require_count(run.get("planned_layer_count"), field="planned_layer_count")
    completed = require_count(run.get("completed_layer_count"), field="completed_layer_count")
    failed = require_count(run.get("failed_layer_count"), field="failed_layer_count")
    pending = require_count(run.get("pending_layer_count"), field="pending_layer_count")
    if planned != len(layers) or completed != len(layers) or failed != 0 or pending != 0:
        raise StageError("Run layer counts do not describe a fully completed catalogue run")

    scope = validate_scope(run)
    prepared: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_payloads: set[Path] = set()
    for index, layer in enumerate(layers, start=1):
        if (
            not isinstance(layer, dict)
            or layer.get("status") not in {"complete", "reused"}
        ):
            raise StageError(
                "Every layer in the selected catalogue run must be complete or reused"
            )
        dataset_id = layer.get("dataset_id")
        if not isinstance(dataset_id, str) or not DATASET_ID_PATTERN.fullmatch(dataset_id):
            raise StageError("The run manifest contains an invalid dataset ID")
        if dataset_id in seen_ids:
            raise StageError(f"Duplicate dataset ID in run manifest: {dataset_id}")
        seen_ids.add(dataset_id)

        payload_path = resolve_raw_reference(layer.get("payload_location"), label=f"{dataset_id} payload")
        receipt_path = resolve_raw_reference(layer.get("manifest_location"), label=f"{dataset_id} receipt")
        if payload_path.parent.name != dataset_id or payload_path.suffix.lower() != ".nc":
            raise StageError(f"The {dataset_id} payload path is outside its expected layer folder")
        if receipt_path.parent != payload_path.parent or not receipt_path.name.endswith(".manifest.json"):
            raise StageError(f"The {dataset_id} receipt is not beside its payload")
        if payload_path in seen_payloads:
            raise StageError(f"Duplicate payload path in run manifest: {layer['payload_location']}")
        seen_payloads.add(payload_path)

        prepared_layer = validate_receipt(
            run=run,
            layer=layer,
            dataset_id=dataset_id,
            payload_path=payload_path,
            receipt_path=receipt_path,
        )
        prepared.append(prepared_layer)
        if progress is not None and (index % 25 == 0 or index == len(layers)):
            progress(f"Preflight: {index:,} of {len(layers):,} layer receipts checked.")

    return run, run_bytes, prepared, scope


def report_copy_progress(
    item: dict[str, Any],
    progress_state: dict[str, Any],
    *,
    force: bool = False,
) -> None:
    progress = progress_state["progress"]
    copied_bytes = progress_state["copied_bytes"]
    total_bytes = progress_state["total_bytes"]
    if progress is None or (
        not force
        and (
            copied_bytes < progress_state["next_report"]
            or copied_bytes >= total_bytes
        )
    ):
        return

    elapsed = max(time.perf_counter() - progress_state["started_at"], 0.001)
    rate = copied_bytes / elapsed
    remaining = max(total_bytes - copied_bytes, 0)
    eta = remaining / rate if rate else 0.0
    percent = 100 if total_bytes == 0 else min(100, round(copied_bytes * 100 / total_bytes))
    progress(
        f"Copy progress: {percent:3d}% | {format_bytes(copied_bytes)} of "
        f"{format_bytes(total_bytes)} | current layer {item['dataset_id']} "
        f"({format_bytes(progress_state['current_layer_bytes'])} of "
        f"{format_bytes(item['payload_bytes'])}) | "
        f"{format_bytes(int(rate))}/s | ETA {format_duration(eta)}."
    )
    while progress_state["next_report"] <= copied_bytes:
        progress_state["next_report"] += progress_state["report_interval"]


def estimate_required_space(
    payload_bytes: int,
    run_bytes: bytes,
    layers: list[dict[str, Any]],
) -> int:
    metadata_bytes = len(run_bytes) + sum(len(item["receipt_bytes"]) for item in layers)
    return payload_bytes + metadata_bytes + DISK_SPACE_BUFFER_BYTES


def check_available_space(required_bytes: int) -> int:
    space_check_path = INTERIM_BIO_ORACLE_ROOT
    while not space_check_path.exists() and space_check_path != space_check_path.parent:
        space_check_path = space_check_path.parent
    try:
        available_bytes = shutil.disk_usage(space_check_path).free
    except OSError as error:
        raise StageError(f"Could not check free space on the target drive: {error}") from error
    if available_bytes < required_bytes:
        raise StageError(
            "There is not enough free space on the target drive: "
            f"{format_bytes(available_bytes)} available, about "
            f"{format_bytes(required_bytes)} required (including the "
            f"{format_bytes(DISK_SPACE_BUFFER_BYTES)} safety buffer). "
            "Free space and run the command again."
        )
    return available_bytes


def copy_payload_verified(
    item: dict[str, Any],
    destination: Path,
    *,
    progress: ProgressReporter | None,
    progress_state: dict[str, int],
) -> None:
    source = item["payload_path"]
    expected_bytes = item["payload_bytes"]
    expected_hash = item["payload_sha256"]
    if source.stat().st_size != expected_bytes:
        raise StageError(f"The {item['dataset_id']} payload changed after preflight")

    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    copied_bytes = 0
    prefix = b""
    try:
        with source.open("rb") as source_stream, destination.open("xb") as output_stream:
            while True:
                chunk = source_stream.read(8 * 1024 * 1024)
                if not chunk:
                    break
                if not prefix:
                    prefix = chunk[:8]
                    if not any(prefix.startswith(signature) for signature in NETCDF_SIGNATURES):
                        raise StageError(f"The {item['dataset_id']} payload has no recognised NetCDF signature")
                written = output_stream.write(chunk)
                if written != len(chunk):
                    raise StageError(f"A short write occurred while staging {item['dataset_id']}")
                digest.update(chunk)
                copied_bytes += written
                progress_state["copied_bytes"] += written
                progress_state["current_layer_bytes"] = copied_bytes
                report_copy_progress(item, progress_state)
            output_stream.flush()
            os.fsync(output_stream.fileno())
    except OSError as error:
        raise StageError(f"Could not stage {item['dataset_id']}: {error}") from error

    copied_hash = digest.hexdigest()
    if copied_bytes != expected_bytes or copied_hash != expected_hash:
        raise StageError(f"The {item['dataset_id']} staged payload failed its size or SHA-256 check")
    if destination.stat().st_size != expected_bytes:
        raise StageError(f"The {item['dataset_id']} staged file has an unexpected size")
    if progress_state["copied_bytes"] == progress_state["total_bytes"]:
        report_copy_progress(item, progress_state, force=True)


def write_bytes_verified(content: bytes, destination: Path, expected_hash: str) -> None:
    if sha256_bytes(content) != expected_hash:
        raise StageError(f"Metadata fingerprint changed before staging: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb") as stream:
            written = stream.write(content)
            if written != len(content):
                raise StageError(f"A short write occurred while staging {destination.name}")
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise StageError(f"Could not stage metadata file {destination.name}: {error}") from error


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f"{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(value, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        temporary_path.replace(path)
        temporary_path = None
    except OSError as error:
        raise StageError(f"Could not write interim provenance manifest: {error}") from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def publish_staging_directory(temporary_dir: Path, *, progress: ProgressReporter | None) -> None:
    """Replace the stable output only after every staged file is verified."""
    backup_dir: Path | None = None
    if OUTPUT_DIR.is_symlink() or (OUTPUT_DIR.exists() and not OUTPUT_DIR.is_dir()):
        raise StageError(f"The stable output path is not a regular directory: {OUTPUT_DIR}")

    if OUTPUT_DIR.exists():
        backup_dir = Path(tempfile.mkdtemp(prefix=".source_validation.backup-", dir=INTERIM_BIO_ORACLE_ROOT))
        backup_dir.rmdir()
        OUTPUT_DIR.replace(backup_dir)
    try:
        temporary_dir.replace(OUTPUT_DIR)
    except OSError as error:
        if backup_dir is not None and backup_dir.exists() and not OUTPUT_DIR.exists():
            try:
                backup_dir.replace(OUTPUT_DIR)
            except OSError as restore_error:
                raise StageError(
                    "Could not publish the new interim folder or restore the previous one; "
                    f"the previous folder is preserved at {backup_dir}: {restore_error}"
                ) from error
        raise StageError(f"Could not publish the verified interim folder: {error}") from error

    if backup_dir is not None:
        try:
            shutil.rmtree(backup_dir)
        except OSError as error:
            if progress is not None:
                progress(
                    "Warning: the new interim folder is ready, but the previous verified "
                    f"phase copy remains at {backup_dir} because cleanup failed: {error}"
                )


def stage(
    run_manifest_path: Path,
    *,
    progress: ProgressReporter | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    if progress is not None:
        progress("Step 1 of 3: checking the selected run and layer receipts.")
    run, run_bytes, layers, scope = inspect_run(run_manifest_path, progress=progress)
    payload_bytes = sum(item["payload_bytes"] for item in layers)
    variable_count = sum(len(item["variables"]) for item in layers)
    run_hash = sha256_bytes(run_bytes)

    if (
        INTERIM_BIO_ORACLE_ROOT.is_symlink()
        or not INTERIM_BIO_ORACLE_ROOT.resolve().is_relative_to(ROOT.resolve())
    ):
        raise StageError("The Bio-ORACLE interim root must not be a symbolic link")
    if OUTPUT_DIR.is_symlink() or (OUTPUT_DIR.exists() and not OUTPUT_DIR.is_dir()):
        raise StageError(f"The stable output path is not a regular directory: {OUTPUT_DIR}")

    required_bytes = estimate_required_space(payload_bytes, run_bytes, layers)
    available_bytes = check_available_space(required_bytes)

    if progress is not None:
        progress(
            f"Preflight passed: run {run['catalog_run_id']}, {len(layers):,} layers, "
            f"{variable_count:,} variables and {format_bytes(payload_bytes)} of NetCDF payloads."
        )
        progress(
            "Scope: longitude "
            f"{scope['longitude_bounds_degrees_east'][0]:.8f} to "
            f"{scope['longitude_bounds_degrees_east'][1]:.8f}°E; latitude "
            f"{scope['latitude_bounds_degrees_north'][0]:.8f} to "
            f"{scope['latitude_bounds_degrees_north'][1]:.8f}°N; requested "
            f"{scope['requested_time_bounds_utc'][0]} to "
            f"{scope['requested_time_bounds_utc'][1]}."
        )
        progress(
            f"Disk check: {format_bytes(available_bytes)} free; about "
            f"{format_bytes(required_bytes)} required, including a "
            f"{format_bytes(DISK_SPACE_BUFFER_BYTES)} safety buffer."
        )

    if dry_run:
        return {
            "dry_run": True,
            "catalog_run_id": run["catalog_run_id"],
            "layer_count": len(layers),
            "variable_count": variable_count,
            "payload_bytes": payload_bytes,
            "required_bytes": required_bytes,
            "available_bytes": available_bytes,
        }

    INTERIM_BIO_ORACLE_ROOT.mkdir(parents=True, exist_ok=True)
    temporary_dir: Path | None = Path(
        tempfile.mkdtemp(prefix=".source_validation.", suffix=".tmp", dir=INTERIM_BIO_ORACLE_ROOT)
    )
    try:
        if progress is not None:
            progress("Step 2 of 3: copying each NetCDF payload and receipt unchanged.")
        write_bytes_verified(
            run_bytes,
            temporary_dir / COPIED_RUN_MANIFEST_NAME,
            run_hash,
        )
        progress_state: dict[str, Any] = {
            "copied_bytes": 0,
            "total_bytes": payload_bytes,
            "report_interval": max(100 * 1024 * 1024, (payload_bytes + 19) // 20),
            "started_at": time.perf_counter(),
            "current_layer_bytes": 0,
            "progress": progress,
        }
        progress_state["next_report"] = progress_state["report_interval"]

        staged_files: list[dict[str, Any]] = []
        for index, item in enumerate(layers, start=1):
            dataset_dir = temporary_dir / item["dataset_id"]
            staged_payload = dataset_dir / item["payload_path"].name
            staged_receipt = dataset_dir / item["receipt_path"].name
            progress_state["current_layer_bytes"] = 0
            copy_payload_verified(
                item,
                staged_payload,
                progress=progress,
                progress_state=progress_state,
            )
            write_bytes_verified(
                item["receipt_bytes"],
                staged_receipt,
                item["receipt_sha256"],
            )
            staged_files.append(
                {
                    "dataset_id": item["dataset_id"],
                    "source_payload": item["payload_relative"],
                    "staged_payload": (OUTPUT_DIR / item["dataset_id"] / staged_payload.name)
                    .relative_to(ROOT)
                    .as_posix(),
                    "source_receipt": item["receipt_relative"],
                    "staged_receipt": (OUTPUT_DIR / item["dataset_id"] / staged_receipt.name)
                    .relative_to(ROOT)
                    .as_posix(),
                    "bytes": item["payload_bytes"],
                    "sha256": item["payload_sha256"],
                    "variables": item["variables"],
                }
            )
            if progress is not None and (index % 25 == 0 or index == len(layers)):
                progress(f"Layers copied and verified: {index:,} of {len(layers):,}.")

        manifest = {
            "format": MANIFEST_FORMAT,
            "source_run": {
                "catalog_run_id": run["catalog_run_id"],
                "path": run_manifest_path.relative_to(ROOT).as_posix(),
                "staged_copy": (OUTPUT_DIR / COPIED_RUN_MANIFEST_NAME).relative_to(ROOT).as_posix(),
                "bytes": len(run_bytes),
                "sha256": run_hash,
            },
            "scope": scope,
            "operation": (
                "structural validation and byte-for-byte copy; no scientific cleaning, "
                "raster conversion or raw-file deletion"
            ),
            "layer_count": len(layers),
            "variable_count": variable_count,
            "payload_bytes": payload_bytes,
            "layers": staged_files,
        }
        if progress is not None:
            progress("Step 3 of 3: writing provenance and publishing the stable interim folder.")
        write_json_atomic(temporary_dir / OUTPUT_MANIFEST_NAME, manifest)
        publish_staging_directory(temporary_dir, progress=progress)
        temporary_dir = None
        return manifest
    finally:
        if temporary_dir is not None and temporary_dir.exists():
            shutil.rmtree(temporary_dir, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a complete Bio-ORACLE catalogue run and stage an unchanged "
            "copy at the stable interim source-validation path"
        ),
        epilog=(
            "Example (run from the repository root):\n"
            "  python src/data_preparation/stage_bio_oracle_layers.py "
            "--run-manifest data/raw/bio_oracle/_runs/<complete-run>_bio_oracle_catalog.json\n\n"
            "Raw data are preserved. The selected run must use the D-048 Sri Lanka "
            "rectangle and request the 2000 to 2100 time window. Use --dry-run to "
            "check the run, receipts and free space without writing files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--run-manifest",
        required=True,
        help="complete catalogue run manifest inside data/raw/bio_oracle/_runs/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "check run metadata, layer receipts, file sizes and free space without "
            "copying files; NetCDF payload bytes are not read or hashed"
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    started_at = time.perf_counter()
    print("OCEAVERA | Bio-ORACLE raw-to-interim handoff")
    print(f"Selected run manifest: {args.run_manifest}")
    print(f"Stable output: {OUTPUT_DIR.relative_to(ROOT).as_posix()}")
    print("Raw data are preserved; the interim folder is published after all payloads pass verification.")
    if args.dry_run:
        print("Mode: dry run (metadata and file-size checks only; no files will be written).")

    def show_progress(message: str) -> None:
        print(f"[INFO] {message}", flush=True)

    try:
        run_manifest_path = resolve_run_manifest(args.run_manifest)
        result = stage(run_manifest_path, progress=show_progress, dry_run=args.dry_run)
    except (OSError, StageError) as error:
        print(f"\n[ERROR] Bio-ORACLE staging did not complete: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("\n[OK] Dry run passed. No files were written and no NetCDF payload bytes were read.")
        print(f"  Catalogue run: {result['catalog_run_id']}")
        print(f"  Layers: {result['layer_count']:,}")
        print(f"  Variables: {result['variable_count']:,}")
        print(f"  NetCDF payloads: {format_bytes(result['payload_bytes'])}")
        print(f"  Estimated space required: {format_bytes(result['required_bytes'])}")
        print(f"  Available space: {format_bytes(result['available_bytes'])}")
        print("  Next step: rerun the same command without --dry-run to copy and verify the layers.")
        print(f"  Elapsed: {format_duration(time.perf_counter() - started_at)}")
        return 0

    print("\n[OK] Bio-ORACLE layers staged and verified.")
    print(f"  Catalogue run: {result['source_run']['catalog_run_id']}")
    print(f"  Layers: {result['layer_count']:,}")
    print(f"  Variables: {result['variable_count']:,}")
    print(f"  NetCDF payloads: {format_bytes(result['payload_bytes'])}")
    print(f"  Output: {OUTPUT_DIR.relative_to(ROOT).as_posix()}")
    print(f"  Manifest: {(OUTPUT_DIR / OUTPUT_MANIFEST_NAME).relative_to(ROOT).as_posix()}")
    print(f"  Elapsed: {format_duration(time.perf_counter() - started_at)}")
    print("  Data handling: byte-for-byte copies; raw files were not changed or removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
