"""Integrate cleaned OBIS rows with compatible Bio-ORACLE source slices.

The NetCDF variables are read with netCDF4's automatic masking and scale/offset
handling enabled. Values are never scaled a second time in this module.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as parquet
from netCDF4 import Dataset, num2date
from shapely.geometry import Point


ROOT = Path(__file__).resolve().parents[2]
OBIS_PATH = ROOT / "data/interim/obis/cleaning/occurrences_cleaned.csv"
BIO_MANIFEST_PATH = ROOT / "data/interim/bio_oracle/cleaning/manifest.json"
OUTPUT_PATH = ROOT / "data/interim/integrated/full/integrated_observations.parquet"
CATALOG_JSON_PATH = ROOT / "docs/records/2026-10-16-integration-variable-catalog.json"
CATALOG_MD_PATH = ROOT / "docs/records/2026-10-16-integration-variable-catalog.md"
REPORT_JSON_PATH = ROOT / "docs/records/2026-10-16-integration-manifest.json"
REPORT_MD_PATH = ROOT / "docs/records/2026-10-16-integration-summary.md"

PERIOD_BY_YEAR = {
    **{year: "baseline_2000" for year in range(2000, 2010)},
    **{year: "baseline_2010" for year in range(2010, 2020)},
    **{year: "ssp245_2020" for year in range(2020, 2027)},
}
PERIOD_LABELS = {
    "baseline_2000": "2000–2009 (Bio-ORACLE coordinate 2000)",
    "baseline_2010": "2010–2019 (Bio-ORACLE coordinate 2010)",
    "ssp245_2020": "2020–2026 (SSP245 coordinate 2020)",
}
EARTH_RADIUS_KM = 6371.0088


class IntegrationError(RuntimeError):
    """Raised when source metadata or output validation is inconsistent."""


class IntegrationHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Keep repository-relative default paths together in CLI help output."""

    def __init__(self, prog: str) -> None:
        super().__init__(prog, width=100)


def progress(message: str) -> None:
    """Show run progress without mixing it into the final console summary."""
    print(f"[Script 8] {message}", file=sys.stderr, flush=True)


def print_dry_run_summary(
    rows: int,
    original_fields: int,
    source_products: int,
    features: int,
    output_path: Path,
    root: Path = ROOT,
) -> None:
    """Show the planned integration in a concise, readable form."""
    print("\nIntegration preflight complete — no files were written.")
    print(f"  OBIS observations: {rows:,}")
    print(f"  Original OBIS fields: {original_fields:,}")
    print(f"  Bio-ORACLE products checked: {source_products:,}")
    print(f"  Environmental features planned: {features:,}")
    print(f"  Planned GeoParquet output: {display_path(output_path, root)}")


def print_integration_summary(
    rows: int,
    original_fields: int,
    features: int,
    output_path: Path,
    geoparquet: dict[str, Any],
    raster_matches: dict[str, int],
    coverage: dict[str, int],
    root: Path = ROOT,
) -> None:
    """Show integration results while keeping detailed reports in their files."""
    compression = ", ".join(geoparquet.get("compression", [])) or "not reported"
    print("\nIntegration complete — output checks passed.")
    print(f"  OBIS observations preserved: {rows:,}")
    print(f"  Original OBIS fields preserved: {original_fields:,}")
    print(f"  Environmental feature columns: {features:,}")
    print(f"  Output: {display_path(output_path, root)}")
    print(
        f"  Format: GeoParquet {geoparquet.get('geoparquet_version', 'unknown')} "
        f"with {compression} compression"
    )
    if raster_matches:
        print("  Raster location matches:")
        for status, count in raster_matches.items():
            print(f"    {status.replace('_', ' ').capitalize()}: {count:,}")
    if coverage:
        print("  Environmental coverage:")
        for status, count in coverage.items():
            print(f"    {status.replace('_', ' ').capitalize()}: {count:,}")
    print("  Detailed reports:")
    print(f"    Variable catalog: {display_path(CATALOG_MD_PATH, root)}")
    print(f"    Integration manifest: {display_path(REPORT_JSON_PATH, root)}")
    print(f"    Run summary: {display_path(REPORT_MD_PATH, root)}")


