"""Download Bio-ORACLE v3 layers for the fixed Sri Lankan EEZ-extrema rectangle."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import json
import math
import re
import sys
import time
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ERDDAP_ROOT = "https://erddap.bio-oracle.org/erddap"
ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "data" / "raw" / "bio_oracle"
METADATA_CACHE_ROOT = RAW_ROOT / "catalogue_metadata"
TIMEOUT_SECONDS = 90
MAX_ATTEMPTS = 3
MAX_METADATA_BYTES = 8 * 1024 * 1024
MAX_DATA_BYTES = 512 * 1024 * 1024
DOWNLOAD_WORKERS = 4
CHUNK_SIZE = 1024 * 1024
NETCDF_SIGNATURES = (b"CDF\x01", b"CDF\x02", b"CDF\x05", b"\x89HDF\r\n\x1a\n")
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")
SAFE_VARIABLE = re.compile(r"^[A-Za-z0-9_]+$")
CATALOG_COLUMNS = (
    "datasetID",
    "accessible",
    "dataStructure",
    "title",
    "summary",
    "sourceUrl",
    "minLongitude",
    "maxLongitude",
    "minLatitude",
    "maxLatitude",
    "minTime",
    "maxTime",
    "griddap",
)
COLLECTION_TIME_BOUNDS_UTC = (
    "2000-01-01T00:00:00Z",
    "2100-01-01T00:00:00Z",
)
LONGITUDE_BOUNDS_DEGREES_EAST = (77.02333333333333, 85.23291666666667)
LATITUDE_BOUNDS_DEGREES_NORTH = (2.5665, 11.44883333333333)
WEST, EAST = LONGITUDE_BOUNDS_DEGREES_EAST
SOUTH, NORTH = LATITUDE_BOUNDS_DEGREES_NORTH
REGION = {
    "preset": "sri-lanka-custom",
    "name": "Sri Lanka rectangle from Marine Regions EEZ v12 extrema",
    "source": "Flanders Marine Institute (2023), Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12",
    "source_resource_id": "Marine Regions MRGID 8346",
    "source_doi": "10.14284/632",
    "source_url": "https://www.marineregions.org/gazetteer.php?id=8346&p=details",
    "methodology_url": "https://www.marineregions.org/eezmethodology.php",
    "longitude_bounds_degrees_east": list(LONGITUDE_BOUNDS_DEGREES_EAST),
    "latitude_bounds_degrees_north": list(LATITUDE_BOUNDS_DEGREES_NORTH),
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [WEST, SOUTH],
            [EAST, SOUTH],
            [EAST, NORTH],
            [WEST, NORTH],
            [WEST, SOUTH],
        ]],
    },
    "interpretation": (
        "Axis-aligned rectangle made from the Sri Lankan EEZ feature's published "
        "extrema. It is not the irregular EEZ polygon; no marine or EEZ mask is applied."
    ),
}


class IntakeError(Exception):
    """Raised when the publisher response cannot be safely inspected or saved."""


class RetryableDownloadError(IntakeError):
    """Raised when a publisher response may succeed if requested again."""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def request_bytes(
    url: str,
    *,
    limit: int,
    timeout_seconds: int = TIMEOUT_SECONDS,
    max_attempts: int = MAX_ATTEMPTS,
) -> tuple[bytes, dict[str, Any]]:
    """Fetch a bounded response, retrying transient ERDDAP errors."""
    last_error = "unknown request failure"
    for attempt in range(1, max_attempts + 1):
        try:
            request = Request(
                url,
                headers={
                    "Accept": "application/json, application/x-netcdf, */*",
                    "User-Agent": "OCEAVERA Bio-ORACLE data intake",
                },
            )
            with urlopen(request, timeout=timeout_seconds) as response:
                status = response.status
                content_type = response.headers.get("Content-Type", "")
                content_length = response.headers.get("Content-Length")
                chunks: list[bytes] = []
                received = 0
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    received += len(chunk)
                    if received > limit:
                        raise IntakeError(
                            f"Publisher response exceeded the {limit:,}-byte limit."
                        )
                    chunks.append(chunk)
            return b"".join(chunks), {
                "http_status": status,
                "content_type": content_type,
                "content_length_header": content_length,
                "response_bytes": received,
                "attempts": attempt,
            }
        except IncompleteRead as error:
            last_error = (
                "Bio-ORACLE ERDDAP ended the response early "
                f"({len(error.partial):,} bytes in the incomplete read)"
            )
            retryable = True
        except HTTPError as error:
            last_error = f"HTTP {error.code} from Bio-ORACLE ERDDAP"
            retryable = error.code == 429 or error.code >= 500
        except URLError as error:
            last_error = f"publisher endpoint request failed: {error.reason}"
            retryable = True
        except (TimeoutError, OSError) as error:
            last_error = f"{type(error).__name__}: {error}"
            retryable = True

        if not retryable or attempt == max_attempts:
            raise IntakeError(last_error)
        time.sleep(2 ** (attempt - 1))

    raise IntakeError(last_error)


def metadata_table(document: Any) -> list[dict[str, str]]:
    """Convert ERDDAP's JSON table response to named rows."""
    if not isinstance(document, dict) or not isinstance(document.get("table"), dict):
        raise IntakeError("ERDDAP returned an unrecognised JSON metadata response.")
    table = document["table"]
    columns = table.get("columnNames")
    rows = table.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        raise IntakeError("ERDDAP metadata is missing its table columns or rows.")
    return [
        {
            str(column): "" if value is None else str(value)
            for column, value in zip(columns, row, strict=False)
        }
        for row in rows
        if isinstance(row, list)
    ]


