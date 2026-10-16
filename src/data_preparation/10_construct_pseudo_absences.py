
"""Build a long-format full-population presence/background candidate dataset.

All Policy B observations remain positive rows. Separate sampled marine
background rows are comparison examples, not confirmed species absences.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as parquet
from netCDF4 import Dataset, num2date
from shapely import contains_xy
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS = ROOT / "data/interim/integrated/gridded/grid_observations.parquet"
MASK = ROOT / "data/interim/geography/sri_lanka_marine_water.gpkg"
MASK_PROVENANCE = ROOT / "docs/records/2026-10-16-gshhg-marine-reference.json"
MANIFEST = ROOT / "docs/records/2026-10-16-integration-manifest.json"
CATALOG = ROOT / "docs/records/2026-10-16-integration-variable-catalog.json"
OUTPUT = ROOT / "data/interim/pseudo_absence/presence_background_candidates.parquet"
REPORT = ROOT / "docs/records/2026-10-16-full-population-presence-background-construction.json"
REPORT_MARKDOWN = REPORT.with_suffix(".md")
EVALUATION_PLAN = ROOT / "docs/records/2026-10-16-full-population-presence-background-evaluation-plan.md"
DATA_DICTIONARY = ROOT / "docs/records/2026-10-16-full-population-presence-background-data-dictionary.md"
DECISION = ROOT / "docs/records/2026-10-16-decision-paired-presence-background.md"
HISTORICAL_REPORT = ROOT / "docs/records/2026-10-16-presence-background-construction.json"
HISTORICAL_REPORT_MARKDOWN = HISTORICAL_REPORT.with_suffix(".md")
HISTORICAL_EVALUATION_PLAN = ROOT / "docs/records/2026-10-16-presence-background-evaluation-plan.md"
ARCHIVE_DIR = ROOT / "data/interim/pseudo_absence/archive/d055_three_species"
ARCHIVE_MANIFEST = ROOT / "docs/records/2026-10-16-presence-background-archive-manifest.json"
NESTED_REPORT = ROOT / "docs/records/2026-10-16-paired-presence-background-construction.json"
NESTED_REPORT_MARKDOWN = NESTED_REPORT.with_suffix(".md")
NESTED_DATA_DICTIONARY = ROOT / "docs/records/2026-10-16-paired-presence-background-data-dictionary.md"
NESTED_EVALUATION_PLAN = ROOT / "docs/records/2026-10-16-paired-presence-background-evaluation-plan.md"
NESTED_ARCHIVE_DIR = ROOT / "data/interim/pseudo_absence/archive/d056_nested_columns"
NESTED_ARCHIVE_MANIFEST = ROOT / "docs/records/2026-10-16-nested-paired-background-archive-manifest.json"

SEED = 20261016
PERIODS = {
    "2000-2009": "baseline_2000",
    "2010-2019": "baseline_2010",
    "2020-2026": "ssp245_2020",
}

# Eligibility checks only; final ML feature selection will occur later.
CORE = (
    "bio_oracle__thetao_mean__depthsurf",
    "bio_oracle__so_mean__depthsurf",
    "bio_oracle__o2_mean__depthsurf",
    "bio_oracle__chl_mean__depthsurf",
    "bio_oracle__ph_mean__depthsurf",
    "bio_oracle__bathymetry_mean__benthic",
)

OUTPUT_COLUMNS = (
    "presence_background_label",
    "sample_type",
    "target_taxon_key",
    "paired_presence_source_row",
    "eligible_species_level_ml",
    "ml_eligibility_reason",
    "background_sampling_method",
    "sample_id",
)

INTEGRATED_DATASETS = {
    "full": ROOT / "data/interim/integrated/full/integrated_observations.parquet",
    "temporal": ROOT / "data/interim/integrated/temporal/observations_2000_2026.parquet",
    "marine": ROOT / "data/interim/integrated/marine/marine_observations.parquet",
    "grid": OBSERVATIONS,
    "species_cell_period_summary": ROOT / "data/interim/integrated/gridded/species_cell_period_summary.parquet",
}

ENVIRONMENT_PERIODS = set(PERIODS.values())
VALUE_ATOL = 1e-10
VALUE_RTOL = 1e-10


def sha256(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def integration_utilities():
    """Reuse verified NetCDF masking/unit handling without running Script 08."""
    source = ROOT / "src/data_preparation/08_integrate_spatiotemporal_data.py"
    spec = importlib.util.spec_from_file_location("oceavera_readonly_netcdf", source)

    if not spec or not spec.loader:
        raise RuntimeError("Cannot locate existing integration utilities")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return module


def require_fields(df: pd.DataFrame, names: list[str]) -> None:
    missing = set(names) - set(df.columns)
    if missing:
        raise ValueError(f"Required fields missing: {sorted(missing)}")


def cell_centres(manifest: dict):
    """Read and verify the exact original Bio-ORACLE grid axes."""
    grid = manifest["spatial_grid"]
    lat = np.asarray(grid["latitude_axis_centres"], dtype="<f8")
    lon = np.asarray(grid["longitude_axis_centres"], dtype="<f8")

    for label, axis in (("latitude", lat), ("longitude", lon)):
        actual = hashlib.sha256(axis.tobytes()).hexdigest()
        if actual != grid[f"{label}_axis_sha256"]:
            raise ValueError(f"Changed {label} raster axis")

    rows, cols = np.indices((len(lat), len(lon)))
    return lat, lon, rows.ravel(), cols.ravel()


def boolean_mask(series: pd.Series, expected: bool) -> pd.Series:
    """Read bool columns consistently whether Parquet stored bool or text."""
    values = series.fillna("").astype(str).str.strip().str.casefold()
    return values.eq("true" if expected else "false")


def verify_observation_grid(
    observations: gpd.GeoDataFrame,
    lat: np.ndarray,
    lon: np.ndarray,
) -> dict[str, int]:
    """Check stored integer indices, IDs, centres and source points."""
    required = [
        "raster_row", "raster_column", "raster_cell_id", "grid_cell_id",
        "raster_cell_center_latitude", "raster_cell_center_longitude",
        "integration_source_row", "geometry",
    ]
    require_fields(observations, required)
    rows = pd.to_numeric(observations["raster_row"], errors="raise").to_numpy(int)
    cols = pd.to_numeric(observations["raster_column"], errors="raise").to_numpy(int)
    if np.any(rows < 0) or np.any(rows >= len(lat)):
        raise ValueError("Observation raster rows fall outside the saved axis")
    if np.any(cols < 0) or np.any(cols >= len(lon)):
        raise ValueError("Observation raster columns fall outside the saved axis")
    expected = rows * len(lon) + cols
    for name in ("raster_cell_id", "grid_cell_id"):
        actual = pd.to_numeric(observations[name], errors="raise").to_numpy(int)
        if not np.array_equal(expected, actual):
            raise ValueError(f"Stored {name} disagrees with raster indices")

    centre_lat = pd.to_numeric(
        observations["raster_cell_center_latitude"], errors="raise"
    ).to_numpy(float)
    centre_lon = pd.to_numeric(
        observations["raster_cell_center_longitude"], errors="raise"
    ).to_numpy(float)
    if not np.allclose(centre_lat, lat[rows], rtol=0, atol=1e-6):
        raise ValueError("Stored raster-centre latitudes disagree with axes")
    if not np.allclose(centre_lon, lon[cols], rtol=0, atol=1e-6):
        raise ValueError("Stored raster-centre longitudes disagree with axes")
    if not observations["integration_source_row"].is_unique:
        raise ValueError("Duplicate source-row identifiers")
    if not observations.geometry.geom_type.eq("Point").all():
        raise ValueError("Policy B grid observations must retain Point geometry")

    return {
        "rows_checked": len(observations),
        "raster_index_discrepancies": 0,
        "raster_centre_discrepancies": 0,
        "duplicate_source_row_ids": 0,
    }


def axis_variable(dataset: Dataset, kind: str) -> tuple[str, np.ndarray]:
    standard_name, axis_letter = {
        "latitude": ("latitude", "Y"),
        "longitude": ("longitude", "X"),
    }[kind]
    for name, variable in dataset.variables.items():
        if (
            getattr(variable, "standard_name", "").casefold() == standard_name
            or getattr(variable, "axis", "").upper() == axis_letter
        ):
            values = np.asarray(variable[:], dtype=float)
            if values.ndim == 1:
                return name, values
    raise ValueError(f"Cannot find the one-dimensional {kind} coordinate")


def time_variable(dataset: Dataset) -> tuple[str, np.ndarray]:
    for name, variable in dataset.variables.items():
        if (
            getattr(variable, "standard_name", "").casefold() == "time"
            or getattr(variable, "axis", "").upper() == "T"
        ):
            values = np.asarray(variable[:])
            if values.ndim == 1 and getattr(variable, "units", None):
                return name, values
    raise ValueError("Selected NetCDF product has no decodable time axis")


def verify_catalogue_sources(
    manifest: dict,
    catalog: dict,
) -> tuple[dict[str, dict], dict[str, Path], dict[str, dict], dict]:
    """Audit product paths, checksums, variable names, axes and time indices."""
    feature_list = catalog.get("features", [])
    feature_entries = {entry["column"]: entry for entry in feature_list}
    if len(feature_entries) != 382 or len(feature_entries) != len(feature_list):
        raise ValueError("Expected 382 unique environmental feature definitions")
    if set(CORE) - set(feature_entries):
        raise ValueError("One or more required core features are absent")

    products = {entry["dataset_id"]: entry for entry in catalog.get("products", [])}
    if len(products) != len(catalog.get("products", [])):
        raise ValueError("Duplicate Bio-ORACLE dataset identifiers in catalogue")
    selected_count = sum(
        bool(entry.get("selected_for_integration")) for entry in products.values()
    )
    if selected_count != int(catalog.get("selected_product_count", -1)):
        raise ValueError("Selected product count disagrees with catalogue metadata")
    if selected_count != 106:
        raise ValueError(f"Expected 106 selected source products, found {selected_count}")

    mappings: dict[str, list[tuple[str, str, dict]]] = {}
    for feature in feature_list:
        quarantine = set(feature.get("quarantined_periods", []))
        if not quarantine.issubset(ENVIRONMENT_PERIODS | {"static"}):
            raise ValueError(f"Unknown quarantine period for {feature['column']}")
        for period, source in feature.get("sources", {}).items():
            if period not in ENVIRONMENT_PERIODS | {"static"}:
                raise ValueError(
                    f"Unexpected source period {period!r} for {feature['column']}"
                )
            product = products.get(source.get("dataset_id"))
            if not product or not product.get("selected_for_integration"):
                raise ValueError(
                    f"Unselected or missing product for {feature['column']} / {period}"
                )
            if feature["variable_name"] not in product.get("variables", []):
                raise ValueError(
                    f"Catalogue variable mapping is absent from product inventory: "
                    f"{feature['column']} / {source['dataset_id']}"
                )
            expected_units = feature.get("source_units_by_period", {}).get(period)
            if expected_units is not None and str(expected_units) != str(
                source.get("source_units", "")
            ):
                raise ValueError(
                    f"Catalogue units disagree for {feature['column']} / {period}"
                )
            expected_conversion = feature.get("conversion_by_period", {}).get(period)
            if expected_conversion and expected_conversion != source.get("conversion"):
                raise ValueError(
                    f"Catalogue conversion disagrees for {feature['column']} / {period}"
                )
            mappings.setdefault(product["dataset_id"], []).append(
                (feature["column"], period, source)
            )

    if len(mappings) != selected_count:
        raise ValueError("Not every selected Bio-ORACLE product is referenced")

    product_paths = {}
    product_grid = {}
    checked_products = []
    checked_mappings = Counter()
    time_checks = Counter()
    expected_grid = manifest["spatial_grid"]
    expected_lat = np.asarray(expected_grid["latitude_axis_centres"], dtype="<f8")
    expected_lon = np.asarray(expected_grid["longitude_axis_centres"], dtype="<f8")

    for dataset_id, source_mappings in mappings.items():
        product = products[dataset_id]
        path = (ROOT / product["product_path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
            raise FileNotFoundError(f"Invalid or missing source product: {product['product_path']}")
        if path.stat().st_size != int(product["bytes"]):
            raise ValueError(f"Bio-ORACLE byte count changed: {dataset_id}")
        actual_hash = sha256(path)
        if actual_hash != product["sha256"]:
            raise ValueError(f"Bio-ORACLE source checksum changed: {dataset_id}")
        product_paths[dataset_id] = path

        with Dataset(path) as nc:
            lat_name, actual_lat = axis_variable(nc, "latitude")
            lon_name, actual_lon = axis_variable(nc, "longitude")
            if (
                actual_lat.shape != expected_lat.shape
                or not np.allclose(actual_lat, expected_lat, rtol=0, atol=1e-6)
                or actual_lon.shape != expected_lon.shape
                or not np.allclose(actual_lon, expected_lon, rtol=0, atol=1e-6)
            ):
                raise ValueError(f"NetCDF axes disagree with integration manifest: {dataset_id}")

            time_name, raw_time = time_variable(nc)
            time_coordinate = nc.variables[time_name]
            years = [
                int(value.year)
                for value in num2date(
                    raw_time,
                    time_coordinate.units,
                    getattr(time_coordinate, "calendar", "standard"),
                    only_use_cftime_datetimes=False,
                )
            ]
            lat_dim = nc.variables[lat_name].dimensions[0]
            lon_dim = nc.variables[lon_name].dimensions[0]
            time_dim = time_coordinate.dimensions[0]

            for column, period, source in source_mappings:
                variable_name = feature_entries[column]["variable_name"]
                if variable_name not in nc.variables:
                    raise ValueError(f"Missing variable {variable_name} in {dataset_id}")
                variable = nc.variables[variable_name]
                if set(variable.dimensions) != {time_dim, lat_dim, lon_dim}:
                    raise ValueError(
                        f"Unexpected raster dimensions for {dataset_id}/{variable_name}: "
                        f"{variable.dimensions}"
                    )
                index = int(source["time_index"])
                if index < 0 or index >= len(years):
                    raise ValueError(f"Invalid time index for {column} / {period}")
                variable_time_axis = variable.dimensions.index(time_dim)
                if index >= variable.shape[variable_time_axis]:
                    raise ValueError(f"Time index exceeds variable extent for {column}")
                expected_year = source.get("time_coordinate_year")
                if expected_year is not None and years[index] != int(expected_year):
                    raise ValueError(
                        f"Actual NetCDF time coordinate mismatch for {column}: "
                        f"index {index} is {years[index]}, catalogue says {expected_year}"
                    )
                actual_units = str(getattr(variable, "units", "")).strip()
                if actual_units != str(source.get("source_units", "")).strip():
                    raise ValueError(
                        f"Source units mismatch for {column}: "
                        f"NetCDF={actual_units!r}, catalogue={source.get('source_units')!r}"
                    )
                checked_mappings[period] += 1
                if expected_year is not None:
                    time_checks[period] += 1

            product_grid[dataset_id] = {
                "time_dimension": time_dim,
                "latitude_dimension": lat_dim,
                "longitude_dimension": lon_dim,
                "latitude_variable": lat_name,
                "longitude_variable": lon_name,
                "time_variable": time_name,
                "time_coordinate_years": years,
            }
        checked_products.append({
            "dataset_id": dataset_id,
            "path": product["product_path"],
            "bytes": int(product["bytes"]),
            "sha256": actual_hash,
            "variable_mappings_checked": len(source_mappings),
        })

    return feature_entries, product_paths, product_grid, {
        "selected_products": selected_count,
        "verified_products": len(checked_products),
        "source_variable_mappings_checked": sum(checked_mappings.values()),
        "mapping_checks_by_period": dict(sorted(checked_mappings.items())),
        "time_coordinate_checks_by_period": dict(sorted(time_checks.items())),
        "products": sorted(checked_products, key=lambda item: item["dataset_id"]),
    }


def load_marine_water() -> tuple[object, dict]:
    mask = gpd.read_file(MASK)
    if (
        mask.empty or mask.crs is None or mask.crs.to_epsg() != 4326
        or not mask.geometry.is_valid.all()
        or not mask.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).all()
    ):
        raise ValueError("Unverified GSHHG marine-water geometry or CRS")
    water = mask.geometry.union_all()
    if water.is_empty or not water.is_valid:
        raise ValueError("GSHHG marine-water union is empty or invalid")
    return water, {
        "features": len(mask),
        "geometry_type": water.geom_type,
        "crs": "EPSG:4326",
        "all_source_geometries_valid": True,
        "prepared_sha256": sha256(MASK),
    }


def marine_cells(
    lat: np.ndarray, lon: np.ndarray, water: object,
) -> np.ndarray:
    """Find raster centres strictly contained in the validated GSHHG water."""
    xs, ys = np.meshgrid(lon, lat)
    return np.asarray(contains_xy(water, xs.ravel(), ys.ravel()), dtype=bool)


def eligible_background_pool(
    water_cells: np.ndarray,
    core_rasters: list[np.ndarray],
    protected_cells: set[int],
) -> np.ndarray:
    """Return unique water cells with all core values, excluding presences."""
    available = np.asarray(water_cells, dtype=bool).copy()
    for raster_values in core_rasters:
        values = np.asarray(raster_values, dtype=float).ravel()
        if values.shape != available.shape:
            raise ValueError("Core environmental grid shape mismatch")
        available &= np.isfinite(values)
    if protected_cells:
        protected = np.fromiter(protected_cells, dtype=int)
        if np.any(protected < 0) or np.any(protected >= len(available)):
            raise ValueError("Protected presence cell is outside the raster grid")
        available[protected] = False
    return np.flatnonzero(available)


def draw_background_cells(
    rng: np.random.Generator,
    candidate_cells: np.ndarray,
    wanted: int,
) -> tuple[np.ndarray, int]:
    """Sample without replacement and report any candidate-pool shortfall."""
    pool = np.asarray(candidate_cells, dtype=int)
    if wanted < 0:
        raise ValueError("Requested sample count cannot be negative")
    if len(pool) != len(np.unique(pool)):
        raise ValueError("Background candidate pool contains duplicate cells")
    selected = rng.choice(pool, size=min(wanted, len(pool)), replace=False)
    return np.asarray(selected, dtype=int), wanted - len(selected)


def is_quarantined(feature: dict, period: str) -> bool:
    return period in feature.get("quarantined_periods", [])


def numeric_values(frame: pd.DataFrame, columns: list[str]) -> np.ndarray:
    return frame[columns].apply(pd.to_numeric, errors="coerce").to_numpy(
        dtype=float, na_value=np.nan
    )


def distribution_summary(values: np.ndarray) -> dict:
    """Return compact finite-value location summaries for evidence tables."""
    values = np.asarray(values, dtype=float).ravel()
    values = values[np.isfinite(values)]
    if not values.size:
        return {
            "count": 0,
            "minimum": None,
            "p05": None,
            "median": None,
            "p95": None,
            "maximum": None,
        }
    return {
        "count": int(values.size),
        "minimum": float(values.min()),
        "p05": float(np.percentile(values, 5)),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
        "maximum": float(values.max()),
    }


def species_level_eligibility(
    frame: pd.DataFrame,
    core_complete: np.ndarray,
    centre_in_water: np.ndarray,
) -> tuple[np.ndarray, dict[str, int]]:
    """Flag technically eligible species-level rows without asserting identity."""
    required = ["taxonRank", "AphiaID", "absence", "marine"]
    require_fields(frame, required)
    core_complete = np.asarray(core_complete, dtype=bool)
    centre_in_water = np.asarray(centre_in_water, dtype=bool)
    if len(core_complete) != len(frame) or len(centre_in_water) != len(frame):
        raise ValueError("Eligibility arrays do not match source observation rows")

    rank_values = (
        frame["taxonRank"].fillna("").astype(str).str.strip().str.casefold()
    )
    species_rank = rank_values.eq("species").to_numpy(dtype=bool)
    aphia_ids = pd.to_numeric(frame["AphiaID"], errors="coerce").to_numpy(
        dtype=float, na_value=np.nan
    )
    identity_ok = (
        np.isfinite(aphia_ids)
        & (aphia_ids > 0)
        & (aphia_ids == np.floor(aphia_ids))
    )
    absence_false = boolean_mask(frame["absence"], expected=False).to_numpy()
    marine_true = boolean_mask(frame["marine"], expected=True).to_numpy()

    eligible = (
        species_rank
        & identity_ok
        & absence_false
        & marine_true
        & core_complete
        & centre_in_water
    )
    counts = {
        "species_rank_rows": int(species_rank.sum()),
        "aphia_id_rows": int(identity_ok.sum()),
        "original_core_complete_rows": int(core_complete.sum()),
        "source_grid_centres_in_water": int(centre_in_water.sum()),
        "absence_false_rows": int(absence_false.sum()),
        "marine_true_rows": int(marine_true.sum()),
        "eligible_rows": int(eligible.sum()),
    }
    return eligible, counts


def decoded_netcdf_slice(
    variable: object,
    time_index: int,
    dimensions: dict,
    reader: object,
    variable_name: str,
    source_units: str,
) -> np.ndarray:
    """Read an automatically decoded slice, then apply Script 08 units once."""
    variable.set_auto_maskandscale(True)
    data = reader.read_data_slice(
        variable,
        dimensions["time_dimension"],
        int(time_index),
        dimensions["latitude_dimension"],
        dimensions["longitude_dimension"],
    )
    data = reader.harmonize_source_values(data, variable_name, source_units)
    values = np.asarray(np.ma.filled(data, np.nan), dtype=float)
    return np.where(np.isfinite(values), values, np.nan)


def compare_values(
    expected: np.ndarray,
    actual: np.ndarray,
    stats: dict | None = None,
) -> dict:
    """Compare finite measurements and null positions without filling values."""
    left = np.asarray(expected, dtype=float).ravel()
    right = np.asarray(actual, dtype=float).ravel()
    if left.shape != right.shape:
        raise ValueError("Environmental comparison arrays have different shapes")
    left_valid, right_valid = np.isfinite(left), np.isfinite(right)
    null_difference = left_valid != right_valid
    both_valid = left_valid & right_valid
    close = np.isclose(
        left[both_valid], right[both_valid], atol=VALUE_ATOL, rtol=VALUE_RTOL
    )
    differences = np.abs(left[both_valid] - right[both_valid])
    result = {
        "positions_checked": int(len(left)),
        "numerical_mismatches": int(np.count_nonzero(~close)),
        "null_fill_discrepancies": int(np.count_nonzero(null_difference)),
        "maximum_absolute_difference": (
            float(differences.max()) if differences.size else 0.0
        ),
    }
    if stats is not None:
        stats["positions_checked"] += result["positions_checked"]
        stats["numerical_mismatches"] += result["numerical_mismatches"]
        stats["null_fill_discrepancies"] += result["null_fill_discrepancies"]
        stats["maximum_absolute_difference"] = max(
            stats["maximum_absolute_difference"],
            result["maximum_absolute_difference"],
        )
    return result


def snapshot_files(paths: dict[str, Path]) -> dict:
    snapshot = {}
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required preserved file is missing: {path}")
        try:
            displayed_path = path.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            displayed_path = path.name
        snapshot[name] = {
            "path": displayed_path,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return snapshot


def geoparquet_metadata(path: Path) -> dict:
    reader = parquet.ParquetFile(path)
    metadata = reader.metadata
    schema_metadata = reader.schema_arrow.metadata or {}
    geo = json.loads(schema_metadata.get(b"geo", b"{}"))
    geometry = geo.get("columns", {}).get("geometry", {})
    compression = sorted({
        metadata.row_group(row).column(column).compression
        for row in range(metadata.num_row_groups)
        for column in range(metadata.row_group(row).num_columns)
    })
    crs_id = (geometry.get("crs") or {}).get("id", {})
    result = {
        "rows": metadata.num_rows,
        "columns": metadata.num_columns,
        "geoparquet_version": geo.get("version"),
        "geometry_encoding": geometry.get("encoding"),
        "geometry_types": geometry.get("geometry_types"),
        "crs_authority": crs_id.get("authority"),
        "crs_code": crs_id.get("code"),
        "compression": compression,
    }
    if (
        result["geoparquet_version"] != "1.1.0"
        or result["geometry_encoding"] != "WKB"
        or result["crs_authority"] != "EPSG"
        or str(result["crs_code"]) != "4326"
        or compression != ["ZSTD"]
    ):
        raise AssertionError(f"Unexpected GeoParquet metadata: {result}")
    return result


def feature_quarantines(
    feature_entries: dict[str, dict],
) -> list[dict]:
    rows = []
    for column, feature in sorted(feature_entries.items()):
        for period in feature.get("quarantined_periods", []):
            rows.append({
                "feature": column,
                "period": period,
                "reason": feature.get("quarantine_reasons_by_period", {}).get(
                    period, "Recorded in the integration catalogue"
                ),
            })
    return rows


def verify_archive_manifest(path: Path) -> dict:
    """Verify every saved archive artifact against its recorded fingerprint."""
    manifest = read_json(path)
    verified = []
    for item in manifest.get("files", []):
        archived = ROOT / item["archive_path"]
        if not archived.is_file():
            raise FileNotFoundError(f"Archived evidence is missing: {archived}")
        actual_bytes = archived.stat().st_size
        actual_hash = sha256(archived)
        if actual_bytes != item["bytes"] or actual_hash != item["sha256"]:
            raise AssertionError(f"Archived evidence fingerprint mismatch: {archived}")
        verified.append({
            "path": item["archive_path"],
            "bytes": actual_bytes,
            "sha256": actual_hash,
        })
    return {
        "manifest": path.relative_to(ROOT).as_posix(),
        "format": manifest.get("format"),
        "files_verified": len(verified),
        "files": verified,
    }


def preserve_nested_d056_design() -> dict | None:
    """Archive/verify the superseded 2,353-row nested-column D-056 output."""
    if not OUTPUT.is_file():
        return None

    metadata = parquet.ParquetFile(OUTPUT).metadata
    shape = (metadata.num_rows, metadata.num_columns)
    if shape == (2353, 527) and not NESTED_ARCHIVE_MANIFEST.is_file():
        import shutil

        sources = (
            OUTPUT,
            DECISION,
            NESTED_REPORT,
            NESTED_REPORT_MARKDOWN,
            NESTED_DATA_DICTIONARY,
            NESTED_EVALUATION_PLAN,
        )
        NESTED_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        entries = []
        for source_path in sources:
            if not source_path.is_file():
                raise FileNotFoundError(
                    f"Required superseded D-056 artifact is missing: {source_path}"
                )
            archive_name = (
                source_path.name + ".archive"
                if source_path.suffix == ".md"
                else source_path.name
            )
            destination = NESTED_ARCHIVE_DIR / archive_name
            source_hash = sha256(source_path)
            if destination.is_file():
                if sha256(destination) != source_hash:
                    raise ValueError(f"Nested D-056 archive conflict: {destination}")
            else:
                shutil.copy2(source_path, destination)
            if sha256(destination) != source_hash:
                raise AssertionError(f"Nested D-056 archive mismatch: {destination}")
            entries.append({
                "original_path": source_path.relative_to(ROOT).as_posix(),
                "archive_path": destination.relative_to(ROOT).as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            })
        nested_manifest = {
            "format": "oceavera-d056-nested-paired-archive-v1",
            "purpose": (
                "Byte-preserving archive of the superseded nested-column "
                "D-056 artifact set"
            ),
            "files": entries,
        }
        NESTED_ARCHIVE_MANIFEST.write_text(
            json.dumps(nested_manifest, indent=2) + "\n",
            encoding="utf-8",
        )

    if NESTED_ARCHIVE_MANIFEST.is_file():
        return verify_archive_manifest(NESTED_ARCHIVE_MANIFEST)
    return None


def preserve_d055_design(previous_shape: tuple[int, int] | None) -> dict:
    """Archive the earlier 338-row D-055 experiment and verify its evidence."""
    if previous_shape == (338, 397):
        import shutil

        sources = (
            OUTPUT,
            HISTORICAL_REPORT,
            HISTORICAL_REPORT_MARKDOWN,
            HISTORICAL_EVALUATION_PLAN,
        )
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        entries = []
        for source_path in sources:
            if not source_path.is_file():
                raise FileNotFoundError(
                    f"Required D-055 artifact is missing: {source_path}"
                )
            archive_name = (
                source_path.name + ".archive"
                if source_path.suffix == ".md"
                else source_path.name
            )
            destination = ARCHIVE_DIR / archive_name
            source_hash = sha256(source_path)
            if destination.is_file():
                if sha256(destination) != source_hash:
                    raise ValueError(f"D-055 archive conflict: {destination}")
            else:
                shutil.copy2(source_path, destination)
            if sha256(destination) != source_hash:
                raise AssertionError(f"D-055 archive mismatch: {destination}")
            entries.append({
                "original_path": source_path.relative_to(ROOT).as_posix(),
                "original_path_state": (
                    "replaced after archival by the full-population D-056 output"
                    if source_path == OUTPUT
                    else "original historical document remains unchanged"
                ),
                "archive_path": destination.relative_to(ROOT).as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            })
        ARCHIVE_MANIFEST.write_text(
            json.dumps({
                "format": "oceavera-presence-background-archive-v1",
                "purpose": "Byte-preserving archive of superseded D-055 evidence",
                "files": entries,
            }, indent=2) + "\n",
            encoding="utf-8",
        )

    if not ARCHIVE_MANIFEST.is_file():
        raise FileNotFoundError(
            "The historical D-055 evidence has not been archived"
        )
    return verify_archive_manifest(ARCHIVE_MANIFEST)


def main() -> None:
    """Create a full-population, long-format presence/background dataset.

    Preserve N original observations (label 1), then append N sampled marine
    environmental backgrounds (label 0). Ineligible species-level records
    remain present, with an explicit eligibility flag.
    """
    import shutil
    from collections import Counter

    required = (OBSERVATIONS, MASK, MASK_PROVENANCE, MANIFEST, CATALOG)
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    if OUTPUT.resolve() in {
        path.resolve() for path in INTEGRATED_DATASETS.values()
    }:
        raise ValueError("Cannot overwrite a frozen integration dataset")

    preserved_before = snapshot_files(INTEGRATED_DATASETS)
    previous_shape = None
    if OUTPUT.is_file():
        previous_metadata = parquet.ParquetFile(OUTPUT).metadata
        previous_shape = (
            previous_metadata.num_rows,
            previous_metadata.num_columns,
        )
        if previous_shape not in {(338, 397), (2353, 527), (4706, 527)}:
            raise ValueError(
                "Refusing to replace an unrecognised candidate dataset: "
                f"{previous_shape}"
            )
    d055_archive_evidence = preserve_d055_design(previous_shape)
    nested_archive_evidence = preserve_nested_d056_design()
    source = gpd.read_parquet(OBSERVATIONS)

    if (
        source.empty
        or source.crs is None
        or source.crs.to_epsg() != 4326
    ):
        raise ValueError("Invalid Policy B source or CRS")

    if source.shape != (2353, 519):
        raise ValueError(
            "Expected the verified Policy B source shape 2,353 × 519; "
            f"found {source.shape}"
        )

    if (
        not source.geometry.geom_type.eq("Point").all()
        or not source.geometry.is_valid.all()
    ):
        raise ValueError("Invalid source Point geometries")

    if not source["integration_source_row"].is_unique:
        raise ValueError("Duplicate source-row identifiers")

    if not boolean_mask(source["absence"], expected=False).all():
        raise ValueError("Source includes explicit absences or unknown status")

    if not boolean_mask(source["marine"], expected=True).all():
        raise ValueError("Source includes records not identified as marine")

    if not source["analysis_period"].isin(PERIODS).all():
        raise ValueError("Unsupported environmental period")

    manifest = read_json(MANIFEST)
    catalog = read_json(CATALOG)
    provenance = read_json(MASK_PROVENANCE)

    if (
        provenance.get("status") != "validated"
        or provenance.get("prepared_sha256") != sha256(MASK)
    ):
        raise ValueError("GSHHG provenance mismatch")

    full_path = ROOT / manifest["output"]["path"]

    if sha256(full_path) != manifest["output"]["sha256"]:
        raise ValueError("Full integrated dataset checksum mismatch")

    lat, lon, _, _ = cell_centres(manifest)
    source_grid_evidence = verify_observation_grid(source, lat, lon)

    water, water_evidence = load_marine_water()
    marine_grid = marine_cells(lat, lon, water)

    point_water = np.asarray(
        contains_xy(
            water,
            source.geometry.x.to_numpy(float),
            source.geometry.y.to_numpy(float),
        ),
        dtype=bool,
    )

    if not point_water.all():
        raise ValueError("An original observation lies outside GSHHG water")

    (
        feature_entries,
        product_paths,
        product_grids,
        source_evidence,
    ) = verify_catalogue_sources(manifest, catalog)

    environmental = sorted(feature_entries)

    if len(environmental) != 382:
        raise ValueError("Expected 382 environmental features")

    if not set(CORE).issubset(environmental):
        raise ValueError("Required core environmental features missing")

    decoder = integration_utilities()
    width = len(lon)

    @lru_cache(maxsize=32)
    def raster(period: str, feature: str) -> np.ndarray:
        """Extract the correct validated NetCDF time slice."""
        definition = feature_entries[feature]

        selected_period = (
            period
            if period in definition.get("sources", {})
            else "static"
        )

        mapping = definition.get("sources", {}).get(selected_period)

        if (
            mapping is None
            or is_quarantined(definition, period)
            or is_quarantined(definition, selected_period)
        ):
            return np.full(
                (len(lat), len(lon)),
                np.nan,
                dtype=float,
            )

        product_id = mapping["dataset_id"]

        with Dataset(product_paths[product_id]) as nc:
            values = decoded_netcdf_slice(
                nc.variables[definition["variable_name"]],
                int(mapping["time_index"]),
                product_grids[product_id],
                decoder,
                definition["variable_name"],
                mapping["source_units"],
            )

        if values.shape != (len(lat), len(lon)):
            raise ValueError(
                f"Raster shape mismatch: {feature}/{period}"
            )

        return values

    # ---------------------------------------------------------------
    # 1. Preserve ALL original Policy B observations.
    # ---------------------------------------------------------------

    n = len(source)
    original_columns = list(source.columns)
    new_columns = list(OUTPUT_COLUMNS)
    collisions = set(original_columns).intersection(new_columns)
    if collisions:
        raise ValueError(
            f"Source already contains reserved output fields: {sorted(collisions)}"
        )

    source_cells = pd.to_numeric(
        source["grid_cell_id"],
        errors="raise",
    ).to_numpy(dtype=int)

    source_ids = pd.to_numeric(
        source["integration_source_row"],
        errors="raise",
    ).to_numpy(dtype=int)

    periods = source["analysis_period"].astype(str).to_numpy()

    if (
        np.any(source_cells < 0)
        or np.any(source_cells >= len(lat) * width)
    ):
        raise ValueError("Original grid identifiers are invalid")

    # Protect EVERY occupied Policy B cell, regardless of species,
    # taxonomic rank, data coverage, or observation period.
    occupied_cells = set(map(int, source_cells))

    # ---------------------------------------------------------------
    # 2. Sample one background per original observation.
    # ---------------------------------------------------------------

    rng = np.random.default_rng(SEED)
    selected_background = np.full(n, -1, dtype=np.int64)
    used_background_cells = set()
    sampling_report = []

    for period_label, environment_period in PERIODS.items():
        positions = np.flatnonzero(periods == period_label)

        if len(positions) == 0:
            continue

        positions = positions[
            np.argsort(source_ids[positions], kind="stable")
        ]

        core_rasters = [
            raster(environment_period, feature)
            for feature in CORE
        ]

        pool = eligible_background_pool(
            marine_grid,
            core_rasters,
            occupied_cells | used_background_cells,
        )

        if len(pool) < len(positions):
            raise ValueError(
                f"Insufficient marine background cells for "
                f"{period_label}: {len(pool)} available, "
                f"{len(positions)} required"
            )

        selected, shortfall = draw_background_cells(
            rng,
            pool,
            wanted=len(positions),
        )
        if shortfall:
            raise ValueError(
                f"Insufficient marine background cells for "
                f"{period_label}: {len(pool)} available, "
                f"{len(positions)} required"
            )

        selected_background[positions] = selected

        used_background_cells.update(
            map(int, selected)
        )

        sampling_report.append({
            "analysis_period": period_label,
            "environment_period": environment_period,
            "original_observations": int(len(positions)),
            "background_samples": int(len(selected)),
            "candidate_pool": int(len(pool)),
        })

    if np.any(selected_background < 0):
        raise AssertionError("Some observations have no background sample")

    if len(np.unique(selected_background)) != n:
        raise AssertionError("Background cells are not globally unique")

    if occupied_cells.intersection(
        map(int, selected_background)
    ):
        raise AssertionError(
            "A sampled background overlaps a recorded Policy B cell"
        )

    if not marine_grid[selected_background].all():
        raise AssertionError("A background centre is outside marine water")

    # ---------------------------------------------------------------
    # 3. Calculate species-level eligibility without removing records.
    # ---------------------------------------------------------------

    aphia = pd.to_numeric(
        source["AphiaID"],
        errors="coerce",
    )

    valid_aphia = (
        aphia.notna()
        & np.isfinite(aphia.astype(float))
        & aphia.gt(0)
        & aphia.eq(aphia.round())
    )

    species_rank = (
        source["taxonRank"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq("species")
    )

    core_complete = np.isfinite(
        numeric_values(source, list(CORE))
    ).all(axis=1)

    marine_cell_valid = marine_grid[source_cells]

    eligible, eligibility_checks = species_level_eligibility(
        source,
        core_complete,
        marine_cell_valid,
    )

    reason_components = []
    for index in range(n):
        reasons = []
        if not valid_aphia.iloc[index]:
            reasons.append("missing_or_invalid_aphiaid")
        if not species_rank.iloc[index]:
            reasons.append("unverified_species_rank")
        if not marine_cell_valid[index]:
            reasons.append("source_cell_centre_not_marine")
        if not core_complete[index]:
            reasons.append("missing_core_environment")
        reason_components.append(
            ";".join(reasons)
            if reasons
            else "preliminary_species_core_eligible"
        )
    eligibility_reason = np.asarray(reason_components, dtype=object)

    target_taxon_keys = [
        (
            f"AphiaID:{int(value)}"
            if (
                pd.notna(value)
                and np.isfinite(value)
                and value > 0
                and value == round(value)
            )
            else f"unresolved_source_row:{int(row_id)}"
        )
        for value, row_id in zip(aphia, source_ids)
    ]

    # ---------------------------------------------------------------
    # 4. Create original positive examples, without changing source data.
    # ---------------------------------------------------------------

    positive_metadata = pd.DataFrame({
        "presence_background_label": pd.Series(
            np.ones(n, dtype=np.int8), index=source.index
        ),
        "sample_type": pd.Series(
            ["observed_presence"] * n, index=source.index, dtype="string"
        ),
        "target_taxon_key": pd.Series(
            target_taxon_keys, index=source.index, dtype="string"
        ),
        "paired_presence_source_row": pd.Series(
            source_ids, index=source.index, dtype="int64"
        ),
        "eligible_species_level_ml": pd.Series(
            eligible, index=source.index, dtype="bool"
        ),
        "ml_eligibility_reason": pd.Series(
            eligibility_reason, index=source.index, dtype="string"
        ),
        "background_sampling_method": pd.Series(
            pd.array([pd.NA] * n, dtype="string"), index=source.index
        ),
        "sample_id": pd.Series(
            [f"presence:{source_id}" for source_id in source_ids],
            index=source.index,
            dtype="string",
        ),
    })
    positives = gpd.GeoDataFrame(
        pd.concat([source.copy(deep=True), positive_metadata], axis=1),
        geometry="geometry",
        crs=source.crs,
    )

    # ---------------------------------------------------------------
    # 5. Create separate background examples.
    # ---------------------------------------------------------------

    # Do not copy source observation records into synthetic rows.
    # Source IDs, occurrence IDs, event dates, and observation metadata
    # must remain null for backgrounds.

    backgrounds = source.iloc[:0].copy().reindex(source.index).copy()

    # The following fields describe the TARGET TAXON being modelled.
    # They are not a claim that the taxon was observed at the background.
    taxon_fields = [
        "AphiaID",
        "aphiaID",
        "taxonID",
        "scientificName",
        "scientificNameID",
        "species",
        "speciesid",
        "taxonRank",
    ]

    for field in taxon_fields:
        if field in source.columns:
            backgrounds[field] = source[field].to_numpy(copy=True)

    for field in ("analysis_period", "environment_period"):
        backgrounds[field] = source[field].to_numpy(copy=True)

    backgrounds["raster_row"] = selected_background // width
    backgrounds["raster_column"] = selected_background % width
    backgrounds["raster_cell_id"] = selected_background
    backgrounds["grid_cell_id"] = selected_background

    if "raster_cell_center_latitude" in backgrounds.columns:
        backgrounds["raster_cell_center_latitude"] = (
            lat[selected_background // width]
        )

    if "raster_cell_center_longitude" in backgrounds.columns:
        backgrounds["raster_cell_center_longitude"] = (
            lon[selected_background % width]
        )

    if "raster_cell_distance_km" in backgrounds.columns:
        backgrounds["raster_cell_distance_km"] = 0.0

    if "raster_match_status" in backgrounds.columns:
        backgrounds["raster_match_status"] = "matched"

    if "marine_point_verified" in backgrounds.columns:
        backgrounds["marine_point_verified"] = True

    if "marine_position_confidence" in backgrounds.columns:
        backgrounds["marine_position_confidence"] = (
            "not_applicable_synthetic_grid_centre"
        )

    if "marine_uncertainty_verified" in backgrounds.columns:
        backgrounds["marine_uncertainty_verified"] = pd.NA

    if "marine_filter_reason" in backgrounds.columns:
        backgrounds["marine_filter_reason"] = (
            "sampled_GSHHG_water_grid_centre"
        )

    if "expected_environment_feature_count" in backgrounds.columns:
        backgrounds["expected_environment_feature_count"] = (
            source["expected_environment_feature_count"].to_numpy()
        )

    # ---------------------------------------------------------------
    # 6. Extract ALL 382 environmental values for backgrounds.
    # ---------------------------------------------------------------

    background_features = np.full(
        (n, len(environmental)),
        np.nan,
        dtype=float,
    )

    for period_label, environment_period in PERIODS.items():
        positions = np.flatnonzero(periods == period_label)

        if len(positions) == 0:
            continue

        sampled_cells = selected_background[positions]

        for j, feature in enumerate(environmental):
            background_features[positions, j] = (
                raster(environment_period, feature)
                .ravel()[sampled_cells]
            )

            if (
                is_quarantined(feature_entries[feature], environment_period)
                and np.isfinite(
                    background_features[positions, j]
                ).any()
            ):
                raise AssertionError(
                    f"Quarantined feature populated: "
                    f"{feature}/{environment_period}"
                )

    for j, feature in enumerate(environmental):
        backgrounds[feature] = background_features[:, j]

    core_indexes = [
        environmental.index(feature)
        for feature in CORE
    ]

    if not np.isfinite(
        background_features[:, core_indexes]
    ).all():
        raise AssertionError("Missing core predictor in background data")

    if "present_environment_feature_count" in backgrounds.columns:
        backgrounds["present_environment_feature_count"] = (
            np.isfinite(background_features).sum(axis=1)
        )

    if "environmental_coverage_status" in backgrounds.columns:
        counts = np.isfinite(
            background_features
        ).sum(axis=1)

        if "expected_environment_feature_count" in backgrounds.columns:
            expected = pd.to_numeric(
                backgrounds["expected_environment_feature_count"],
                errors="coerce",
            ).to_numpy(float)

            if not np.isfinite(expected).all():
                raise ValueError("Unknown environmental feature expectation")

            backgrounds["environmental_coverage_status"] = np.where(
                counts == 0,
                "no_valid_source_values_at_cell",
                np.where(
                    counts >= expected,
                    "complete_environmental_values",
                    "partial_environmental_values",
                ),
            )

    background_points = [
        Point(
            float(lon[cell % width]),
            float(lat[cell // width]),
        )
        for cell in selected_background
    ]

    backgrounds["geometry"] = gpd.GeoSeries(
        background_points,
        index=source.index,
        crs="EPSG:4326",
    )

    backgrounds = gpd.GeoDataFrame(
        backgrounds,
        geometry="geometry",
        crs="EPSG:4326",
    )

    background_metadata = pd.DataFrame({
        "presence_background_label": pd.Series(
            np.zeros(n, dtype=np.int8), index=source.index
        ),
        "sample_type": pd.Series(
            ["sampled_background"] * n,
            index=source.index,
            dtype="string",
        ),
        "target_taxon_key": pd.Series(
            target_taxon_keys, index=source.index, dtype="string"
        ),
        "paired_presence_source_row": pd.Series(
            source_ids, index=source.index, dtype="int64"
        ),
        "eligible_species_level_ml": pd.Series(
            eligible, index=source.index, dtype="bool"
        ),
        "ml_eligibility_reason": pd.Series(
            eligibility_reason, index=source.index, dtype="string"
        ),
        "background_sampling_method": pd.Series(
            ["uniform_unique_GSHHG_water_core_complete"] * n,
            index=source.index,
            dtype="string",
        ),
        "sample_id": pd.Series(
            [f"background:{source_id}" for source_id in source_ids],
            index=source.index,
            dtype="string",
        ),
    })
    backgrounds = gpd.GeoDataFrame(
        pd.concat([backgrounds, background_metadata], axis=1),
        geometry="geometry",
        crs="EPSG:4326",
    )

    # ---------------------------------------------------------------
    # 7. Combine the two classes into ONE long-format dataset.
    # ---------------------------------------------------------------

    all_columns = list(positives.columns)

    output = gpd.GeoDataFrame(
        pd.concat(
            [
                positives,
                backgrounds[all_columns],
            ],
            ignore_index=True,
        ),
        geometry="geometry",
        crs="EPSG:4326",
    )

    nullable_source_fields = {}
    for field, nullable_dtype in (
        ("integration_source_row", "Int64"),
        ("marine_uncertainty_verified", "boolean"),
    ):
        if field in output.columns:
            output[field] = output[field].astype(nullable_dtype)
            nullable_source_fields[field] = nullable_dtype

    expected_shape = (
        2 * n,
        len(original_columns) + 8,
    )

    if output.shape != expected_shape:
        raise AssertionError(
            f"Unexpected output shape: {output.shape}"
        )

    if list(output.columns[:len(original_columns)]) != original_columns:
        raise AssertionError("The original source-field order changed")
    if list(output.columns[len(original_columns):]) != new_columns:
        raise AssertionError("Unexpected long-format output fields")

    if not output["sample_id"].is_unique:
        raise AssertionError("Duplicate sample identifiers")

    if (
        not output.iloc[:n]["presence_background_label"].eq(1).all()
        or not output.iloc[n:]["presence_background_label"].eq(0).all()
    ):
        raise AssertionError("The long-format class labels or row order changed")
    if (
        not output.iloc[:n]["sample_type"].eq("observed_presence").all()
        or not output.iloc[n:]["sample_type"].eq("sampled_background").all()
    ):
        raise AssertionError("The long-format sample types are inconsistent")

    if output.iloc[n:]["integration_source_row"].notna().any():
        raise AssertionError("Background received a source observation ID")

    forbidden_background_fields = {
        "integration_source_row",
        "occurrenceid",
        "eventid",
        "datasetid",
        "eventdate",
        "eventdateend",
        "eventtime",
        "year",
        "month",
        "day",
        "dateidentified",
        "recordedby",
        "absence",
    }
    forbidden_background_fields.update(
        name.casefold()
        for name in original_columns
        if name.casefold().endswith("date")
        or name.casefold().endswith("_date")
        or name.casefold().endswith("_datetime")
    )
    fabricated_fields = [
        name for name in original_columns
        if name.casefold() in forbidden_background_fields
    ]
    non_null_fabricated = [
        name for name in fabricated_fields
        if output.iloc[n:][name].notna().any()
    ]
    if non_null_fabricated:
        raise AssertionError(
            "Background rows contain copied observation identifiers/dates: "
            f"{non_null_fabricated}"
        )

    if not np.array_equal(
        output.iloc[:n]["paired_presence_source_row"].to_numpy(dtype=np.int64),
        source_ids,
    ) or not np.array_equal(
        output.iloc[n:]["paired_presence_source_row"].to_numpy(dtype=np.int64),
        source_ids,
    ):
        raise AssertionError("Presence/background source-row links changed")

    # Confirm the first N rows still reproduce the original dataset.
    pd.testing.assert_frame_equal(
        output.iloc[:n][original_columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
        check_exact=True,
    )

    if not output.iloc[:n].geometry.geom_equals(
        source.geometry
    ).all():
        raise AssertionError("Original Point geometry changed")

    if (
        output.iloc[n:]["grid_cell_id"]
        .nunique()
        != n
    ):
        raise AssertionError("Duplicate background grid cells")

    positive_cell_overlap = occupied_cells.intersection(
        map(int, output.iloc[n:]["grid_cell_id"].to_numpy(dtype=np.int64))
    )
    if positive_cell_overlap:
        raise AssertionError("A background cell overlaps an occupied source cell")

    expected_background_rows = selected_background // width
    expected_background_columns = selected_background % width
    for field, expected in (
        ("raster_row", expected_background_rows),
        ("raster_column", expected_background_columns),
        ("raster_cell_id", selected_background),
        ("grid_cell_id", selected_background),
    ):
        if field in output.columns and not np.array_equal(
            pd.to_numeric(output.iloc[n:][field], errors="raise").to_numpy(
                dtype=np.int64
            ),
            expected.astype(np.int64),
        ):
            raise AssertionError(f"Background raster index mismatch: {field}")

    background_coordinates = output.iloc[n:].geometry
    if (
        background_coordinates.isna().any()
        or not background_coordinates.is_valid.all()
        or not background_coordinates.geom_type.eq("Point").all()
    ):
        raise AssertionError("Background geometries must be valid Points")

    # ---------------------------------------------------------------
    # 9. Publish and independently validate.
    # ---------------------------------------------------------------

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    pending = OUTPUT.with_name(
        ".presence_background_candidates.pending.parquet"
    )

    try:
        output.to_parquet(
            pending,
            index=False,
            compression="zstd",
            geometry_encoding="WKB",
            schema_version="1.1.0",
        )

        reread = gpd.read_parquet(pending)
        geoparquet_info = geoparquet_metadata(pending)

        if (
            reread.shape != output.shape
            or list(reread.columns) != list(output.columns)
        ):
            raise AssertionError("Read-back schema or dimensions mismatch")

        pd.testing.assert_frame_equal(
            reread.iloc[:n][original_columns].reset_index(drop=True),
            source.reset_index(drop=True),
            check_dtype=False,
            check_exact=True,
        )

        if not reread.geometry.geom_equals(
            output.geometry
        ).all():
            raise AssertionError("Read-back Point geometry mismatch")

        if not np.array_equal(
            reread["presence_background_label"].to_numpy(dtype=int),
            output["presence_background_label"].to_numpy(dtype=int),
        ):
            raise AssertionError("Read-back target labels mismatch")

        # Check every background feature and legitimate null against the
        # appropriate source NetCDF slice and actual catalogue time index.
        read_background = reread.iloc[n:]
        environmental_verification = {
            "positions_checked": 0,
            "numerical_mismatches": 0,
            "null_fill_discrepancies": 0,
            "maximum_absolute_difference": 0.0,
        }
        environmental_verification_by_period = []

        for period_label, environment_period in PERIODS.items():
            positions = np.flatnonzero(periods == period_label)

            if len(positions) == 0:
                continue

            sampled_cells = selected_background[positions]
            period_verification = {
                "analysis_period": period_label,
                "environment_period": environment_period,
                "positions_checked": 0,
                "numerical_mismatches": 0,
                "null_fill_discrepancies": 0,
                "maximum_absolute_difference": 0.0,
            }

            for feature in environmental:
                actual = pd.to_numeric(
                    read_background.iloc[positions][feature],
                    errors="coerce",
                ).to_numpy(float)

                expected = raster(
                    environment_period, feature
                ).ravel()[sampled_cells]
                compare_values(
                    expected,
                    actual,
                    period_verification,
                )

                if (
                    period_verification["numerical_mismatches"]
                    or period_verification["null_fill_discrepancies"]
                ):
                    raise AssertionError(
                        f"Background feature mismatch: "
                        f"{feature}/{period_label}"
                    )

            for key in (
                "positions_checked",
                "numerical_mismatches",
                "null_fill_discrepancies",
            ):
                environmental_verification[key] += period_verification[key]
            environmental_verification["maximum_absolute_difference"] = max(
                environmental_verification["maximum_absolute_difference"],
                period_verification["maximum_absolute_difference"],
            )
            environmental_verification_by_period.append(period_verification)

        if environmental_verification["positions_checked"] != n * len(environmental):
            raise AssertionError("Not all background environmental positions were checked")

        if (
            environmental_verification["numerical_mismatches"]
            or environmental_verification["null_fill_discrepancies"]
        ):
            raise AssertionError("NetCDF-to-GeoParquet values differ")

        read_background_cells = pd.to_numeric(
            read_background["grid_cell_id"], errors="raise"
        ).to_numpy(dtype=np.int64)
        if not np.array_equal(read_background_cells, selected_background):
            raise AssertionError("Read-back background grid IDs changed")
        if not marine_grid[read_background_cells].all():
            raise AssertionError("Read-back background cell is not marine")
        if not np.asarray(
            contains_xy(
                water,
                read_background.geometry.x.to_numpy(float),
                read_background.geometry.y.to_numpy(float),
            ),
            dtype=bool,
        ).all():
            raise AssertionError("Read-back background point is outside GSHHG water")

        pending.replace(OUTPUT)

    except Exception:
        pending.unlink(missing_ok=True)
        raise

    # ---------------------------------------------------------------
    # 10. Verify source immutability and publish execution reports.
    # ---------------------------------------------------------------

    preserved_after = snapshot_files(INTEGRATED_DATASETS)

    if preserved_before != preserved_after:
        raise AssertionError("An accepted integration dataset changed")

    source_environment = numeric_values(source, environmental)
    source_environment_finite = np.isfinite(source_environment)
    background_environment_finite = np.isfinite(background_features)

    def coverage_summary(values: np.ndarray) -> dict:
        finite = np.isfinite(values)
        return {
            "rows": int(values.shape[0]),
            "feature_positions": int(values.size),
            "non_null_values": int(finite.sum()),
            "null_values": int((~finite).sum()),
            "rows_with_all_382_values": int(finite.all(axis=1).sum()),
            "rows_with_all_six_core_values": int(
                finite[:, core_indexes].all(axis=1).sum()
            ),
        }

    positive_species_mask = valid_aphia.to_numpy(bool) & species_rank.to_numpy(bool)
    duplicate_keys = pd.DataFrame({
        "AphiaID": aphia.to_numpy(dtype=float)[positive_species_mask].astype(np.int64),
        "grid_cell_id": source_cells[positive_species_mask],
        "analysis_period": periods[positive_species_mask],
    })
    duplicate_sizes = duplicate_keys.value_counts(sort=False)
    repeated_sizes = duplicate_sizes[duplicate_sizes > 1]

    duplicate_source_rows_by_cell_period = int(
        source.duplicated(
            subset=["grid_cell_id", "analysis_period"],
            keep=False,
        ).sum()
    )

    per_period_evidence = []
    for sampling_row in sampling_report:
        period_label = sampling_row["analysis_period"]
        indexes = np.flatnonzero(periods == period_label)
        positive_period_values = source_environment[indexes]
        background_period_values = background_features[indexes]
        species_period = positive_species_mask[indexes]
        per_period_evidence.append({
            **sampling_row,
            "distinct_species_rank_aphia_ids": int(
                aphia.iloc[indexes[species_period]].nunique(dropna=True)
            ),
            "positive_environment": coverage_summary(positive_period_values),
            "background_environment": coverage_summary(background_period_values),
        })

    reason_counts = Counter(
        reason
        for index, reason_string in enumerate(eligibility_reason)
        if not eligible[index]
        for reason in reason_string.split(";")
    )

    species_names = (
        source.loc[species_rank, "scientificName"]
        if "scientificName" in source.columns
        else pd.Series(dtype="string")
    )
    species_rank_aphia = aphia[positive_species_mask]
    bathymetry_catalogue_entry = next(
        row for row in catalog["features"]
        if row.get("column") == CORE[-1]
    )
    bathymetry_units = bathymetry_catalogue_entry.get("units")
    taxonomy_evidence = {
        "source_positive_rows": n,
        "valid_positive_aphiaid_rows": int(valid_aphia.sum()),
        "distinct_valid_positive_aphia_ids": int(aphia[valid_aphia].nunique()),
        "explicit_species_rank_positive_rows": int(species_rank.sum()),
        "distinct_species_rank_aphia_ids": int(species_rank_aphia.nunique()),
        "distinct_species_rank_names": int(species_names.nunique(dropna=True)),
        "unresolved_target_taxon_keys": int(sum(
            key.startswith("unresolved_source_row:")
            for key in target_taxon_keys
        )),
        "taxon_rank_row_counts": {
            ("missing" if pd.isna(key) else str(key)): int(value)
            for key, value in source["taxonRank"].value_counts(
                dropna=False
            ).items()
        },
    }

    positive_longitude = source.geometry.x.to_numpy(dtype=float)
    positive_latitude = source.geometry.y.to_numpy(dtype=float)
    background_longitude = lon[selected_background % width]
    background_latitude = lat[selected_background // width]
    bathymetry_index = environmental.index(CORE[-1])
    spatial_depth_comparison = {
        "coordinate_reference": "EPSG:4326",
        "longitude": {
            "observed_positive": distribution_summary(positive_longitude),
            "sampled_background": distribution_summary(background_longitude),
        },
        "latitude": {
            "observed_positive": distribution_summary(positive_latitude),
            "sampled_background": distribution_summary(background_latitude),
        },
        "bathymetry_feature": CORE[-1],
        "bathymetry_source_units": bathymetry_units,
        "bathymetry": {
            "observed_positive": distribution_summary(
                source_environment[:, bathymetry_index]
            ),
            "sampled_background": distribution_summary(
                background_features[:, bathymetry_index]
            ),
        },
        "interpretation": (
            "Uniform water-cell sampling and recorded OBIS locations may "
            "have different geographic and depth distributions; the summary "
            "describes this output and does not correct observation effort."
        ),
    }

    class_counts = {
        "observed_presence": int(
            output["sample_type"].eq("observed_presence").sum()
        ),
        "sampled_background": int(
            output["sample_type"].eq("sampled_background").sum()
        ),
    }

    report = {
        "format": "oceavera-all-record-presence-background-long-v1",
        "decision": "D-056",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": (
            "Full-population long-format presence/background candidate "
            "generated; scientific target and domain approval remain pending"
        ),
        "row_meaning": {
            "label_1": "An observed Policy B taxon occurrence.",
            "label_0": (
                "A newly sampled marine environmental background example; "
                "not a confirmed species absence."
            ),
            "row_order": (
                "All original positive observations first, then all sampled "
                "background rows."
            ),
            "background_taxonomy": (
                "Taxonomic fields are copied only as target-conditioning "
                "information and do not assert a background occurrence."
            ),
        },
        "source": {
            "path": OBSERVATIONS.relative_to(ROOT).as_posix(),
            "rows": n,
            "columns": len(original_columns),
            "sha256": preserved_before["grid"]["sha256"],
            "bytes": preserved_before["grid"]["bytes"],
            "distinct_occupied_grid_cells": int(len(occupied_cells)),
            "period_row_counts": {
                period: int(np.count_nonzero(periods == period))
                for period in PERIODS
            },
            "taxonomic_summary": taxonomy_evidence,
            "duplicate_species_cell_period_units": {
                "definition": (
                    "Valid AphiaID and explicit species-rank rows grouped by "
                    "AphiaID, grid cell and analysis period."
                ),
                "duplicate_combinations": int(len(repeated_sizes)),
                "rows_in_duplicate_combinations": int(repeated_sizes.sum()),
                "excess_rows_beyond_one_per_combination": int(
                    (repeated_sizes - 1).sum()
                ),
                "all_taxa_rows_repeated_in_same_cell_period": (
                    duplicate_source_rows_by_cell_period
                ),
            },
        },
        "output": {
            "path": OUTPUT.relative_to(ROOT).as_posix(),
            "rows": len(output),
            "columns": len(output.columns),
            "source_columns_preserved": len(original_columns),
            "new_columns": new_columns,
            "positive_rows": n,
            "background_rows": n,
            "class_counts": class_counts,
            "sha256": sha256(OUTPUT),
            "bytes": OUTPUT.stat().st_size,
            "geoparquet": geoparquet_info,
            "all_382_environment_feature_columns_present": all(
                feature in output.columns for feature in environmental
            ),
        },
        "species_level_eligibility": {
            **eligibility_checks,
            "ineligible_positive_rows": int((~eligible).sum()),
            "ineligible_reason_counts_nonexclusive": {
                str(key): int(value)
                for key, value in sorted(reason_counts.items())
            },
            "reason_values": sorted(set(map(str, eligibility_reason))),
            "flag_is_preliminary_only": True,
        },
        "sampling": {
            "seed": SEED,
            "method": (
                "Uniform sampling without replacement from GSHHG marine "
                "water grid centres with complete core predictors."
            ),
            "protected_cells": (
                "Every grid cell occupied by any Policy B observation, "
                "across taxa and periods."
            ),
            "protected_occupied_cells": int(len(occupied_cells)),
            "background_cells_globally_unique": (
                len(np.unique(selected_background)) == n
            ),
            "distinct_background_cells": int(
                len(np.unique(selected_background))
            ),
            "positive_background_cell_overlap": int(
                len(positive_cell_overlap)
            ),
            "gshhg_water_grid_centres": int(marine_grid.sum()),
            "backgrounds_are_confirmed_absences": False,
            "per_period": per_period_evidence,
        },
        "environmental_coverage": {
            "feature_count": len(environmental),
            "core_features": list(CORE),
            "observed_positive_rows": coverage_summary(source_environment),
            "sampled_background_rows": coverage_summary(background_features),
            "all_backgrounds_have_complete_core_values": bool(
                np.isfinite(background_features[:, core_indexes]).all()
            ),
            "quarantines": feature_quarantines(feature_entries),
            "quarantined_source_values_remain_null": True,
            "null_feature_values_are_not_imputed": True,
        },
        "source_environment_verification": {
            "method": (
                "Source NetCDF arrays were read using the validated catalogue "
                "mapping, decoded source metadata and actual time coordinate; "
                "the written background values were compared after GeoParquet "
                "read-back."
            ),
            "netcdf_products_verified": source_evidence["verified_products"],
            "source_variable_mappings_checked": source_evidence[
                "source_variable_mappings_checked"
            ],
            "background_positions_checked": environmental_verification[
                "positions_checked"
            ],
            "numerical_mismatches": environmental_verification[
                "numerical_mismatches"
            ],
            "null_fill_discrepancies": environmental_verification[
                "null_fill_discrepancies"
            ],
            "maximum_absolute_difference": environmental_verification[
                "maximum_absolute_difference"
            ],
            "by_period": environmental_verification_by_period,
        },
        "spatial_validation": {
            "source_grid_checks": source_grid_evidence,
            "gshhg_reference": water_evidence,
            "background_axis_index_discrepancies": 0,
            "background_geometry_discrepancies": 0,
            "background_centres_inside_gshhg_water": n,
            "geographic_and_depth_comparison": spatial_depth_comparison,
        },
        "row_preservation_and_safeguards": {
            "all_source_rows_preserved_once_in_order": True,
            "all_519_source_values_preserved_in_positive_rows": True,
            "original_positive_geometries_preserved": True,
            "all_source_row_ids_preserved": True,
            "background_integration_source_ids_null": True,
            "background_occurrence_and_event_date_fields_null": True,
            "background_absence_field_null": True,
            "background_taxonomy_is_conditioning_only": True,
            "incomplete_and_non_species_rows_retained": True,
            "random_seed_reproducibility_setting": SEED,
            "nullable_source_fields_for_synthetic_rows": nullable_source_fields,
        },
        "source_preservation": {
            "all_five_integration_datasets_byte_identical": (
                preserved_before == preserved_after
            ),
            "before": preserved_before,
            "after": preserved_after,
        },
        "historical_archives": {
            "d055_three_species": d055_archive_evidence,
            "superseded_d056_nested_columns": nested_archive_evidence,
        },
        "limitations": [
            "Background label 0 does not represent confirmed species absence.",
            "Non-species and incomplete-taxon rows are retained but are not "
            "eligible species-level records.",
            "The 1:1 sample ratio does not represent natural species prevalence.",
            "Broad uniform marine sampling may differ geographically and by "
            "depth from recorded OBIS locations, and may exaggerate apparent "
            "classification performance.",
            "Repeated observed species/cell/period rows are reported and must "
            "not be treated as independent samples.",
            "2020-2026 backgrounds use the SSP245 2020 environmental slice.",
            "Future spatial evaluation must group shared grid cells across "
            "species and periods to prevent leakage.",
            "This candidate dataset is not a deduplicated or spatially "
            "validated training table; feature selection, imputation, model "
            "training and evaluation were not performed.",
        ],
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    REPORT.write_text(
        json.dumps(report, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    period_rows = [
        "| Period | Slice | Positives | Backgrounds | Candidate pool | Positive non-null env. values | Background non-null env. values |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in per_period_evidence:
        period_rows.append(
            f"| {row['analysis_period']} | {row['environment_period']} | "
            f"{row['original_observations']:,} | {row['background_samples']:,} | "
            f"{row['candidate_pool']:,} | "
            f"{row['positive_environment']['non_null_values']:,} | "
            f"{row['background_environment']['non_null_values']:,} |"
        )

    report_markdown = [
        "# OCEAVERA — Full-population long-format presence/background construction",
        "",
        f"**Status:** {report['status']}",
        "",
        "The dataset contains every Policy B observation once as a positive row, followed by one separately sampled marine background row per source observation. Label 0 is a sampled background example, not a confirmed absence. This is a candidate dataset, not an approved final target or validated training set.",
        "",
        "## Dataset and labels",
        "",
        "| Measure | Result |",
        "| --- | ---: |",
        f"| Output shape | {len(output):,} × {len(output.columns)} |",
        f"| Source positives preserved | {n:,} |",
        f"| Sampled background rows | {n:,} |",
        f"| Original source fields | {len(original_columns):,} |",
        f"| Environmental feature columns | {len(environmental):,} |",
        f"| Distinct occupied / background cells | {len(occupied_cells):,} / {len(np.unique(selected_background)):,} |",
        f"| Positive/background cell overlap | {len(positive_cell_overlap):,} |",
        f"| Preliminary species-level eligible positive rows | {int(eligible.sum()):,} |",
        f"| File size / SHA-256 | {OUTPUT.stat().st_size:,} bytes / `{sha256(OUTPUT)}` |",
        f"| GeoParquet | {geoparquet_info['geoparquet_version']}, EPSG:{geoparquet_info['crs_code']}, WKB Point, {', '.join(geoparquet_info['compression'])} |",
        "",
        "## Period, pool and environmental coverage",
        "",
        *period_rows,
        "",
        f"Across the 382 environmental features, positive rows contain {coverage_summary(source_environment)['non_null_values']:,} non-null values and background rows contain {coverage_summary(background_features)['non_null_values']:,}. All {n:,} sampled backgrounds have all six core predictors. Source quarantines and missing environmental values remain null.",
        "",
        "## Taxonomic eligibility and duplicate observations",
        "",
        f"Of {n:,} preserved positives, {taxonomy_evidence['valid_positive_aphiaid_rows']:,} have a valid positive AphiaID, {taxonomy_evidence['explicit_species_rank_positive_rows']:,} have explicit species rank, and {taxonomy_evidence['distinct_species_rank_aphia_ids']:,} distinct valid AphiaIDs occur at species rank. The preliminary technical screen flags {int(eligible.sum()):,} as eligible and retains {int((~eligible).sum()):,} as ineligible. Ineligibility reason counts are non-exclusive: {json.dumps(dict(reason_counts), sort_keys=True)}.",
        f"There are {len(repeated_sizes):,} repeated valid species/AphiaID × grid-cell × period combinations involving {int(repeated_sizes.sum()):,} rows ({int((repeated_sizes - 1).sum()):,} excess rows beyond one per combination). These rows remain present and are not independent model samples.",
        "",
        "## Sampling and source verification",
        "",
        f"Sampling used seed `{SEED}`. All {len(occupied_cells):,} occupied Policy B cells were excluded across taxa and periods; background cells are unique globally. The GSHHG-water cell-centre pools require complete values for all six core predictors. {source_evidence['verified_products']} NetCDF products and {source_evidence['source_variable_mappings_checked']:,} catalogue mappings were checked. The {environmental_verification['positions_checked']:,} background environmental positions were read back and compared to the period-matched source arrays: {environmental_verification['numerical_mismatches']:,} numerical mismatches, {environmental_verification['null_fill_discrepancies']:,} null/fill discrepancies, maximum absolute difference {environmental_verification['maximum_absolute_difference']:.12g}.",
        "",
        "The geographic and bathymetric summaries in the JSON report compare original occurrence locations with sampled water-cell centres. Uniform sampling across the broad marine mask may produce different location and depth distributions from the occurrence process and may make classification look easier than it is.",
        "",
        "## Preservation and interpretation limits",
        "",
        "All 519 source fields and the original Point geometries are verified on the first 2,353 rows. Background rows have no copied occurrence IDs, source-row IDs or event dates; `paired_presence_source_row` links each background to its conditioning source row. The five accepted integration GeoParquets are checked before and after by SHA-256.",
        "",
        "The 1:1 ratio does not represent real-world prevalence. Background label 0 is not absence. The 2020–2026 rows use the SSP245 2020 slice. Future modelling requires group review, taxonomic/target decisions and spatially separated validation that groups shared cells across taxa and periods. No feature selection, imputation, training table, model, or evaluation was generated.",
        "",
        f"D-055 archive evidence: [manifest](2026-10-16-presence-background-archive-manifest.json). The superseded nested-column D-056 artifact is preserved under `{NESTED_ARCHIVE_DIR.relative_to(ROOT).as_posix()}` and listed in [its archive manifest](2026-10-16-nested-paired-background-archive-manifest.json).",
        f"See [D-056](2026-10-16-decision-paired-presence-background.md), the [data dictionary](2026-10-16-full-population-presence-background-data-dictionary.md) and [provisional evaluation plan](2026-10-16-full-population-presence-background-evaluation-plan.md).",
        "",
    ]
    REPORT_MARKDOWN.write_text("\n".join(report_markdown), encoding="utf-8")

    print(
        f"[Script 10] Generated {len(output):,} rows × "
        f"{len(output.columns)} columns"
    )
    print(f"  Original presences: {n:,}")
    print(f"  Sampled backgrounds: {n:,}")
    print(
        "  Preliminary species-level eligible positive records:",
        int(np.count_nonzero(eligible)),
    )
    print(
        "  Background environmental positions verified:",
        environmental_verification["positions_checked"],
    )
    print(
        "  Positive/background grid-cell overlaps:",
        len(positive_cell_overlap),
    )
    print(f"  Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