def display_path(path: Path, root: Path = ROOT) -> str:
    """Prefer repository-relative paths in terminal messages and reports."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(resolved)


DATE_EPOCH_FIELDS = {"date_start", "date_mid", "date_end"}
SINGLE_DATE_FIELDS = ("year", "date_mid", "date_year", "eventDate")
TEMPERATURE_ABSOLUTE_VARIABLES = {"tas_ltmax", "tas_ltmin", "tas_max", "tas_mean", "tas_min"}
CLOUD_FRACTION_VARIABLES = {"clt_ltmax", "clt_ltmin", "clt_max", "clt_mean", "clt_min", "clt_range"}


def parse_year(value: Any, field: str | None = None) -> int | None:
    """Read one year/date, including OBIS date-field epoch milliseconds.

    Slash-separated date intervals deliberately return no single year. Call
    ``parse_year_interval`` when interval bounds are needed.
    """
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if "/" in text:
        return None
    # The OBIS API date_* fields are milliseconds, even near the Unix epoch.
    # Handle them before four-digit year recognition (e.g. date_mid=2000).
    if field in DATE_EPOCH_FIELDS and re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        try:
            return datetime.fromtimestamp(float(text) / 1000, tz=timezone.utc).year
        except (OverflowError, OSError, ValueError):
            return None
    if re.fullmatch(r"\d{4}", text):
        year = int(text)
        return year if 1500 <= year <= 2100 else None
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        number = float(text)
        if 1500 <= number <= 2100 and number.is_integer():
            return int(number)
        try:
            if field in {"year", "date_year"}:
                return None
            # Generic numeric dates use milliseconds; never infer seconds by size.
            return datetime.fromtimestamp(number / 1000, tz=timezone.utc).year
        except (OverflowError, OSError, ValueError):
            return None
    try:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        return datetime.fromisoformat(normalized).year
    except ValueError:
        match = re.match(r"^(\d{4})[-/]\d{1,2}(?:[-/]\d{1,2})?", text)
        if match:
            year = int(match.group(1))
            return year if 1500 <= year <= 2100 else None
        return None


def parse_year_interval(value: Any, field: str | None = None) -> tuple[int, int] | None:
    """Return the year bounds represented by one date or slash interval."""
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if "/" not in text:
        year = parse_year(text, field)
        return (year, year) if year is not None else None
    start_text, end_text = (part.strip() for part in text.split("/", 1))
    start = parse_year(start_text, field)
    if start is None:
        return None
    # OBIS sometimes abbreviates an interval end to a day, e.g. 1983-01-27/28.
    if re.fullmatch(r"\d{1,2}", end_text) and re.match(r"^\d{4}-", start_text):
        end = start
    else:
        end = parse_year(end_text, field)
    if end is None:
        return None
    return min(start, end), max(start, end)


def resolve_observation_date(row: dict[str, str | None]) -> dict[str, Any]:
    """Resolve a defensible year and environmental period without truncating intervals.

    A supported single-year field can resolve a multi-year interval only when
    it falls inside the interval. Conflicting single-year periods are marked
    ambiguous. An interval without a single-year field is eligible only when
    its entire span fits one supported environmental period.
    """
    candidates: list[tuple[str, int]] = []
    for field in SINGLE_DATE_FIELDS:
        year = parse_year(row.get(field), field)
        if year is not None:
            candidates.append((field, year))

    interval_bounds: list[tuple[int, int, str]] = []
    event_interval = parse_year_interval(row.get("eventDate"), "eventDate")
    if event_interval is not None and event_interval[0] != event_interval[1]:
        interval_bounds.append((*event_interval, "eventDate"))
    start = parse_year(row.get("date_start"), "date_start")
    end = parse_year(row.get("date_end"), "date_end")
    if start is not None or end is not None:
        interval_bounds.append((start if start is not None else end, end if end is not None else start, "date_start/date_end"))

    if interval_bounds:
        interval_start = min(bounds[0] for bounds in interval_bounds)
        interval_end = max(bounds[1] for bounds in interval_bounds)
    else:
        interval_start = interval_end = None

    if candidates:
        candidate_periods = {temporal_period(year) for _, year in candidates}
        candidates_fit_interval = (
            interval_start is None
            or all(interval_start <= year <= interval_end for _, year in candidates)
        )
        if len(candidate_periods) > 1 or not candidates_fit_interval:
            return {
                "year": None, "source": None, "period": None,
                "status": "ambiguous_conflicting_date_evidence",
                "eligibility": "ambiguous", "interval_start_year": interval_start,
                "interval_end_year": interval_end,
            }
        source, year = candidates[0]
        period = temporal_period(year)
        return {
            "year": year, "source": source, "period": period,
            "status": "resolved_single_year_with_interval" if interval_bounds else "resolved_single_year",
            "eligibility": "eligible" if period is not None else "ineligible",
            "interval_start_year": interval_start, "interval_end_year": interval_end,
        }

    if interval_start is not None:
        start_period = temporal_period(interval_start)
        end_period = temporal_period(interval_end)
        if start_period is not None and start_period == end_period:
            return {
                "year": None, "source": None, "period": start_period,
                "status": "resolved_period_from_bounded_interval",
                "eligibility": "eligible", "interval_start_year": interval_start,
                "interval_end_year": interval_end,
            }
        status = "ambiguous_interval_crosses_supported_period" if (
            start_period != end_period or (interval_start <= 2026 and interval_end >= 2000)
        ) else "interval_outside_supported_periods"
        eligibility = "ambiguous" if status.startswith("ambiguous") else "ineligible"
        return {
            "year": None, "source": None, "period": None, "status": status,
            "eligibility": eligibility, "interval_start_year": interval_start,
            "interval_end_year": interval_end,
        }

    return {
        "year": None, "source": None, "period": None,
        "status": "missing_or_invalid_date", "eligibility": "unknown",
        "interval_start_year": None, "interval_end_year": None,
    }


def resolve_observation_year(row: dict[str, str | None]) -> tuple[int | None, str | None]:
    """Backward-compatible pair for callers that only need the chosen point year."""
    result = resolve_observation_date(row)
    return result["year"], result["source"]


def legacy_parse_year_for_comparison(value: Any) -> int | None:
    """Recreate the former first-year parsing rule for a change-count report only."""
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}", text):
        year = int(text)
        return year if 1500 <= year <= 2100 else None
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        number = float(text)
        if 1500 <= number <= 2100 and number.is_integer():
            return int(number)
        try:
            seconds = number / 1000 if abs(number) >= 100_000_000_000 else number
            return datetime.fromtimestamp(seconds, tz=timezone.utc).year
        except (OverflowError, OSError, ValueError):
            return None
    try:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        return datetime.fromisoformat(normalized).year
    except ValueError:
        match = re.match(r"^(\d{4})[-/]\d{1,2}(?:[-/]\d{1,2})?", text)
        return int(match.group(1)) if match else None


def legacy_resolve_year_for_comparison(row: dict[str, str | None]) -> int | None:
    for field in ("year", "eventDate", "date_start", "date_mid", "date_end", "date_year"):
        year = legacy_parse_year_for_comparison(row.get(field))
        if year is not None:
            return year
    return None


def temporal_period(year: int | None) -> str | None:
    """Map a resolved observation year to the nearest supported source slice."""
    return PERIOD_BY_YEAR.get(year) if year is not None else None


def cell_edges(axis: np.ndarray) -> np.ndarray:
    """Return raster-cell edges from a monotonic one-dimensional centre axis."""
    values = np.asarray(axis, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise IntegrationError("Raster axes must contain at least two finite centres.")
    differences = np.diff(values)
    if not (np.all(differences > 0) or np.all(differences < 0)):
        raise IntegrationError("Raster coordinate axes must be strictly monotonic.")
    edges = np.empty(len(values) + 1, dtype=float)
    edges[1:-1] = (values[:-1] + values[1:]) / 2
    edges[0] = values[0] - differences[0] / 2
    edges[-1] = values[-1] + differences[-1] / 2
    return edges


def nearest_cell(
    longitude: float,
    latitude: float,
    longitude_axis: np.ndarray,
    latitude_axis: np.ndarray,
) -> tuple[int | None, int | None, str]:
    """Find the closest in-extent cell; ties choose the lower array index."""
    if not math.isfinite(longitude) or not math.isfinite(latitude):
        return None, None, "invalid_observation_coordinate"
    if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
        return None, None, "invalid_observation_coordinate"
    longitude_edges = cell_edges(longitude_axis)
    latitude_edges = cell_edges(latitude_axis)
    if not (
        min(longitude_edges) <= longitude <= max(longitude_edges)
        and min(latitude_edges) <= latitude <= max(latitude_edges)
    ):
        return None, None, "outside_raster_extent"
    column = int(np.argmin(np.abs(longitude_axis - longitude)))
    row = int(np.argmin(np.abs(latitude_axis - latitude)))
    return row, column, "matched"


def great_circle_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Approximate source-point to cell-centre distance with the haversine formula."""
    lon1, lat1, lon2, lat2 = map(math.radians, (lon1, lat1, lon2, lat2))
    dlon, dlat = lon2 - lon1, lat2 - lat1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(value)))


def feature_column(variable_name: str, depth_key: str) -> str:
    return f"bio_oracle__{variable_name}__{depth_key}"


def unit_key(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).casefold()


def unit_policy(variable_name: str, source_units: str, standard_name: str) -> dict[str, str]:
    """Describe one source-to-output unit mapping from declared NetCDF metadata."""
    source_key = unit_key(source_units)
    reason = ""
    if variable_name in TEMPERATURE_ABSOLUTE_VARIABLES and source_key in {"k", "kelvin"}:
        reason = "Original baseline tas payload is Celsius-like but declares Kelvin; publisher interpretation unresolved."
    elif variable_name == "tas_range":
        reason = "Original tas_range equals max-minus-min minus 273.15; range offset is scientifically unresolved."
    elif variable_name == "clt_sd":
        reason = "Original clt_sd exceeds one despite dimensionless cloud-fraction metadata; scale/statistic unresolved."
    if reason:
        return {
            "standardized_units": "degree_C" if variable_name.startswith("tas_") else "1",
            "conversion": "quarantine as null; original numerical values and metadata preserved unchanged",
            "scientific_status": "quarantined_unresolved_source_semantics",
            "quarantine_reason": reason,
        }
    if variable_name in TEMPERATURE_ABSOLUTE_VARIABLES | {"tas_range"}:
        if source_key in {"degree_c", "degrees_c", "degree_celsius", "degrees_celsius", "degc", "°c"}:
            return {"standardized_units": "degree_C", "conversion": "identity; source is already Celsius"}
        raise IntegrationError(f"Unsupported AirTemperature unit {source_units!r} for {variable_name}.")
    if variable_name in CLOUD_FRACTION_VARIABLES:
        if standard_name.strip().casefold() != "cloud_area_fraction":
            raise IntegrationError(f"Cloud fraction variable {variable_name} has unexpected standard_name {standard_name!r}.")
        if source_key in {"1", "(0 - 1)", "0 - 1", "dimensionless"}:
            return {"standardized_units": "1", "conversion": "identity; dimensionless fraction"}
        raise IntegrationError(f"Unsupported TotalCloudFraction unit {source_units!r} for {variable_name}.")
    return {"standardized_units": str(source_units).strip(), "conversion": "identity"}