def dataset_catalog() -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Read the publisher's active-dataset catalogue without fetching grids."""
    columns = quote(",".join(CATALOG_COLUMNS), safe=",")
    url = f"{ERDDAP_ROOT}/tabledap/allDatasets.json?{columns}"
    body, response = request_bytes(url, limit=MAX_METADATA_BYTES)
    try:
        rows = metadata_table(json.loads(body.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IntakeError(f"Could not parse ERDDAP catalogue JSON: {error}") from error
    missing = set(CATALOG_COLUMNS) - (set(rows[0]) if rows else set())
    if missing:
        raise IntakeError(
            "ERDDAP catalogue omitted required columns: " + ", ".join(sorted(missing))
        )
    return rows, {
        "url": url,
        **response,
                "sha256": hashlib.sha256(body).hexdigest(),
        "retrieved_at_utc": now_utc(),
    }


def layer_metadata(dataset_id: str, *, use_cache: bool = False) -> dict[str, Any]:
    if not SAFE_ID.fullmatch(dataset_id):
        raise IntakeError("Dataset IDs may contain only letters, digits, underscores and hyphens.")
    cache_path = METADATA_CACHE_ROOT / f"{dataset_id}.json"
    if use_cache and cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if (
                isinstance(cached, dict)
                and cached.get("dataset_id") == dataset_id
                and isinstance(cached.get("variables"), dict)
                and isinstance(cached.get("dimensions"), dict)
                and isinstance(cached.get("response"), dict)
            ):
                cached["variables"] = {
                    name: tuple(dimensions)
                    for name, dimensions in cached["variables"].items()
                }
                cached["metadata_cache_reused"] = True
                return cached
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass

    url = f"{ERDDAP_ROOT}/info/{dataset_id}/index.json"
    body, response = request_bytes(
        url, limit=MAX_METADATA_BYTES, timeout_seconds=30, max_attempts=2
    )
    try:
        rows = metadata_table(json.loads(body.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IntakeError(f"Could not parse ERDDAP metadata JSON: {error}") from error

    global_attributes: dict[str, str] = {}
    dimensions: dict[str, dict[str, Any]] = {}
    attributes_by_name: dict[str, dict[str, str]] = {}
    variables: dict[str, tuple[str, ...]] = {}
    for row in rows:
        row_type = row.get("Row Type", "").casefold()
        name = row.get("Variable Name", "")
        if row_type == "dimension":
            values: dict[str, str] = {}
            for part in row.get("Value", "").split(","):
                key, separator, value = part.partition("=")
                if separator:
                    values[key.strip()] = value.strip()
            dimensions[name] = {"metadata": values, "attributes": {}}
        elif row_type == "attribute":
            attribute_name = row.get("Attribute Name", "")
            value = row.get("Value", "")
            if name == "NC_GLOBAL":
                global_attributes[attribute_name] = value
            else:
                attributes_by_name.setdefault(name, {})[attribute_name] = value
        elif row_type == "variable":
            variables[name] = tuple(
                dimension.strip()
                for dimension in row.get("Value", "").split(",")
                if dimension.strip()
            )

    variable_attributes: dict[str, dict[str, str]] = {}
    for name, attributes in attributes_by_name.items():
        if name in dimensions:
            dimensions[name]["attributes"].update(attributes)
        else:
            variable_attributes[name] = attributes

    if not variables or not dimensions:
        raise IntakeError("ERDDAP metadata did not describe any grid variables and dimensions.")
    result = {
        "dataset_id": dataset_id,
        "metadata_url": url,
        "response": {
            **response,
            "sha256": hashlib.sha256(body).hexdigest(),
            "retrieved_at_utc": now_utc(),
        },
        "global_attributes": global_attributes,
        "dimensions": dimensions,
        "variables": variables,
        "variable_attributes": variable_attributes,
        "metadata_cache_reused": False,
    }
    if use_cache:
        try:
            METADATA_CACHE_ROOT.mkdir(parents=True, exist_ok=True)
            temporary_path = cache_path.with_name(cache_path.name + ".tmp")
            temporary_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(cache_path)
        except OSError:
            # A cache write failure must not invalidate the live publisher response.
            pass
    return result


def dimension_extent(
    layer: dict[str, Any],
    dimension_name: str,
    *,
    require_even_spacing: bool = True,
) -> tuple[int, float, float, float]:
    """Return count, first coordinate, last coordinate and positive spacing."""
    try:
        dimension = layer["dimensions"][dimension_name]
        count = int(dimension["metadata"]["nValues"])
        extent = dimension["attributes"]["actual_range"].split(",")
        low, high = (float(value.strip()) for value in extent)
        spacing = 0.0
        evenly_spaced = dimension["metadata"].get("evenlySpaced", "true").casefold()
        if count > 1:
            spacing_text = dimension["metadata"]["averageSpacing"]
            spacing_match = re.match(
                r"\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)",
                spacing_text,
            )
            if spacing_match is None:
                raise ValueError("averageSpacing is not numeric")
            spacing = abs(float(spacing_match.group(1)))
    except (KeyError, TypeError, ValueError) as error:
        raise IntakeError(
            f"ERDDAP metadata for {dimension_name!r} lacks a usable range and spacing."
        ) from error
    if count < 1 or not math.isfinite(low) or not math.isfinite(high):
        raise IntakeError(f"ERDDAP returned invalid coordinate metadata for {dimension_name!r}.")
    if count > 1:
        if spacing <= 0 or high <= low:
            raise IntakeError(f"Only ascending {dimension_name!r} axes are supported.")
        if require_even_spacing and evenly_spaced != "true":
            raise IntakeError(
                f"Only evenly spaced {dimension_name!r} axes are supported."
            )
    return count, low, high, spacing


def validate_coordinate_bounds(
    layer: dict[str, Any], dimension_name: str, requested: tuple[float, float]
) -> dict[str, Any]:
    """Validate bounds against the publisher axis without assuming its direction."""
    lower, upper = requested
    if not math.isfinite(lower) or not math.isfinite(upper) or lower >= upper:
        raise IntakeError(f"{dimension_name} bounds must be finite and increasing.")
    count, axis_low, axis_high, spacing = dimension_extent(layer, dimension_name)
    if lower < axis_low or upper > axis_high:
        raise IntakeError(
            f"Requested {dimension_name} bounds {lower:g}..{upper:g} exceed the "
            f"publisher axis {axis_low:g}..{axis_high:g}."
        )
    if count == 1:
        if not lower <= axis_low <= upper:
            raise IntakeError(f"The requested bounds contain no {dimension_name} grid cells.")
    return {
        "requested_bounds": [lower, upper],
        "publisher_axis_bounds": [axis_low, axis_high],
        "publisher_axis_spacing": spacing,
        "publisher_axis_values": count,
    }


def time_coordinate_bounds(layer: dict[str, Any]) -> tuple[str, str]:
    """Return the full time-axis extent as ERDDAP-compatible UTC coordinates."""
    try:
        dimension = layer["dimensions"]["time"]
        units = dimension["attributes"]["units"]
        if units.casefold() != "seconds since 1970-01-01t00:00:00z":
            raise ValueError("unsupported time units")
        _, start, end, _ = dimension_extent(
            layer, "time", require_even_spacing=False
        )
        values = tuple(
            datetime.fromtimestamp(value, timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
            for value in (start, end)
        )
    except (KeyError, OSError, OverflowError, ValueError) as error:
        raise IntakeError(
            "This collector requires a time axis expressed as seconds since the Unix epoch."
        ) from error
    return values


def intersect_time_bounds(
    available: tuple[str, str], requested: tuple[str, str]
) -> tuple[str, str] | None:
    """Clip a requested UTC time range to the layer's advertised time axis."""
    try:
        available_start, available_end = (
            datetime.fromisoformat(value.replace("Z", "+00:00")) for value in available
        )
        requested_start, requested_end = (
            datetime.fromisoformat(value.replace("Z", "+00:00")) for value in requested
        )
    except ValueError as error:
        raise IntakeError("Time bounds must be ISO-8601 UTC timestamps.") from error
    if requested_start > requested_end:
        raise IntakeError("Requested time bounds must be increasing.")
    start = max(available_start, requested_start)
    end = min(available_end, requested_end)
    if start > end:
        return None
    return tuple(
        value.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        for value in (start, end)
    )


def build_query(
    layer: dict[str, Any],
    variable: str | Sequence[str],
    longitude: tuple[float, float],
    latitude: tuple[float, float],
    requested_time_bounds: tuple[str, str] | None = None,
) -> tuple[str, dict[str, Any]]:
    variables = [variable] if isinstance(variable, str) else list(variable)
    if not variables or len(variables) != len(set(variables)):
        raise IntakeError("Select one or more distinct data variables.")
    available = set(layer["variables"])
    for name in variables:
        if not SAFE_VARIABLE.fullmatch(name):
            raise IntakeError(
                "Variable names may contain only letters, digits and underscores."
            )
        if name not in available:
            raise IntakeError(f"Variable {name!r} is not in this layer.")

    dimension_sets = {layer["variables"][name] for name in variables}
    if len(dimension_sets) != 1:
        raise IntakeError(
            "ERDDAP only allows variables with identical dimensions in one request; "
            "this dataset's data variables do not share one dimension set."
        )
    dimensions = next(iter(dimension_sets))
    if not {"latitude", "longitude"}.issubset(dimensions):
        raise IntakeError(
            "This collector requires gridded variables with latitude and longitude axes."
        )
    if any(name not in layer["dimensions"] for name in dimensions):
        raise IntakeError("ERDDAP metadata is missing an axis required by the variables.")

    coordinate_constraints: dict[str, dict[str, Any]] = {}
    for dimension_name, requested in (
        ("latitude", latitude),
        ("longitude", longitude),
    ):
        coordinate_constraints[dimension_name] = validate_coordinate_bounds(
            layer, dimension_name, requested
        )

    time_bounds = None
    if "time" in dimensions:
        available_time_bounds = time_coordinate_bounds(layer)
        time_bounds = intersect_time_bounds(
            available_time_bounds,
            requested_time_bounds or available_time_bounds,
        )
        if time_bounds is None:
            raise IntakeError("The requested time range does not overlap this layer.")

    ranges = []
    for dimension_name in dimensions:
        if dimension_name == "time":
            start, stop = time_bounds
            ranges.append(f"[({start}):1:({stop})]")
        elif dimension_name in coordinate_constraints:
            lower, upper = coordinate_constraints[dimension_name]["requested_bounds"]
            ranges.append(f"[({lower:.15g}):1:({upper:.15g})]")
        else:
            # Retain every value on additional axes such as depth or altitude.
            ranges.append("[]")
    query = ",".join(name + "".join(ranges) for name in variables)
    url = f"{ERDDAP_ROOT}/griddap/{layer['dataset_id']}.nc?{quote(query, safe='[]():,')}"
    detail = {
        "variable": variables[0] if len(variables) == 1 else None,
        "variables": variables,
        "variable_dimensions": list(dimensions),
        "requested_longitude_bounds_degrees_east": list(longitude),
        "requested_latitude_bounds_degrees_north": list(latitude),
        "coordinate_constraints": coordinate_constraints,
        "requested_time_bounds_utc": (
            list(requested_time_bounds) if requested_time_bounds else None
        ),
        "available_time_bounds_utc": (
            list(available_time_bounds) if "time" in dimensions else None
        ),
        "selected_time_bounds_utc": list(time_bounds) if time_bounds else None,
    }
    return url, detail


def _extent_intersects(
    row: dict[str, str], minimum_name: str, maximum_name: str, bounds: tuple[float, float]
) -> bool:
    """Use catalogue extents to skip only layers clearly outside the requested area."""
    try:
        minimum = float(row[minimum_name])
        maximum = float(row[maximum_name])
    except (KeyError, TypeError, ValueError):
        return True
    return maximum >= bounds[0] and minimum <= bounds[1]


def _catalog_grid_candidates(
    rows: list[dict[str, str]],
    longitude: tuple[float, float],
    latitude: tuple[float, float],
) -> tuple[list[dict[str, str]], int, list[dict[str, str]]]:
    candidates = []
    skipped = 0
    other_release_layers = []
    for row in rows:
        if row.get("dataStructure", "").casefold() != "grid":
            continue
        if row.get("accessible", "").casefold() not in {
            "true",
            "yes",
            "1",
            "public",
        }:
            continue
        if not row.get("griddap") or not row.get("datasetID"):
            continue
        if not SAFE_ID.fullmatch(row["datasetID"]):
            raise IntakeError("ERDDAP catalogue returned an unsafe dataset ID.")
        intersects = _extent_intersects(
            row, "minLongitude", "maxLongitude", longitude
        ) and _extent_intersects(row, "minLatitude", "maxLatitude", latitude)
        if not intersects:
            skipped += 1
            continue

        dataset_id = row["datasetID"].casefold()
        v3_temporal_id = re.search(
            r"_(?:baseline_2000_2018|baseline_2000_2019|baseline_2000_2020|ssp(?:119|126|245|370|460|585)_2020_2100)_",
            dataset_id,
        )
        if not v3_temporal_id and dataset_id != "terrain_characteristics":
            other_release_layers.append(
                {
                    "dataset_id": row["datasetID"],
                    "title": row.get("title", ""),
                }
            )
            continue
        candidates.append(row)
    return candidates, skipped, other_release_layers


def scenario_label(dataset_id: str, title: str, *, is_static: bool) -> str:
    text = f"{dataset_id} {title}".casefold().replace("_", "-")
    for code, label in (
        ("ssp119", "SSP1-1.9"),
        ("ssp126", "SSP1-2.6"),
        ("ssp245", "SSP2-4.5"),
        ("ssp370", "SSP3-7.0"),
        ("ssp460", "SSP4-6.0"),
        ("ssp585", "SSP5-8.5"),
    ):
        if code in text.replace("-", "") or label.casefold() in text:
            return label
    if "baseline" in text or "present" in text:
        return "present-day baseline"
    return "static" if is_static else "unclassified time-varying layer"


def build_catalog_plan() -> dict[str, Any]:
    """Inspect matching Bio-ORACLE v3 grids for the fixed collection area."""
    longitude = LONGITUDE_BOUNDS_DEGREES_EAST
    latitude = LATITUDE_BOUNDS_DEGREES_NORTH
    time_bounds = COLLECTION_TIME_BOUNDS_UTC
    print("[1/3] Reading the Bio-ORACLE catalogue...")
    catalog_rows, catalog_response = dataset_catalog()
    candidates, outside_region_count, other_release_layers = _catalog_grid_candidates(
        catalog_rows, longitude, latitude
    )
    print(
        f"[2/3] Inspecting metadata for {len(candidates)} regional v3 layer(s)...",
        flush=True,
    )
    selected: list[dict[str, Any]] = []
    outside_period: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []

    def inspect_candidate(
        row: dict[str, str],
    ) -> tuple[str, dict[str, Any]]:
        dataset_id = row["datasetID"]
        try:
            layer = layer_metadata(dataset_id, use_cache=True)
            variables = sorted(
                name
                for name in layer["variables"]
                if name not in layer["dimensions"]
            )
            if not variables:
                raise IntakeError("No gridded data variables were listed in metadata.")

            has_time_axis = any(
                "time" in layer["variables"][name] for name in variables
            )
            has_time = False
            available_time_bounds = None
            if has_time_axis:
                try:
                    has_time = int(layer["dimensions"]["time"]["metadata"]["nValues"]) > 1
                except (KeyError, TypeError, ValueError) as error:
                    raise IntakeError(
                        "ERDDAP metadata did not provide a valid time-axis value count."
                    ) from error
                if has_time:
                    available_time_bounds = time_coordinate_bounds(layer)
            if available_time_bounds and intersect_time_bounds(
                available_time_bounds, time_bounds
            ) is None:
                return "outside_period", {
                    "dataset_id": dataset_id,
                    "available_time_bounds_utc": ", ".join(available_time_bounds),
                }

            query_url, query = build_query(
                layer,
                variables,
                longitude,
                latitude,
                requested_time_bounds=time_bounds if has_time else None,
            )
        except IntakeError as error:
            return "unresolved", {"dataset_id": dataset_id, "reason": str(error)}

        title = layer["global_attributes"].get("title") or row.get("title", "")
        return "selected", {
            "dataset_id": dataset_id,
            "title": title,
            "scenario": scenario_label(dataset_id, title, is_static=not has_time),
            "variables": variables,
            "dimensions": list(query["variable_dimensions"]),
            "available_time_bounds_utc": available_time_bounds,
            "selected_time_bounds_utc": query["selected_time_bounds_utc"],
            "query_url": query_url,
            "query": query,
            "layer": layer,
        }

    if candidates:
        with ThreadPoolExecutor(max_workers=min(12, len(candidates))) as executor:
            for index, (result_type, result) in enumerate(
                executor.map(inspect_candidate, candidates), start=1
            ):
                if result_type == "selected":
                    selected.append(result)
                elif result_type == "outside_period":
                    outside_period.append(result)
                else:
                    unresolved.append(result)
                if index % 25 == 0 or index == len(candidates):
                    print(
                        f"[INFO] Inspected layer metadata {index}/{len(candidates)}.",
                        file=sys.stderr,
                        flush=True,
                    )

    return {
        "publisher": "Bio-ORACLE ERDDAP",
        "catalog_url": catalog_response["url"],
        "catalog_response": catalog_response,
        "requested_longitude_bounds_degrees_east": list(longitude),
        "requested_latitude_bounds_degrees_north": list(latitude),
        "region": REGION,
        "requested_time_bounds_utc": list(time_bounds),
        "catalog_dataset_row_count": len(catalog_rows),
        "catalog_grid_candidates_intersecting_region": len(candidates),
        "catalog_grids_skipped_outside_region": outside_region_count,
        "catalog_grids_outside_bio_oracle_v3_scope": other_release_layers,
        "layers_skipped_outside_time_range": outside_period,
        "unresolved_layers": unresolved,
        "selected_layer_count": len(selected),
        "selected_variable_count": sum(len(item["variables"]) for item in selected),
        "layers": selected,
    }


def print_catalog_plan(plan: dict[str, Any]) -> None:
    """Print a concise, machine-readable catalogue plan without payload data."""
    summary = {
        key: value
        for key, value in plan.items()
        if key not in {"catalog_response", "layers"}
    }
    summary["catalog_response"] = {
        key: value
        for key, value in plan["catalog_response"].items()
        if key != "url"
    }
    summary["layers"] = [
        {key: value for key, value in layer.items() if key not in {"layer", "query"}}
        for layer in plan["layers"]
    ]
    summary["catalog_url"] = plan["catalog_url"]
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def local_download_paths(dataset_id: str, variable: str) -> tuple[Path, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = RAW_ROOT / dataset_id
    directory.mkdir(parents=True, exist_ok=True)
    suffix = 1
    while True:
        extra = "" if suffix == 1 else f"-{suffix:02d}"
        stem = f"{timestamp}_{variable}{extra}"
        data_path = directory / f"{stem}.nc"
        manifest_path = directory / f"{stem}.manifest.json"
        temporary_path = data_path.with_name(data_path.name + ".part")
        temporary_manifest_path = manifest_path.with_name(manifest_path.name + ".tmp")
        if (
            not data_path.exists()
            and not manifest_path.exists()
            and not temporary_path.exists()
            and not temporary_manifest_path.exists()
        ):
            return data_path, manifest_path
        suffix += 1


def download_netcdf(
    url: str,
    destination: Path,
    *,
    progress_callback: Callable[[int, int | None], None] | None = None,
) -> dict[str, Any]:
    """Stream one NetCDF response to disk, reporting bytes and fingerprinting it."""
    temporary = destination.with_name(destination.name + ".part")
    digest = hashlib.sha256()
    received = 0
    expected_bytes: int | None = None
    temporary_created = False
    try:
        request = Request(
            url,
            headers={
                "Accept": "application/x-netcdf, application/octet-stream",
                "User-Agent": "OCEAVERA Bio-ORACLE data intake",
            },
        )
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                try:
                    expected_bytes = int(content_length)
                except ValueError as error:
                    raise IntakeError(
                        "Bio-ORACLE returned an invalid Content-Length header."
                    ) from error
                if expected_bytes < 0:
                    raise IntakeError("Bio-ORACLE returned a negative Content-Length.")
            prefix = response.read(8)
            if not prefix.startswith(NETCDF_SIGNATURES):
                raise IntakeError(
                    "Bio-ORACLE ERDDAP did not return a recognised NetCDF response. "
                    f"Content-Type was {content_type or 'not provided'}."
                )
            with temporary.open("xb") as output:
                temporary_created = True
                output.write(prefix)
                digest.update(prefix)
                received = len(prefix)
                if progress_callback is not None:
                    progress_callback(received, expected_bytes)
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    received += len(chunk)
                    if received > MAX_DATA_BYTES:
                        raise IntakeError(
                            f"NetCDF response exceeded the {MAX_DATA_BYTES:,}-byte limit. "
                            "Narrow the bounds before downloading."
                        )
                    output.write(chunk)
                    digest.update(chunk)
                    if progress_callback is not None:
                        progress_callback(received, expected_bytes)
                output.flush()
        if expected_bytes is not None:
            if expected_bytes != received:
                raise IntakeError(
                    "Bio-ORACLE response length does not match Content-Length "
                    f"({received:,} received, {expected_bytes:,} advertised)."
                )
        temporary.replace(destination)
    except IncompleteRead as error:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        received_in_response = received + len(error.partial)
        transfer_detail = f"{received_in_response:,} bytes received"
        if expected_bytes is not None:
            transfer_detail = (
                f"{received_in_response:,} of {expected_bytes:,} advertised bytes received"
            )
        raise RetryableDownloadError(
            "The publisher closed the response early "
            f"({transfer_detail})."
        ) from error
    except HTTPError as error:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        if error.code == 429 or error.code >= 500:
            raise RetryableDownloadError(
                f"ERDDAP data request returned HTTP {error.code}."
            ) from error
        raise IntakeError(f"ERDDAP data request failed with HTTP {error.code}.") from error
    except URLError as error:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        raise RetryableDownloadError(
            f"Publisher data endpoint request failed: {error.reason}."
        ) from error
    except TimeoutError as error:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        raise RetryableDownloadError(
            f"Publisher data response timed out: {error}."
        ) from error
    except OSError as error:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        raise IntakeError(f"Could not save the NetCDF response: {error}") from error
    except IntakeError:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        raise

    return {
        "http_status": status,
        "content_type": content_type,
        "content_length_header": content_length,
        "response_bytes": received,
        "sha256": digest.hexdigest(),
    }


def human_bytes(value: int) -> str:
    """Format a byte count compactly for terminal progress and run summaries."""
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            return f"{amount:,.1f} {unit}" if unit != "B" else f"{value:,} B"
        amount /= 1024
    return f"{value:,} B"


def write_json_atomic(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary_created = False
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            temporary_created = True
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
        temporary.replace(path)
    except OSError:
        if temporary_created:
            temporary.unlink(missing_ok=True)
        raise


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _reusable_download(
    item: dict[str, Any], plan: dict[str, Any]
) -> dict[str, Any] | None:
    """Reuse only a prior payload whose manifest, query, size and hash still match."""
    dataset_id = item["dataset_id"]
    directory = RAW_ROOT / dataset_id
    if not directory.is_dir():
        return None
    for manifest_path in sorted(directory.glob("*.manifest.json"), reverse=True):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if (
                manifest.get("status") != "complete"
                or not isinstance(manifest.get("catalog_run_id"), str)
                or not manifest.get("catalog_run_id")
                or manifest.get("dataset_id") != dataset_id
                or manifest.get("query_url") != item["query_url"]
                or manifest.get("region") != plan.get("region")
                or manifest.get("requested_time_range_utc")
                != plan["requested_time_bounds_utc"]
            ):
                continue
            payload_location = Path(manifest["payload_location"])
            if payload_location.is_absolute():
                continue
            payload_path = (ROOT / payload_location).resolve()
            if not payload_path.is_relative_to(ROOT):
                continue
            download = manifest["download"]
            expected_hash = download["sha256"]
            expected_bytes = int(download["response_bytes"])
            if (
                not payload_path.is_file()
                or payload_path.stat().st_size != expected_bytes
                or _file_sha256(payload_path) != expected_hash
            ):
                continue
            return {
                "dataset_id": dataset_id,
                "status": "reused",
                "variables": item["variables"],
                "payload_location": payload_path.relative_to(ROOT).as_posix(),
                "response_bytes": expected_bytes,
                "sha256": expected_hash,
                "manifest_location": manifest_path.relative_to(ROOT).as_posix(),
            }
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return None


def download_catalog_plan(plan: dict[str, Any]) -> int:
    """Download every regional grid response in the fixed collection plan."""
    if plan["unresolved_layers"]:
        print_catalog_plan(plan)
        print(
            "[ERROR] The catalogue has unresolved regional grid layers; no data were "
            "downloaded. Resolve the listed metadata or dimension issue first.",
            file=sys.stderr,
        )
        return 2
    if not plan["layers"]:
        print("[ERROR] No Bio-ORACLE layers intersect the requested area and period.", file=sys.stderr)
        return 2

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_directory = RAW_ROOT / "_runs"
    run_manifest_path = run_directory / f"{run_id}_bio_oracle_catalog.json"
    run_directory.mkdir(parents=True, exist_ok=True)
    run_started = time.monotonic()
    results: dict[int, dict[str, Any]] = {
        index: {
            "dataset_id": item["dataset_id"],
            "status": "pending",
            "variables": item["variables"],
        }
        for index, item in enumerate(plan["layers"])
    }

    def build_run_manifest() -> dict[str, Any]:
        ordered_results = [results[index] for index in range(len(plan["layers"]))]
        completed_count = sum(
            item["status"] in {"complete", "reused"} for item in ordered_results
        )
        failed_count = sum(item["status"] == "failed" for item in ordered_results)
        finished = completed_count + failed_count == len(ordered_results)
        return {
            "schema_version": 1,
            "status": (
                "complete"
                if finished and failed_count == 0
                else "partial"
                if finished
                else "in_progress"
            ),
            "publisher": plan["publisher"],
            "catalog_run_id": run_id,
            "catalog_url": plan["catalog_url"],
            "catalog_response": plan["catalog_response"],
            "requested_longitude_bounds_degrees_east": plan[
                "requested_longitude_bounds_degrees_east"
            ],
            "requested_latitude_bounds_degrees_north": plan[
                "requested_latitude_bounds_degrees_north"
            ],
            "region": plan.get("region"),
            "requested_time_bounds_utc": plan["requested_time_bounds_utc"],
            "catalog_dataset_row_count": plan["catalog_dataset_row_count"],
            "catalog_grid_candidates_intersecting_region": plan[
                "catalog_grid_candidates_intersecting_region"
            ],
            "catalog_grids_skipped_outside_region": plan[
                "catalog_grids_skipped_outside_region"
            ],
            "catalog_grids_outside_bio_oracle_v3_scope": plan[
                "catalog_grids_outside_bio_oracle_v3_scope"
            ],
            "layers_skipped_outside_time_range": plan[
                "layers_skipped_outside_time_range"
            ],
            "planned_layer_count": len(plan["layers"]),
            "completed_layer_count": completed_count,
            "failed_layer_count": failed_count,
            "pending_layer_count": len(ordered_results) - completed_count - failed_count,
            "layers": ordered_results,
        }

    def persist_run_manifest() -> None:
        write_json_atomic(run_manifest_path, build_run_manifest())

    print("[3/3] Checking saved layers and preparing downloads...", flush=True)
    prior_partials = sorted(RAW_ROOT.rglob("*.part")) if RAW_ROOT.is_dir() else []
    if prior_partials:
        print(
            f"[NOTE] Found {len(prior_partials)} earlier partial response file(s). "
            "They will be kept and will not count as complete downloads.",
            flush=True,
        )
        print(f"       Example: {prior_partials[0].relative_to(ROOT).as_posix()}")

    pending: list[tuple[int, dict[str, Any]]] = []
    for index, item in enumerate(plan["layers"]):
        reused = _reusable_download(item, plan)
        if reused is None:
            pending.append((index, item))
        else:
            results[index] = reused
        checked = index + 1
        if checked % 25 == 0 or checked == len(plan["layers"]):
            verified_count = sum(
                result["status"] == "reused" for result in results.values()
            )
            print(
                f"[CHECK] Existing responses inspected: {checked}/{len(plan['layers'])}; "
                f"{verified_count} verified and reusable.",
                flush=True,
            )

    reused_count = sum(result["status"] == "reused" for result in results.values())
    print(
        f"[PLAN] {len(plan['layers'])} layer(s), "
        f"{sum(len(item['variables']) for item in plan['layers'])} variable(s); "
        f"{reused_count} verified and reusable, {len(pending)} to download.",
        flush=True,
    )
    try:
        persist_run_manifest()
    except OSError as error:
        print(f"[ERROR] Could not initialize catalogue run manifest: {error}", file=sys.stderr)
        return 1

    progress_lock = Lock()
    active_progress: dict[int, tuple[int, int | None]] = {}

    def update_progress(index: int, received: int, expected: int | None) -> None:
        with progress_lock:
            active_progress[index] = (received, expected)

    def download_item(
        index: int, item: dict[str, Any]
    ) -> tuple[int, dict[str, Any]]:
        dataset_id = item["dataset_id"]
        layer = item["layer"]
        try:
            data_path, manifest_path = local_download_paths(dataset_id, "all-variables")
            download: dict[str, Any] | None = None
            for attempt in range(1, MAX_ATTEMPTS + 1):
                update_progress(index, 0, None)
                try:
                    download = download_netcdf(
                        item["query_url"],
                        data_path,
                        progress_callback=lambda received, expected: update_progress(
                            index, received, expected
                        ),
                    )
                    download["attempts"] = attempt
                    break
                except RetryableDownloadError as error:
                    if attempt == MAX_ATTEMPTS:
                        raise IntakeError(
                            f"Transfer failed after {attempt} attempts: {error}"
                        ) from error
                    print(
                        f"[RETRY] {dataset_id}: {error} "
                        f"Trying again ({attempt + 1}/{MAX_ATTEMPTS})...",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(2 ** (attempt - 1))
            if download is None:
                raise IntakeError("No complete response was received.")
            manifest = {
                "schema_version": 1,
                "status": "complete",
                "publisher": "Bio-ORACLE consortium",
                "catalog_run_id": run_id,
                "dataset_id": dataset_id,
                "dataset_title": item["title"],
                "dataset_source": layer["global_attributes"].get("source"),
                "scenario": item["scenario"],
                "metadata_url": layer["metadata_url"],
                "metadata_response": layer["response"],
                "catalog_url": plan["catalog_url"],
                "catalog_response": plan["catalog_response"],
                "variables": {
                    name: {
                        "dimensions": list(layer["variables"][name]),
                        "attributes": layer["variable_attributes"].get(name, {}),
                    }
                    for name in item["variables"]
                },
                "query_url": item["query_url"],
                "query": item["query"],
                "region": plan.get("region"),
                "requested_time_range_utc": plan["requested_time_bounds_utc"],
                "retrieved_at_utc": now_utc(),
                "format": "NetCDF; all dataset data variables retained in one publisher response",
                "payload_location": data_path.relative_to(ROOT).as_posix(),
                "download": download,
                "license_metadata": layer["global_attributes"].get("license"),
            }
            write_json_atomic(manifest_path, manifest)
            result = {
                "dataset_id": dataset_id,
                "status": "complete",
                "variables": item["variables"],
                "payload_location": manifest["payload_location"],
                "response_bytes": download["response_bytes"],
                "sha256": download["sha256"],
                "manifest_location": manifest_path.relative_to(ROOT).as_posix(),
            }
        except (IntakeError, OSError) as error:
            result = {
                "dataset_id": dataset_id,
                "status": "failed",
                "variables": item["variables"],
                "reason": str(error),
            }
        return index, result

    def progress_message() -> str:
        complete_count = sum(
            result["status"] in {"complete", "reused"}
            for result in results.values()
        )
        with progress_lock:
            active = list(active_progress.values())
        received = sum(item[0] for item in active)
        known_sizes = [item[1] for item in active if item[1] is not None]
        if active and len(known_sizes) == len(active):
            expected = sum(known_sizes)
            transfer = (
                f"{human_bytes(received)} / {human_bytes(expected)} "
                f"received for active requests"
            )
            if expected:
                transfer += f" ({min(100, received / expected * 100):.0f}%)"
        elif active:
            transfer = f"{human_bytes(received)} received; some response sizes are unknown"
        else:
            transfer = "waiting for active requests"
        return (
            f"[PROGRESS] {complete_count}/{len(plan['layers'])} layers verified; "
            f"{len(active)} active request(s); {transfer}."
        )

    if pending:
        print(
            f"[DOWNLOAD] Starting {len(pending)} layer download(s), "
            f"with up to {DOWNLOAD_WORKERS} requests at once.",
            flush=True,
        )
        with progress_lock:
            active_progress.update({index: (0, None) for index, _ in pending})
        with ThreadPoolExecutor(
            max_workers=min(DOWNLOAD_WORKERS, len(pending))
        ) as executor:
            futures = {
                executor.submit(download_item, index, item): (index, item)
                for index, item in pending
            }
            last_progress_at = time.monotonic()
            while futures:
                done, _ = wait(
                    futures,
                    timeout=1.0,
                    return_when=FIRST_COMPLETED,
                )
                if not done:
                    now = time.monotonic()
                    if now - last_progress_at >= 10:
                        print(progress_message(), flush=True)
                        last_progress_at = now
                    continue

                for future in done:
                    index, item = futures.pop(future)
                    try:
                        result_index, result = future.result()
                    except Exception as error:
                        result_index = index
                        result = {
                            "dataset_id": item["dataset_id"],
                            "status": "failed",
                            "variables": item["variables"],
                            "reason": (
                                f"Unexpected download worker error: "
                                f"{type(error).__name__}: {error}"
                            ),
                        }
                    with progress_lock:
                        active_progress.pop(result_index, None)
                    results[result_index] = result
                    finished_count = sum(
                        value["status"] in {"complete", "reused", "failed"}
                        for value in results.values()
                    )
                    if result["status"] == "failed":
                        print(
                            f"[FAILED] {result['dataset_id']}: {result['reason']}",
                            file=sys.stderr,
                            flush=True,
                        )
                    else:
                        print(
                            f"[OK] {finished_count}/{len(plan['layers'])} "
                            f"{result['dataset_id']} — "
                            f"{human_bytes(result['response_bytes'])}, "
                            f"{len(result['variables'])} variable(s).",
                            flush=True,
                        )
                    try:
                        persist_run_manifest()
                    except OSError as error:
                        print(
                            f"[ERROR] Could not update catalogue run manifest: {error}",
                            file=sys.stderr,
                        )
                last_progress_at = time.monotonic()

    run_manifest = build_run_manifest()
    try:
        persist_run_manifest()
    except OSError as error:
        print(f"[ERROR] Could not write the catalogue run manifest: {error}", file=sys.stderr)
        return 1
    completed_results = [
        result
        for result in results.values()
        if result["status"] in {"complete", "reused"}
    ]
    failed_results = [
        result for result in results.values() if result["status"] == "failed"
    ]
    downloaded_count = sum(result["status"] == "complete" for result in results.values())
    reused_count = sum(result["status"] == "reused" for result in results.values())
    available_variable_count = sum(len(result["variables"]) for result in completed_results)
    requested_variable_count = sum(len(item["variables"]) for item in plan["layers"])
    verified_payload_bytes = sum(
        int(result.get("response_bytes", 0)) for result in completed_results
    )
    downloaded_payload_bytes = sum(
        int(result.get("response_bytes", 0))
        for result in results.values()
        if result["status"] == "complete"
    )
    elapsed_seconds = time.monotonic() - run_started

    if run_manifest["status"] == "complete":
        print("\n[COMPLETE] Every planned layer is downloaded and verified.", flush=True)
    else:
        print("\n[INCOMPLETE] Some planned layers still need a successful download.", flush=True)
    print(
        f"  Layers: {run_manifest['completed_layer_count']}/"
        f"{run_manifest['planned_layer_count']} complete; "
        f"{run_manifest['failed_layer_count']} failed; "
        f"{run_manifest['pending_layer_count']} pending."
    )
    print(
        f"  Variables in complete layers: "
        f"{available_variable_count:,}/{requested_variable_count:,}."
    )
    print(
        f"  Verified payloads: {human_bytes(verified_payload_bytes)}; "
        f"downloaded this run: {human_bytes(downloaded_payload_bytes)}."
    )
    print(f"  Reused existing layers: {reused_count}; downloaded this run: {downloaded_count}.")
    print(f"  Elapsed time: {elapsed_seconds / 60:.1f} minutes.")
    if failed_results:
        print("  Layers to retry:")
        for result in failed_results:
            print(
                f"    - {result['dataset_id']} "
                f"({len(result['variables'])} variable(s)): {result['reason']}"
            )
        print(
            "  Retry by running `python src/data_collection/bio_oracle_layers.py` "
            "again; complete files are checksum-verified and reused."
        )
    if prior_partials:
        print(
            f"  Earlier partial files kept unchanged: {len(prior_partials)} "
            f"(they do not count as complete layers)."
        )
    print(f"  Data folder: {RAW_ROOT.relative_to(ROOT).as_posix()}/")
    print(f"  Run report: {run_manifest_path.relative_to(ROOT).as_posix()}")
    return 0 if run_manifest["status"] == "complete" else 1


def main() -> int:
    """Run the fixed Sri Lankan Bio-ORACLE collection without options."""
    if len(sys.argv) > 1:
        print(
            "This collector has fixed Sri Lankan bounds and a fixed 2000–2100 "
            "window. Run it without command-line options to collect those data.",
            file=sys.stderr,
        )
        return 2

    print("=" * 72)
    print("BIO-ORACLE v3 | SRI LANKA ENVIRONMENTAL DATA COLLECTION")
    print("=" * 72)
    print(f"Region: {REGION['name']}")
    print(
        "Longitude bounds: "
        f"{LONGITUDE_BOUNDS_DEGREES_EAST[0]}–{LONGITUDE_BOUNDS_DEGREES_EAST[1]}° E"
    )
    print(
        "Latitude bounds: "
        f"{LATITUDE_BOUNDS_DEGREES_NORTH[0]}–{LATITUDE_BOUNDS_DEGREES_NORTH[1]}° N"
    )
    print(
        "Requested time range: "
        f"{COLLECTION_TIME_BOUNDS_UTC[0][:10]} to "
        f"{COLLECTION_TIME_BOUNDS_UTC[1][:10]} UTC"
    )
    print(
        "The collector will download every matching Bio-ORACLE v3 grid and all "
        "data variables, using only time coordinates supplied by the publisher."
    )
    print(
        "Bio-ORACLE provides decade-level values; this request does not create "
        "annual data or a separate 2100 snapshot."
    )
    print(f"Output folder: {RAW_ROOT.relative_to(ROOT).as_posix()}/")
    print(
        "Existing complete files will be checksum-verified and reused. "
        "Transient response interruptions are retried automatically."
    )

    try:
        plan = build_catalog_plan()
        print(
            f"[PLAN] Catalogue: {plan['catalog_dataset_row_count']} entries; "
            f"{plan['selected_layer_count']} regional grids; "
            f"{plan['selected_variable_count']} variables."
        )
        return download_catalog_plan(plan)
    except IntakeError as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"[ERROR] File operation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