def harmonize_source_values(values: np.ma.MaskedArray, variable_name: str, source_units: str) -> np.ma.MaskedArray:
    """Convert already-decoded NetCDF values without applying scale/offset twice."""
    result = np.ma.asarray(values, dtype=float)
    policy = unit_policy(variable_name, source_units, "cloud_area_fraction" if variable_name in CLOUD_FRACTION_VARIABLES else "")
    if policy.get("quarantine_reason"):
        return np.ma.masked_all(result.shape, dtype=float)
    if variable_name in CLOUD_FRACTION_VARIABLES:
        valid = np.asarray(np.ma.compressed(result), dtype=float)
        if valid.size and (valid.min() < -1e-6 or valid.max() > 1 + 1e-6):
            raise IntegrationError(
                f"Decoded cloud fraction {variable_name} falls outside [0, 1]: "
                f"minimum={valid.min()}, maximum={valid.max()}."
            )
    return np.ma.asarray(result)


def depth_from_title(title: str) -> str:
    """Read the declared depth stratum from the NetCDF title metadata."""
    match = re.search(r"\[(depth(?:surf|min|mean|max)|benthic)\]", title, flags=re.IGNORECASE)
    if not match:
        raise IntegrationError(f"No recognised depth stratum in NetCDF title: {title}")
    value = match.group(1).lower()
    return "benthic" if value == "benthic" else f"depth{value[5:]}"


def scenario_from_metadata(title: str, dataset_id: str, time_years: list[int]) -> str:
    """Classify a product from its NetCDF title and cross-check its manifest ID."""
    title_lower, id_lower = title.lower(), dataset_id.lower()
    if "terrain characteristics" in title_lower:
        if dataset_id != "terrain_characteristics":
            raise IntegrationError(f"Terrain title does not match manifest product {dataset_id}.")
        return "terrain"
    baseline_title = "baseline" in title_lower or ("2000" in title_lower and "2020" in title_lower)
    if baseline_title and "_baseline_" in id_lower and {2000, 2010}.issubset(set(time_years)):
        return "baseline"
    if "ssp245" in title_lower and "_ssp245_" in id_lower and 2020 in time_years:
        return "ssp245"
    raise IntegrationError(f"NetCDF title and product ID disagree for {dataset_id}: {title}")


def axis_variable(dataset: Dataset, standard_name: str, axis_letter: str) -> tuple[str, np.ndarray]:
    for name, variable in dataset.variables.items():
        if getattr(variable, "standard_name", "").lower() == standard_name or getattr(variable, "axis", "").upper() == axis_letter:
            values = np.asarray(variable[:], dtype=float)
            if values.ndim == 1:
                return name, values
    raise IntegrationError(f"Could not find one-dimensional {standard_name} coordinates.")


def time_coordinate(dataset: Dataset) -> tuple[str, dict[int, int], list[int]]:
    for name, variable in dataset.variables.items():
        if getattr(variable, "standard_name", "").lower() == "time" or getattr(variable, "axis", "").upper() == "T":
            years = [int(value.year) for value in num2date(
                variable[:], variable.units, getattr(variable, "calendar", "standard"),
                only_use_cftime_datetimes=False,
            )]
            return name, {year: index for index, year in enumerate(years)}, years
    raise IntegrationError("A selected Bio-ORACLE product has no decodable time coordinate.")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return value.as_posix()
    return str(value)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=json_default) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_obis_csv(path: Path) -> tuple[list[str], list[dict[str, str | None]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration as error:
            raise IntegrationError(f"OBIS CSV is empty: {path}") from error
        if len(headers) != len(set(headers)):
            raise IntegrationError("Cleaned OBIS CSV has duplicate column names; preserve and resolve before integration.")
        rows = list(csv.DictReader(handle, fieldnames=headers))
    for row in rows:
        if None in row:
            raise IntegrationError("A cleaned OBIS CSV row has more values than its header.")
    return headers, rows


def selected_products(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != "oceavera-bio-oracle-cleaning-manifest-v2":
        raise IntegrationError("Unexpected Bio-ORACLE cleaning manifest format.")
    products = manifest.get("products", [])
    if len(products) != manifest.get("product_count"):
        raise IntegrationError("Bio-ORACLE manifest product count does not match its product list.")
    chosen = [
        item for item in products
        if "_baseline_" in item["dataset_id"]
        or "_ssp245_" in item["dataset_id"]
        or item["dataset_id"] == "terrain_characteristics"
    ]
    review_products = [item for item in chosen if item.get("disposition") == "review_required"]
    if review_products:
        summary_path = manifest_path.with_name("cleaning_summary.json")
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
        global_issues = summary.get("global_issues") or []
        if isinstance(global_issues, dict):
            global_issues = [global_issues]
        global_issue = next(
            (item for item in global_issues if item.get("code") == "marine_mask_unresolved"),
            {},
        )
        if global_issue.get("code") != "marine_mask_unresolved" or len(review_products) != 1:
            raise IntegrationError("Selected products have an unresolved review status unrelated to the documented marine-mask issue.")
        details = global_issue.get("details", {})
        manifest["integration_review_context"] = {
            "code": global_issue.get("code"),
            "severity": global_issue.get("severity"),
            "status": details.get("status"),
            "missing_values_inside_candidate_domain": details.get("missing_values_inside_candidate_domain"),
            "candidate_domain_interpreted_as_marine": False,
            "note": "The cleaning review is preserved; masked environmental cells remain null and the candidate domain is not used as a marine filter.",
        }
    counts = Counter(
        "terrain" if item["dataset_id"] == "terrain_characteristics"
        else "ssp245" if "_ssp245_" in item["dataset_id"]
        else "baseline" for item in chosen
    )
    if counts != Counter({"baseline": 55, "ssp245": 50, "terrain": 1}):
        raise IntegrationError(f"Selected product inventory changed unexpectedly: {dict(counts)}")
    return manifest, chosen


def inspect_product(
    product: dict[str, Any],
    root: Path,
    expected_grid: tuple[np.ndarray, np.ndarray] | None,
) -> tuple[dict[str, Any], tuple[np.ndarray, np.ndarray]]:
    if product.get("disposition") not in {"validated", "review_required"}:
        raise IntegrationError(f"Source product was not accepted for read-only integration: {product['dataset_id']}")
    path = root / product["product_path"]
    if not path.is_file() or path.stat().st_size != product.get("output_bytes"):
        raise IntegrationError(f"Cleaned NetCDF is missing or its size differs from its manifest: {product['dataset_id']}")
    actual_sha = file_sha256(path)
    if actual_sha != product.get("output_sha256"):
        raise IntegrationError(f"Cleaned NetCDF checksum differs from its manifest: {product['dataset_id']}")
    with Dataset(path, "r") as dataset:
        title = str(getattr(dataset, "title", ""))
        source_version = str(getattr(dataset, "source", ""))
        if "bio-oracle" not in source_version.lower():
            raise IntegrationError(f"Unexpected environmental publisher metadata in {product['dataset_id']}.")
        lat_name, latitudes = axis_variable(dataset, "latitude", "Y")
        lon_name, longitudes = axis_variable(dataset, "longitude", "X")
        cell_edges(latitudes)
        cell_edges(longitudes)
        if expected_grid is not None and (
            not np.allclose(latitudes, expected_grid[0], rtol=0, atol=1e-6)
            or not np.allclose(longitudes, expected_grid[1], rtol=0, atol=1e-6)
        ):
            raise IntegrationError(f"Raster axes differ from the shared grid in {product['dataset_id']}.")
        time_name, time_indexes, time_years = time_coordinate(dataset)
        scenario = scenario_from_metadata(title, product["dataset_id"], time_years)
        depth = depth_from_title(title)
        variables: list[dict[str, Any]] = []
        for name in product.get("variables", []):
            if name not in dataset.variables:
                raise IntegrationError(f"Manifest variable {name} is absent from {product['dataset_id']}.")
            variable = dataset.variables[name]
            dimensions = list(variable.dimensions)
            if not {lat_name, lon_name}.issubset(dimensions):
                raise IntegrationError(f"Variable {name} lacks the declared raster axes.")
            if time_name not in dimensions:
                raise IntegrationError(f"Variable {name} has no time dimension in {product['dataset_id']}.")
            if len(dimensions) != 3:
                raise IntegrationError(f"Unexpected dimensions for {name} in {product['dataset_id']}: {dimensions}")
            variables.append({
                "name": name,
                "column": feature_column(name, depth),
                "dimensions": dimensions,
                "shape": list(variable.shape),
                "dtype": str(variable.dtype),
                "units": str(getattr(variable, "units", "")),
                "long_name": str(getattr(variable, "long_name", "")),
                "standard_name": str(getattr(variable, "standard_name", "")),
                "fill_value": json_default(getattr(variable, "_FillValue", None)),
                "missing_value": json_default(getattr(variable, "missing_value", None)),
                "scale_factor": json_default(getattr(variable, "scale_factor", None)),
                "add_offset": json_default(getattr(variable, "add_offset", None)),
            })
        metadata = {
            "dataset_id": product["dataset_id"],
            "path": product["product_path"],
            "scenario": scenario,
            "depth": depth,
            "cleaning_disposition": product.get("disposition"),
            "global_quality_review": product.get("disposition") == "review_required",
            "title": title,
            "publisher_version": source_version,
            "sha256": actual_sha,
            "bytes": path.stat().st_size,
            "latitude_variable": lat_name,
            "longitude_variable": lon_name,
            "time_variable": time_name,
            "time_years": time_years,
            "time_indexes_by_year": time_indexes,
            "latitude_count": len(latitudes),
            "longitude_count": len(longitudes),
            "variables": variables,
        }
    return metadata, (latitudes, longitudes)


def build_feature_inventory(products: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    features: dict[str, dict[str, Any]] = {}
    for product in products:
        scenario = product["scenario"]
        for variable in product["variables"]:
            column = variable["column"]
            policy = unit_policy(variable["name"], variable["units"], variable["standard_name"])
            feature = features.setdefault(column, {
                "column": column,
                "variable_name": variable["name"],
                "depth": product["depth"],
                "units": policy["standardized_units"],
                "long_name": variable["long_name"],
                "standard_name": variable["standard_name"],
                "source_units_by_period": {},
                "conversion_by_period": {},
                "sources": {},
            })
            if (feature["variable_name"], feature["depth"]) != (variable["name"], product["depth"]):
                raise IntegrationError(f"Feature key collision for {column}.")
            if feature["units"] != policy["standardized_units"]:
                raise IntegrationError(f"Shared source units cannot be harmonized for {column}.")
            if unit_key(feature["long_name"]) != unit_key(variable["long_name"]):
                raise IntegrationError(f"Shared source long_name differs for {column}.")
            if unit_key(feature["standard_name"]) != unit_key(variable["standard_name"]):
                raise IntegrationError(f"Shared source standard_name differs for {column}.")
            years = product["time_indexes_by_year"]
            if scenario == "baseline":
                for target_year in (2000, 2010):
                    if target_year in years:
                        period = f"baseline_{target_year}"
                        if period in feature["sources"]:
                            raise IntegrationError(f"Two baseline sources define {column} at {target_year}.")
                        feature["source_units_by_period"][period] = variable["units"]
                        feature["conversion_by_period"][period] = policy["conversion"]
                        feature["sources"][period] = {
                            "dataset_id": product["dataset_id"], "time_index": years[target_year],
                            "time_coordinate_year": target_year,
                            "source_units": variable["units"],
                            "conversion": policy["conversion"],
                        }
            elif scenario == "ssp245" and 2020 in years:
                if "ssp245_2020" in feature["sources"]:
                    raise IntegrationError(f"Two SSP245 sources define {column} at 2020.")
                feature["source_units_by_period"]["ssp245_2020"] = variable["units"]
                feature["conversion_by_period"]["ssp245_2020"] = policy["conversion"]
                feature["sources"]["ssp245_2020"] = {
                    "dataset_id": product["dataset_id"], "time_index": years[2020],
                    "time_coordinate_year": 2020,
                    "source_units": variable["units"],
                    "conversion": policy["conversion"],
                }
            elif scenario == "terrain":
                if "static" in feature["sources"]:
                    raise IntegrationError(f"Two terrain sources define {column}.")
                feature["source_units_by_period"]["static"] = variable["units"]
                feature["conversion_by_period"]["static"] = policy["conversion"]
                feature["sources"]["static"] = {
                    "dataset_id": product["dataset_id"], "time_index": 0,
                    "source_units": variable["units"], "conversion": policy["conversion"],
                }
    for feature in features.values():
        feature["quarantined_periods"] = []
        feature["quarantine_reasons_by_period"] = {}
        for period, source in feature["sources"].items():
            policy = unit_policy(feature["variable_name"], source["source_units"], feature["standard_name"])
            source["scientific_status"] = policy.get("scientific_status", "retained_source_values")
            if policy.get("quarantine_reason"):
                source["quarantine_reason"] = policy["quarantine_reason"]
                feature["quarantined_periods"].append(period)
                feature["quarantine_reasons_by_period"][period] = policy["quarantine_reason"]
    return features


def write_catalog(
    manifest: dict[str, Any],
    all_products: list[dict[str, Any]],
    selected_metadata: list[dict[str, Any]],
    features: dict[str, dict[str, Any]],
    json_path: Path,
    markdown_path: Path,
) -> dict[str, Any]:
    selected_by_id = {item["dataset_id"]: item for item in selected_metadata}
    product_rows = []
    selected_ids = set(selected_by_id)
    for item in all_products:
        record = {
            "dataset_id": item["dataset_id"],
            "disposition": item["disposition"],
            "product_path": item["product_path"],
            "sha256": item["output_sha256"],
            "bytes": item["output_bytes"],
            "variables": item["variables"],
            "selected_for_integration": item["dataset_id"] in selected_ids,
        }
        if item["dataset_id"] in selected_by_id:
            info = selected_by_id[item["dataset_id"]]
            record.update({
                "scenario_from_title": info["scenario"],
                "depth_from_title": info["depth"],
                "netcdf_title": info["title"],
                "cleaning_disposition": info["cleaning_disposition"],
                "global_quality_review": info["global_quality_review"],
                "time_coordinate_years": info["time_years"],
                "latitude_count": info["latitude_count"],
                "longitude_count": info["longitude_count"],
            })
        product_rows.append(record)
    category_counts = Counter(item["scenario"] for item in selected_metadata)
    feature_rows = sorted(features.values(), key=lambda item: item["column"])
    catalog = {
        "format": "oceavera-obis-bio-oracle-variable-catalog-v1",
        "source_manifest": "data/interim/bio_oracle/cleaning/manifest.json",
        "source_manifest_format": manifest["format"],
        "source_product_count": len(all_products),
        "selected_product_count": len(selected_metadata),
        "selected_product_counts": dict(category_counts),
        "selected_variable_name_count": len({v["name"] for p in selected_metadata for v in p["variables"]}),
        "feature_column_count": len(features),
        "cleaning_review_context": manifest.get("integration_review_context"),
        "time_interpretation": PERIOD_LABELS,
        "products": product_rows,
        "features": feature_rows,
    }
    write_json(json_path, catalog)
    by_depth = Counter(item["depth"] for item in feature_rows)
    lines = [
        "# OBIS–Bio-ORACLE source variable catalog",
        "",
        "Catalog generated from the cleaned Bio-ORACLE manifest and the actual selected NetCDF metadata. Product titles establish declared scenario and depth; the NetCDF time coordinate establishes the selected slice.",
        "",
        f"- Cleaned source products inventoried: **{len(all_products)}**",
        f"- Products selected for integration: **{len(selected_metadata)}** (55 baseline, 50 SSP245, one static terrain product)",
        f"- Distinct NetCDF variable names: **{catalog['selected_variable_name_count']}**",
        f"- Output feature columns: **{len(features)}**",
        "- Future scenario selected for 2020–2026: **SSP245**, using actual time coordinate 2020.",
        "- Baseline slices: actual time coordinates 2000 and 2010.",
        "- Static terrain is recorded as benthic/static from the NetCDF title; its 1970 time label is not treated as an observation year.",
        "",
        "## Feature columns by depth",
        "",
        "| Depth declared in NetCDF title | Feature columns |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {depth} | {count} |" for depth, count in sorted(by_depth.items()))
    lines.extend([
        "",
        "## Feature inventory",
        "",
        "| Output column | NetCDF variable | Depth | Standardized units | Original source units by slice | Baseline slices | SSP245 slice |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for feature in feature_rows:
        baseline = ", ".join(str(year) for year in (2000, 2010) if f"baseline_{year}" in feature["sources"]) or "—"
        future = "2020" if "ssp245_2020" in feature["sources"] else "—"
        source_units = ", ".join(
            f"{period}: {unit or 'not declared'}"
            for period, unit in sorted(feature["source_units_by_period"].items())
        ) or "not declared"
        lines.append(f"| `{feature['column']}` | `{feature['variable_name']}` | {feature['depth']} | {feature['units'] or 'not declared'} | {source_units} | {baseline} | {future} |")
    lines.extend([
        "",
        'The machine-readable record includes all 356 product identities, source checksums, original metadata and per-period quarantine reasons. Original baseline absolute tas, all tas_range and clt_sd have unresolved semantics and are published as null. SSP245 absolute tas remains unchanged in degree_C. Completeness excludes quarantined definitions for that period. Regular cloud fractions retain dimensionless decoded values. Columns remain defined even when quarantined, masked or unavailable.',
        "A selected product carrying `review_required` remains flagged because the cleaning review concerns the unresolved marine mask and a masked source cell. The missing value remains null; the candidate non-fill domain is not interpreted as a marine mask.",
        "",
    ])
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return catalog


def read_data_slice(variable: Any, time_name: str, time_index: int, lat_name: str, lon_name: str) -> np.ma.MaskedArray:
    variable.set_auto_maskandscale(True)
    selection: list[Any] = []
    remaining_dimensions: list[str] = []
    for dimension in variable.dimensions:
        if dimension == time_name:
            selection.append(time_index)
        else:
            selection.append(slice(None))
            remaining_dimensions.append(dimension)
    values = np.ma.asarray(variable[tuple(selection)])
    if values.ndim != 2 or set(remaining_dimensions) != {lat_name, lon_name}:
        raise IntegrationError(f"Cannot reduce {variable.name} to a two-dimensional raster slice.")
    if remaining_dimensions != [lat_name, lon_name]:
        values = np.ma.transpose(values, (remaining_dimensions.index(lat_name), remaining_dimensions.index(lon_name)))
    return values


def prepare_period_cells(
    periods: list[str | None], raster_rows: np.ndarray, raster_columns: np.ndarray, width: int,
) -> dict[str, dict[str, np.ndarray]]:
    result: dict[str, dict[str, np.ndarray]] = {}
    for period in ("baseline_2000", "baseline_2010", "ssp245_2020"):
        observation_indexes = np.flatnonzero(
            np.asarray([value == period for value in periods]) & (raster_rows >= 0) & (raster_columns >= 0)
        )
        if not len(observation_indexes):
            continue
        cell_ids = raster_rows[observation_indexes] * width + raster_columns[observation_indexes]
        unique_ids, inverse = np.unique(cell_ids, return_inverse=True)
        result[period] = {
            "observation_indexes": observation_indexes,
            "cell_ids": unique_ids,
            "rows": unique_ids // width,
            "columns": unique_ids % width,
            "inverse": inverse,
        }
    return result


def assign_sampled_cells(
    output: np.ndarray,
    values: np.ma.MaskedArray,
    period_group: dict[str, np.ndarray],
) -> None:
    rows, columns = period_group["rows"], period_group["columns"]
    mask = np.ma.getmaskarray(values)[rows, columns]
    sampled = np.asarray(np.ma.getdata(values), dtype=float)[rows, columns]
    sampled = np.where(mask | ~np.isfinite(sampled), np.nan, sampled)
    output[period_group["observation_indexes"]] = sampled[period_group["inverse"]]


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def validate_geoparquet(path: Path, expected_geo_version: str = "1.1.0") -> dict[str, Any]:
    metadata = parquet.ParquetFile(path).metadata
    schema_metadata = parquet.ParquetFile(path).schema_arrow.metadata or {}
    geo = json.loads(schema_metadata.get(b"geo", b"{}"))
    compression = sorted({
        metadata.row_group(group).column(column).compression
        for group in range(metadata.num_row_groups)
        for column in range(metadata.row_group(group).num_columns)
    })
    if geo.get("version") != expected_geo_version:
        raise IntegrationError(f"Expected GeoParquet {expected_geo_version}, found {geo.get('version')}.")
    if compression != ["ZSTD"]:
        raise IntegrationError(f"Expected ZSTD compression for every column, found {compression}.")
    return {"rows": metadata.num_rows, "columns": metadata.num_columns, "geoparquet_version": geo["version"], "compression": compression}


def publish_geoparquet(frame: gpd.GeoDataFrame, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f".{path.stem}.pending.parquet")
    if pending.exists():
        pending.unlink()
    frame.to_parquet(
        pending, index=False, compression="zstd", geometry_encoding="WKB", schema_version="1.1.0",
    )
    checks = validate_geoparquet(pending)
    pending.replace(path)
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Integrate the cleaned OBIS table with the selected Bio-ORACLE source slices.",
        formatter_class=IntegrationHelpFormatter,
        epilog=(
            "Run from the repository root. --dry-run checks the selected source files, their hashes, "
            "NetCDF metadata and the planned feature inventory, then exits without writing outputs."
        ),
    )
    parser.add_argument(
        "--obis-csv", type=Path, default=OBIS_PATH.relative_to(ROOT),
        metavar="PATH", help="Cleaned OBIS CSV to integrate.",
    )
    parser.add_argument(
        "--bio-oracle-manifest", type=Path,
        default=BIO_MANIFEST_PATH.relative_to(ROOT),
        metavar="PATH", help="Manifest for the cleaned Bio-ORACLE product bundle.",
    )
    parser.add_argument(
        "--output", type=Path, default=OUTPUT_PATH.relative_to(ROOT),
        metavar="PATH", help="GeoParquet output path. An existing output is replaced after validation.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Check sources and build the feature plan without writing the catalog, dataset or reports.",
    )
    args = parser.parse_args()
    root = ROOT
    obis_path = args.obis_csv if args.obis_csv.is_absolute() else root / args.obis_csv
    manifest_path = args.bio_oracle_manifest if args.bio_oracle_manifest.is_absolute() else root / args.bio_oracle_manifest
    output_path = args.output if args.output.is_absolute() else root / args.output

    progress("Step 1/5: checking inputs")
    if not obis_path.is_file():
        parser.error(
            f"Cleaned OBIS CSV not found: {display_path(obis_path)}. "
            "Run Script 4 first or pass its location with --obis-csv."
        )
    if not manifest_path.is_file():
        parser.error(
            f"Bio-ORACLE cleaning manifest not found: {display_path(manifest_path)}. "
            "Run Scripts 6 and 7 first or pass a manifest with --bio-oracle-manifest."
        )
    for option, path in (
        ("--obis-csv", obis_path),
        ("--bio-oracle-manifest", manifest_path),
        ("--output", output_path),
    ):
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            parser.error(f"{option} must point inside the repository: {display_path(path)}")
    if output_path.resolve() in {obis_path.resolve(), manifest_path.resolve()}:
        parser.error("--output must not overwrite either input file.")

    progress(f"Reading cleaned OBIS rows from {display_path(obis_path)}")

    headers, source_rows = read_obis_csv(obis_path)
    if len(headers) != 112 or len(source_rows) != 23_371:
        raise IntegrationError(
            "Expected the cleaned OBIS table to contain 23,371 rows and 112 fields; "
            f"found {len(source_rows):,} rows and {len(headers)} fields."
        )
    progress(f"Loaded {len(source_rows):,} rows and {len(headers)} original fields")
    progress(f"Reading Bio-ORACLE manifest from {display_path(manifest_path)}")
    manifest, products = selected_products(manifest_path)
    all_products = manifest["products"]

    progress(f"Step 2/5: checking {len(products)} selected Bio-ORACLE products and their checksums")
    product_metadata: list[dict[str, Any]] = []
    shared_grid: tuple[np.ndarray, np.ndarray] | None = None
    for product_number, product in enumerate(products, start=1):
        progress(
            f"Checking source {product_number}/{len(products)}: "
            f"{product['dataset_id']} ({product.get('output_bytes', 0):,} bytes)"
        )
        metadata, axes = inspect_product(product, root, shared_grid)
        if shared_grid is None:
            shared_grid = axes
        product_metadata.append(metadata)
    if shared_grid is None:
        raise IntegrationError("No selected Bio-ORACLE product supplied a raster grid.")
    latitudes, longitudes = shared_grid
    features = build_feature_inventory(product_metadata)
    if args.dry_run:
        progress(
            f"Dry run complete: {len(product_metadata)} products, {len(features)} environmental features; "
            "no files were written."
        )
        print_dry_run_summary(
            len(source_rows), len(headers), len(product_metadata), len(features), output_path, root,
        )
        return 0

    progress("Step 3/5: writing the source and feature catalog")
    catalog = write_catalog(
        manifest, all_products, product_metadata, features, CATALOG_JSON_PATH, CATALOG_MD_PATH,
    )

    progress(f"Step 4/5: mapping {len(source_rows):,} observation dates and raster cells")
    observation_years: list[int | None] = []
    date_sources: list[str | None] = []
    periods: list[str | None] = []
    date_statuses: list[str] = []
    temporal_eligibility: list[str] = []
    date_interval_starts: list[int | None] = []
    date_interval_ends: list[int | None] = []
    legacy_years: list[int | None] = []
    longitudes_from_obis = np.full(len(source_rows), np.nan)
    latitudes_from_obis = np.full(len(source_rows), np.nan)
    point_geometries = []
    raster_rows = np.full(len(source_rows), -1, dtype=int)
    raster_columns = np.full(len(source_rows), -1, dtype=int)
    raster_status: list[str] = []
    center_longitudes = np.full(len(source_rows), np.nan)
    center_latitudes = np.full(len(source_rows), np.nan)
    center_distance_km = np.full(len(source_rows), np.nan)

    for index, row in enumerate(source_rows):
        resolution = resolve_observation_date(row)
        year, source_field, period = resolution["year"], resolution["source"], resolution["period"]
        observation_years.append(year)
        date_sources.append(source_field)
        periods.append(period)
        date_statuses.append(resolution["status"])
        temporal_eligibility.append(resolution["eligibility"])
        date_interval_starts.append(resolution["interval_start_year"])
        date_interval_ends.append(resolution["interval_end_year"])
        legacy_years.append(legacy_resolve_year_for_comparison(row))
        try:
            longitude = float(row.get("decimalLongitude") or "nan")
            latitude = float(row.get("decimalLatitude") or "nan")
        except (TypeError, ValueError):
            longitude, latitude = math.nan, math.nan
        longitudes_from_obis[index], latitudes_from_obis[index] = longitude, latitude
        row_index, column_index, status = nearest_cell(longitude, latitude, longitudes, latitudes)
        raster_status.append(status)
        if math.isfinite(longitude) and math.isfinite(latitude) and -180 <= longitude <= 180 and -90 <= latitude <= 90:
            point_geometries.append(Point(longitude, latitude))
        else:
            point_geometries.append(None)
        if row_index is not None and column_index is not None:
            raster_rows[index], raster_columns[index] = row_index, column_index
            center_longitudes[index] = longitudes[column_index]
            center_latitudes[index] = latitudes[row_index]
            center_distance_km[index] = great_circle_km(
                longitude, latitude, center_longitudes[index], center_latitudes[index],
            )
        completed = index + 1
        if completed % 5_000 == 0 or completed == len(source_rows):
            progress(f"Mapped observation locations: {completed:,}/{len(source_rows):,}")

    width = len(longitudes)
    period_cells = prepare_period_cells(periods, raster_rows, raster_columns, width)
    feature_values = {column: np.full(len(source_rows), np.nan, dtype=float) for column in features}
    progress(f"Sampling environmental values from {len(product_metadata)} source products")
    for product_number, product in enumerate(product_metadata, start=1):
        progress(
            f"Reading source values {product_number}/{len(product_metadata)}: "
            f"{product['dataset_id']} ({len(product['variables'])} variables)"
        )
        path = root / product["path"]
        with Dataset(path, "r") as dataset:
            lat_name = product["latitude_variable"]
            lon_name = product["longitude_variable"]
            time_name = product["time_variable"]
            for variable_info in product["variables"]:
                column = variable_info["column"]
                variable = dataset.variables[variable_info["name"]]
                source_plan: list[tuple[str, str, int]] = []
                if product["scenario"] == "baseline":
                    source_plan = [
                        (f"baseline_{year}", f"baseline_{year}", product["time_indexes_by_year"][year])
                        for year in (2000, 2010) if year in product["time_indexes_by_year"]
                    ]
                elif product["scenario"] == "ssp245" and 2020 in product["time_indexes_by_year"]:
                    source_plan = [("ssp245_2020", "ssp245_2020", product["time_indexes_by_year"][2020])]
                elif product["scenario"] == "terrain":
                    source_plan = [(period, "static", 0) for period in period_cells]
                for period, source_key, time_index in source_plan:
                    group = period_cells.get(period)
                    if group is None:
                        continue
                    if source_key not in features[column]["sources"]:
                        continue
                    values = read_data_slice(variable, time_name, time_index, lat_name, lon_name)
                    values = harmonize_source_values(values, variable_info["name"], variable_info["units"])
                    assign_sampled_cells(feature_values[column], values, group)

    progress(f"Environmental extraction complete: {len(features)} feature columns")
    progress("Assembling the GeoDataFrame and coverage indicators")
    frame = pd.DataFrame({column: [row.get(column) for row in source_rows] for column in headers})
    frame["integration_source_row"] = np.arange(1, len(source_rows) + 1, dtype=np.int64)
    frame["resolved_event_year"] = pd.array(observation_years, dtype="Int64")
    frame["resolved_event_year_source"] = date_sources
    frame["temporal_resolution_status"] = date_statuses
    frame["temporal_eligibility"] = temporal_eligibility
    frame["date_interval_start_year"] = pd.array(date_interval_starts, dtype="Int64")
    frame["date_interval_end_year"] = pd.array(date_interval_ends, dtype="Int64")
    frame["environment_period"] = periods
    frame["raster_row"] = pd.array([None if value < 0 else int(value) for value in raster_rows], dtype="Int64")
    frame["raster_column"] = pd.array([None if value < 0 else int(value) for value in raster_columns], dtype="Int64")
    frame["raster_cell_id"] = pd.array([
        None if raster_rows[index] < 0 else int(raster_rows[index] * width + raster_columns[index])
        for index in range(len(source_rows))
    ], dtype="Int64")
    frame["raster_match_status"] = raster_status
    frame["raster_cell_center_longitude"] = center_longitudes
    frame["raster_cell_center_latitude"] = center_latitudes
    frame["raster_cell_distance_km"] = center_distance_km
    frame = pd.concat([frame, pd.DataFrame(feature_values, index=frame.index)], axis=1)

    expected_columns_by_period: dict[str, list[str]] = {}
    for period in ("baseline_2000", "baseline_2010", "ssp245_2020"):
        expected_columns_by_period[period] = [
            column for column, feature in features.items()
            if (period in feature["sources"] or "static" in feature["sources"])
            and period not in feature["quarantined_periods"]
        ]
    nonnull_count = np.zeros(len(source_rows), dtype=int)
    expected_count = np.zeros(len(source_rows), dtype=int)
    for period, columns in expected_columns_by_period.items():
        row_indexes = np.flatnonzero(np.asarray([item == period for item in periods]))
        expected_count[row_indexes] = len(columns)
        if columns:
            nonnull_count[row_indexes] = frame.iloc[row_indexes][columns].notna().sum(axis=1).to_numpy()
    statuses = []
    for index, period in enumerate(periods):
        if period is None:
            if temporal_eligibility[index] == "ambiguous":
                statuses.append("ambiguous_date_assignment")
            elif temporal_eligibility[index] == "ineligible":
                statuses.append("outside_supported_time_range")
            else:
                statuses.append("missing_or_invalid_date")
        elif raster_status[index] != "matched":
            statuses.append("no_spatial_match")
        elif expected_count[index] == 0:
            statuses.append("no_matching_source_time_coordinate")
        elif nonnull_count[index] == expected_count[index]:
            statuses.append("complete_environmental_values")
        elif nonnull_count[index] > 0:
            statuses.append("partial_environmental_values")
        else:
            statuses.append("no_valid_source_values_at_cell")
    frame["expected_environment_feature_count"] = expected_count
    frame["present_environment_feature_count"] = nonnull_count
    frame["environmental_coverage_status"] = statuses
    geodata = gpd.GeoDataFrame(frame, geometry=point_geometries, crs="EPSG:4326")

    progress(f"Step 5/5: publishing GeoParquet to {display_path(output_path, root)}")
    if output_path.exists():
        progress("The existing output will be replaced after the new file passes validation")
    write_checks = publish_geoparquet(geodata, output_path)
    progress("GeoParquet written; reading it back for integrity checks")
    readback = gpd.read_parquet(output_path)
    if len(readback) != len(source_rows):
        raise IntegrationError("GeoParquet read-back row count differs from cleaned OBIS.")
    if readback["integration_source_row"].tolist() != list(range(1, len(source_rows) + 1)):
        raise IntegrationError("GeoParquet read-back changed the OBIS source row sequence.")
    for field_number, column in enumerate(headers, start=1):
        actual_values = readback[column].tolist()
        for index, expected in enumerate(row.get(column) for row in source_rows):
            actual = actual_values[index]
            if expected is None:
                if not is_missing(actual):
                    raise IntegrationError(f"Source null was changed in GeoParquet field {column}.")
            elif is_missing(actual) or str(actual) != expected:
                raise IntegrationError(f"Cleaned OBIS field changed during integration: {column}, row {index + 1}.")
        if field_number % 16 == 0 or field_number == len(headers):
            progress(f"Verified original OBIS fields: {field_number}/{len(headers)}")
    progress(f"Verifying {len(readback):,} observation geometries")
    for index, geometry in enumerate(readback.geometry):
        expected_geometry = point_geometries[index]
        if expected_geometry is None:
            if geometry is not None:
                raise IntegrationError(f"Invalid source coordinate became a geometry at row {index + 1}.")
        elif geometry is None or not (
            math.isclose(geometry.x, expected_geometry.x, rel_tol=0, abs_tol=1e-12)
            and math.isclose(geometry.y, expected_geometry.y, rel_tol=0, abs_tol=1e-12)
        ):
            raise IntegrationError(f"Source observation geometry changed at row {index + 1}.")
        completed = index + 1
        if completed % 5_000 == 0 or completed == len(readback):
            progress(f"Verified observation geometries: {completed:,}/{len(readback):,}")
    final_checks = validate_geoparquet(output_path)

    year_counts = Counter(str(year) if year is not None else "missing_or_invalid" for year in observation_years)
    period_counts = Counter(period or "no_supported_slice" for period in periods)
    date_status_counts = Counter(date_statuses)
    temporal_eligibility_counts = Counter(temporal_eligibility)
    legacy_period_counts = Counter(temporal_period(year) or "no_supported_slice" for year in legacy_years)
    changed_period_assignments = sum(
        new_period != temporal_period(old_year)
        for new_period, old_year in zip(periods, legacy_years)
    )
    changed_year_assignments = sum(new_year != old_year for new_year, old_year in zip(observation_years, legacy_years))
    raster_counts = Counter(raster_status)
    coverage_counts = Counter(statuses)
    feature_report = {}
    for column, feature in features.items():
        values = frame[column]
        has_source = np.asarray([
            period is not None and (period in feature["sources"] or "static" in feature["sources"])
            for period in periods
        ])
        has_cell = np.asarray([status == "matched" for status in raster_status])
        present = values.notna().to_numpy()
        quarantined = np.asarray([period in feature["quarantined_periods"] for period in periods])
        feature_report[column] = {
            "variable_name": feature["variable_name"],
            "depth": feature["depth"],
            "units": feature["units"],
            "source_units_by_period": feature["source_units_by_period"],
            "conversion_by_period": feature["conversion_by_period"],
            "source_periods": sorted(key for key in feature["sources"] if key != "static"),
            "has_static_source": "static" in feature["sources"],
            "quarantined_periods": feature["quarantined_periods"],
            "quarantine_reasons_by_period": feature["quarantine_reasons_by_period"],
            "non_null_count": int(values.notna().sum()),
            "null_count": int(values.isna().sum()),
            "legitimate_zero_count": int((values.fillna(np.nan) == 0).sum()),
            "null_unsupported_or_out_of_period": int((~has_source).sum()),
            "null_without_raster_match": int((has_source & ~has_cell).sum()),
            "null_quarantined_source_semantics": int((has_source & has_cell & quarantined).sum()),
            "null_at_matched_source_cell": int((has_source & has_cell & ~quarantined & ~present).sum()),
        }
    report = {
        "format": "oceavera-spatiotemporal-integration-report-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Cleaned OBIS rows matched to source NetCDF values by nearest in-extent cell centres; source time coordinate and NetCDF title metadata determine compatibility.",
        "date_resolution_policy": {
            "single_year_evidence_priority": list(SINGLE_DATE_FIELDS),
            "interval_fields": ["eventDate", "date_start", "date_end"],
            "epoch_units": "OBIS date_start/date_mid/date_end numeric epochs are milliseconds; date_mid is point evidence, start/end bound an interval.",
            "interval_rule": "A single-year candidate resolves only when all parsed single-year evidence maps to one environmental period and lies inside any supplied interval. An interval without a single-year candidate is eligible only when wholly contained in one supported environmental period. Cross-period or conflicting evidence is ambiguous and excluded from the strict temporal dataset, but retained in the full archive.",
            "date_year_rule": "date_year is treated as single-year evidence and must agree by environmental period with other single-year evidence.",
        },
        "date_resolution_comparison_to_previous_rule": {
            "previous_first_parseable_year_counts_by_period": dict(legacy_period_counts),
            "corrected_environment_period_counts": dict(period_counts),
            "rows_with_changed_resolved_year": int(changed_year_assignments),
            "rows_with_changed_or_ambiguous_environment_period": int(changed_period_assignments),
            "corrected_resolution_status_counts": dict(date_status_counts),
            "strict_temporal_eligibility_counts": dict(temporal_eligibility_counts),
        },
        "temporal_slice_policy": PERIOD_LABELS,
        "future_scenario_assumption": "SSP245, using actual 2020 coordinate; scenario choice is an assumption, not an OBIS-derived fact.",
        "static_terrain_policy": "Terrain variables are treated as static from their declared Benthic title; the 1970 coordinate is not assigned as an occurrence year.",
        "netcdf_value_handling": "netCDF4 automatic masking and scale/offset are explicitly enabled; no second scale_factor/add_offset calculation is performed.",
        "scientific_quarantine_policy": "Original sources are immutable. Unresolved baseline absolute tas, all tas_range and clt_sd values are null; columns/source metadata remain in the catalogue. Completeness excludes quarantined definitions in the relevant period.",
        "usable_features_by_period": {period: len(columns) for period, columns in expected_columns_by_period.items()},
        "sources": {
            "obis_csv": display_path(obis_path, root),
            "obis_csv_sha256": file_sha256(obis_path),
            "bio_oracle_manifest": display_path(manifest_path, root),
            "bio_oracle_cleaning_manifest_sha256": file_sha256(manifest_path),
            "cleaned_bio_oracle_product_count": len(all_products),
            "selected_source_products": len(product_metadata),
            "selected_source_counts": dict(Counter(item["scenario"] for item in product_metadata)),
            "selected_product_variable_name_count": catalog["selected_variable_name_count"],
            "selected_product_checksums_verified": True,
            "netcdf_publisher_version": "Bio-Oracle version V3.0",
            "cleaning_review_context": manifest.get("integration_review_context"),
        },
        "output": {
            "path": display_path(output_path, root),
            "sha256": file_sha256(output_path),
            "bytes": output_path.stat().st_size,
            **final_checks,
            "initial_writer_readback": write_checks,
        },
        "spatial_grid": {
            "crs": "EPSG:4326",
            "rows": len(latitudes),
            "columns": len(longitudes),
            "latitude_axis_centres": [float(value) for value in latitudes],
            "longitude_axis_centres": [float(value) for value in longitudes],
            "axis_serialization": "JSON decimal numbers that round-trip to IEEE-754 binary64; cell edges are adjacent-centre midpoints with half-spacing extrapolation at the outer edges.",
            "latitude_min_center": float(min(latitudes)),
            "latitude_max_center": float(max(latitudes)),
            "longitude_min_center": float(min(longitudes)),
            "longitude_max_center": float(max(longitudes)),
            "latitude_axis_sha256": hashlib.sha256(np.asarray(latitudes, dtype="<f8").tobytes()).hexdigest(),
            "longitude_axis_sha256": hashlib.sha256(np.asarray(longitudes, dtype="<f8").tobytes()).hexdigest(),
            "nearest_cell_tie_rule": "Lowest zero-based array index.",
            "point_to_centre_distance": "Haversine distance on a 6,371.0088 km mean-radius sphere.",
        },
        "records": {
            "cleaned_obis_rows": len(source_rows),
            "original_obis_field_count": len(headers),
            "original_obis_fields_preserved_exactly": len(headers),
            "output_fields": len(geodata.columns),
            "resolved_year_counts": dict(year_counts),
            "temporal_period_counts": dict(period_counts),
            "temporal_resolution_status_counts": dict(date_status_counts),
            "temporal_eligibility_counts": dict(temporal_eligibility_counts),
            "legacy_period_counts_for_comparison": dict(legacy_period_counts),
            "rows_with_changed_resolved_year": int(changed_year_assignments),
            "rows_with_changed_or_ambiguous_environment_period": int(changed_period_assignments),
            "raster_match_status_counts": dict(raster_counts),
            "environmental_coverage_status_counts": dict(coverage_counts),
            "distinct_matched_cells": int(len({
                int(row * width + column) for row, column in zip(raster_rows, raster_columns) if row >= 0
            })),
        },
        "feature_columns": feature_report,
        "limits": [
            "The source cleaning review remains open for the unresolved marine-mask convention and one missing value inside its candidate non-fill domain.",
            "The 2000/2010 baseline coordinate labels do not prove each layer's exact averaging window.",
            "The 2020–2026 rows use an SSP245 2020 decadal projection slice and are not annual environmental observations.",
            "A matching Bio-ORACLE raster cell does not independently establish that an OBIS location is marine.",
            "No species target, absence, background, ecological filter, or model feature selection is performed.",
            "Baseline absolute tas, all tas_range and clt_sd remain source-semantic quarantines; null values are deliberate and source arrays are preserved.",
        ],
    }
    write_json(REPORT_JSON_PATH, report)
    markdown = [
        "# OBIS–Bio-ORACLE integration run summary",
        "",
        f"- Cleaned OBIS rows preserved: **{len(source_rows):,}**",
        f"- Original OBIS fields preserved exactly: **{len(headers)} of {len(headers)}**",
        f"- Output environmental feature columns: **{len(features)}**",
        f"- Selected source products: **{len(product_metadata)}** (55 baseline, 50 SSP245, one static terrain product)",
        f"- Output: `{display_path(output_path, root)}` ({output_path.stat().st_size:,} bytes)",
        f"- Format: GeoParquet {final_checks['geoparquet_version']}, compression {', '.join(final_checks['compression'])}",
        f"- Distinct raster cells occupied by source observations: **{report['records']['distinct_matched_cells']:,}**",
        "",
        "## Temporal assignments",
        "",
        "| Time mapping | Source rows |",
        "| --- | ---: |",
    ]
    markdown.extend(f"| {PERIOD_LABELS.get(key, key)} | {count:,} |" for key, count in period_counts.items())
    markdown.extend([
        "",
        "## Spatial and environmental coverage",
        "",
        "| Status | Rows |",
        "| --- | ---: |",
    ])
    markdown.extend(f"| {key} | {count:,} |" for key, count in raster_counts.items())
    markdown.extend(["", "| Environmental value status | Rows |", "| --- | ---: |"])
    markdown.extend(f"| {key} | {count:,} |" for key, count in coverage_counts.items())
    markdown.extend([
        "",
        "The full per-feature non-null, null, legitimate-zero and source-period counts are in the machine-readable manifest. NetCDF fill masks and scale/offset metadata were handled by netCDF4 automatic decoding exactly once.",
        "A matched raster cell does not prove marine eligibility. The separate temporal, marine and grid workflow records that evidence gate.",
        "",
    ])
    REPORT_MD_PATH.write_text("\n".join(markdown), encoding="utf-8")
    progress("GeoParquet publication and read-back checks passed")
    print_integration_summary(
        len(source_rows), len(headers), len(features), output_path, final_checks,
        dict(raster_counts), dict(coverage_counts), root,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IntegrationError as error:
        print(f"Integration stopped: {error}", file=sys.stderr)
        raise SystemExit(2)
    except (OSError, json.JSONDecodeError, UnicodeError) as error:
        print(f"Could not read or write an integration file: {error}", file=sys.stderr)
        raise SystemExit(2)
