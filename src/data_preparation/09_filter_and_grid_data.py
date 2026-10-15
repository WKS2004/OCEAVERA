"""Build temporal and Policy B marine water-centre candidate datasets.

Reads the completed full integration GeoParquet. Positional uncertainty is
retained as a diagnostic and does not remove otherwise eligible water-centre
records. This is a candidate dataset, not a claim of precise marine habitat.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as parquet
from pyproj import Geod
from shapely.geometry import Point, Polygon, box
from shapely.prepared import prep

class FilterError(RuntimeError):
    """Raised when filtering metadata or output validation is inconsistent."""


def cell_edges(axis: np.ndarray) -> np.ndarray:
    """Reconstruct cell edges from persisted monotonic coordinate centres."""
    values = np.asarray(axis, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise FilterError("Persisted raster axes must contain at least two finite centres.")
    differences = np.diff(values)
    if not (np.all(differences > 0) or np.all(differences < 0)):
        raise FilterError("Persisted raster axes must be strictly monotonic.")
    edges = np.empty(len(values) + 1, dtype=float)
    edges[1:-1] = (values[:-1] + values[1:]) / 2
    edges[0] = values[0] - differences[0] / 2
    edges[-1] = values[-1] + differences[-1] / 2
    return edges


def validate_geoparquet(path: Path) -> dict[str, Any]:
    metadata = parquet.ParquetFile(path).metadata
    schema_metadata = parquet.ParquetFile(path).schema_arrow.metadata or {}
    geo = json.loads(schema_metadata.get(b"geo", b"{}"))
    compression = sorted({
        metadata.row_group(group).column(column).compression
        for group in range(metadata.num_row_groups)
        for column in range(metadata.row_group(group).num_columns)
    })
    if geo.get("version") != "1.1.0" or compression != ["ZSTD"]:
        raise FilterError("Published output must be GeoParquet 1.1.0 with ZSTD compression.")
    return {
        "rows": metadata.num_rows,
        "columns": metadata.num_columns,
        "geoparquet_version": geo["version"],
        "compression": compression,
    }


def publish_geoparquet(frame: gpd.GeoDataFrame, path: Path) -> dict[str, Any]:
    if frame.crs is None or frame.crs.to_epsg() != 4326:
        raise FilterError("Published GeoParquet must use EPSG:4326 geometry.")
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f".{path.stem}.pending.parquet")
    if pending.exists():
        pending.unlink()
    frame.to_parquet(pending, index=False, compression="zstd", geometry_encoding="WKB", schema_version="1.1.0")
    checks = validate_geoparquet(pending)
    pending.replace(path)
    return checks


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


ROOT = Path(__file__).resolve().parents[2]
FULL_PATH = ROOT / "data/interim/integrated/full/integrated_observations.parquet"
TEMPORAL_PATH = ROOT / "data/interim/integrated/temporal/observations_2000_2026.parquet"
MARINE_PATH = ROOT / "data/interim/integrated/marine/marine_observations.parquet"
GRID_OBSERVATIONS_PATH = ROOT / "data/interim/integrated/gridded/grid_observations.parquet"
GRID_SUMMARY_PATH = ROOT / "data/interim/integrated/gridded/species_cell_period_summary.parquet"
INTEGRATION_REPORT_PATH = ROOT / "docs/records/2026-10-16-integration-manifest.json"
TEMPORAL_REPORT_PATH = ROOT / "docs/records/2026-10-16-temporal-filter-report.json"
TEMPORAL_REPORT_MD_PATH = ROOT / "docs/records/2026-10-16-temporal-filter-report.md"
MARINE_BLOCKER_PATH = ROOT / "docs/records/2026-10-16-marine-filter-blocker.json"
MARINE_BLOCKER_MD_PATH = ROOT / "docs/records/2026-10-16-marine-filter-blocker.md"
GRID_REPORT_PATH = ROOT / "docs/records/2026-10-16-spatial-grid-report.json"
GRID_REPORT_MD_PATH = ROOT / "docs/records/2026-10-16-spatial-grid-report.md"
COVERAGE_CROSSTAB_PATH = ROOT / "docs/records/2026-10-16-environmental-coverage-by-geography-and-period.json"
COVERAGE_CROSSTAB_MD_PATH = ROOT / "docs/records/2026-10-16-environmental-coverage-by-geography-and-period.md"
GSHHG_ARCHIVE_PATH = ROOT / "data/raw/geography/gshhg/gshhg-shp-2.3.7.zip"
DEFAULT_MARINE_PATH = ROOT / "data/interim/geography/sri_lanka_marine_water.gpkg"
MARINE_PROVENANCE_PATH = ROOT / "docs/records/2026-10-16-gshhg-marine-reference.json"
GSHHG_SHA256 = "8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41"
STUDY_BOUNDS = (77.02333333333333, 2.5665, 85.23291666666667, 11.44883333333333)


def progress(message: str) -> None:
    """Show progress on stderr, separate from the final readable summary."""
    print(f"[Script 9] {message}", file=sys.stderr, flush=True)


def display_path(path: Path, root: Path = ROOT) -> str:
    """Prefer repository-relative paths in the console."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def print_temporal_summary(report: dict[str, Any]) -> None:
    """Print the temporal results without dumping the full JSON report."""
    compression = ", ".join(report["geoparquet"].get("compression", [])) or "not reported"
    print("\nTemporal filtering complete.")
    print(f"  Input observations: {report['input_rows']:,}")
    print(f"  Retained (2000–2026): {report['retained_rows']:,}")
    print(f"  Excluded: {report['excluded_rows']:,}")
    print("  Retained by period:")
    for period, count in report["counts_by_analysis_period"].items():
        print(f"    {period}: {count:,}")
    print("  Excluded by date:")
    for reason, count in report["counts_by_reason"].items():
        if reason != "retained_2000_2026":
            print(f"    {reason.replace('_', ' ')}: {count:,}")
    print(f"  Output: {report['output']}")
    print(
        f"  Format: GeoParquet {report['geoparquet'].get('geoparquet_version', 'unknown')} "
        f"with {compression} compression"
    )
    print("  Reports:")
    print(f"    Readable summary: {display_path(TEMPORAL_REPORT_MD_PATH)}")
    print(f"    Detailed data: {display_path(TEMPORAL_REPORT_PATH)}")
    crosstab = report.get("environmental_coverage_by_geography_and_period", {})
    if crosstab:
        print(f"    Geographic/environmental comparison: {crosstab.get('markdown')}")


def print_marine_grid_summary(report: dict[str, Any]) -> None:
    """Print Policy B and grid results in a compact console summary."""
    counts = report["counts"]
    print("\nPolicy B marine water-centre filtering and grid summaries complete.")
    print(f"  Marine source: {report['marine_mask']['citation_or_source_id']}")
    print(f"  Temporal observations reviewed: {counts['input_temporal_rows']:,}")
    print(f"  Water-centre matches before flag checks: {counts['inside_marine_polygon']:,}")
    print(f"  Excluded by ON_LAND/MARINE_UNSURE/invalid flags: {counts['excluded_by_geographic_quality_flags']:,}")
    print(f"  Policy B water-centre candidates retained: {counts['retained_verified_marine_rows']:,}")
    print("  Retained positional-confidence diagnostics:")
    for category, count in report.get("retained_position_confidence_counts", {}).items():
        print(f"    {category.replace('_', ' ')}: {count:,}")
    print("  Known uncertainty does not determine Policy B eligibility.")
    print(
        "  Polygon-boundary observations excluded: "
        f"{counts['marine_polygon_boundary_excluded_by_strict_contains']:,}"
    )
    print("  Grid outputs:")
    print(f"    Individual observations: {report['individual_grid_rows']:,}")
    print(f"    Distinct matched cells: {report['distinct_matched_grid_cells']:,}")
    print(f"    Observations without a raster cell: {report['marine_rows_without_raster_cell']:,}")
    print(f"    Species/cell/period summaries: {report['species_cell_period_summary_rows']:,}")
    print("  Files:")
    print(f"    Marine observations: {report['marine_output']}")
    print(f"    Gridded observations: {report['outputs']['individuals']}")
    print(f"    Species/cell/period summary: {report['outputs']['species_cell_period_summary']}")
    print("  Detailed reports:")
    print(f"    Readable summary: {display_path(GRID_REPORT_MD_PATH)}")
    print(f"    Detailed data: {display_path(GRID_REPORT_PATH)}")
    print("  Counts describe occurrence records, not animal abundance.")


def period_label(year: int) -> str:
    if 2000 <= year <= 2009:
        return "2000-2009"
    if 2010 <= year <= 2019:
        return "2010-2019"
    if 2020 <= year <= 2026:
        return "2020-2026"
    return "outside_2000_2026"


ENVIRONMENT_PERIOD_LABELS = {
    "baseline_2000": "2000-2009",
    "baseline_2010": "2010-2019",
    "ssp245_2020": "2020-2026",
}
GEOGRAPHIC_GROUPS = (
    "ON_LAND",
    "MARINE_UNSURE (excluding ON_LAND overlap)",
    "Neither ON_LAND nor MARINE_UNSURE",
)


def parse_obis_flags(value: Any) -> tuple[set[str], bool]:
    """Parse exact tokens from the cleaned OBIS JSON-array flags field."""
    if value is None or pd.isna(value):
        return set(), False
    try:
        parsed = json.loads(str(value))
    except (json.JSONDecodeError, TypeError):
        return set(), False
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        return set(), False
    return set(parsed), True


def geographic_quality_group(flags: set[str]) -> str:
    if "ON_LAND" in flags:
        return GEOGRAPHIC_GROUPS[0]
    if "MARINE_UNSURE" in flags:
        return GEOGRAPHIC_GROUPS[1]
    return GEOGRAPHIC_GROUPS[2]


def expected_environment_columns(manifest: dict[str, Any], period: str) -> list[str]:
    feature_columns = manifest.get("feature_columns")
    if not isinstance(feature_columns, dict):
        raise FilterError("Integration manifest lacks the feature-column coverage metadata.")
    return [
        column for column, feature in feature_columns.items()
        if period in feature.get("source_periods", []) or feature.get("has_static_source", False)
        if period not in feature.get("quarantined_periods", [])
    ]


def environmental_coverage_crosstab(temporal: gpd.GeoDataFrame, manifest: dict[str, Any]) -> dict[str, Any]:
    """Summarize environmental completeness by exact quality tags and period."""
    flag_values = [parse_obis_flags(value) for value in temporal.get("flags", pd.Series(index=temporal.index, dtype=object))]
    groups = [geographic_quality_group(flags) for flags, _ in flag_values]
    group_by_index = dict(zip(temporal.index, groups))
    invalid_flags = sum(not valid for _, valid in flag_values)
    rows: list[dict[str, Any]] = []
    coverage_totals = Counter()
    for period, label in ENVIRONMENT_PERIOD_LABELS.items():
        period_rows = temporal.loc[temporal["analysis_period"] == label]
        expected = expected_environment_columns(manifest, period)
        missing_columns = sorted(set(expected) - set(period_rows.columns))
        if missing_columns:
            raise FilterError(f"Temporal data lacks environmental columns from the integration manifest: {missing_columns[:5]}")
        for group_name in GEOGRAPHIC_GROUPS:
            indexes = [
                index for index in period_rows.index
                if group_by_index[index] == group_name
            ]
            group_rows = period_rows.loc[indexes]
            valid_counts = group_rows[expected].notna().sum(axis=1) if expected else pd.Series(0, index=group_rows.index)
            complete = int((valid_counts == len(expected)).sum()) if expected else 0
            partial = int(((valid_counts > 0) & (valid_counts < len(expected))).sum()) if expected else 0
            none = int((valid_counts == 0).sum())
            species_ids = {
                key for _, row in group_rows.iterrows()
                if (key := taxonomy_species_key(row)) is not None
            }
            item = {
                "geographic_quality_group": group_name,
                "analysis_period": label,
                "total_observation_records": len(group_rows),
                "complete_environmental_coverage": complete,
                "partial_environmental_coverage": partial,
                "no_valid_environmental_values": none,
                "distinct_species_rank_taxonomic_identifiers": len(species_ids),
                "expected_environment_feature_count": len(expected),
            }
            if complete + partial + none != len(group_rows):
                raise FilterError("Environmental coverage categories do not reconcile to the group row count.")
            coverage_totals[label] += len(group_rows)
            rows.append(item)

    reconciled_rows = sum(item["total_observation_records"] for item in rows)
    if reconciled_rows != len(temporal) or any(coverage_totals[label] != int((temporal["analysis_period"] == label).sum()) for label in ENVIRONMENT_PERIOD_LABELS.values()):
        raise FilterError("Geographic/environmental cross-tab row counts do not reconcile to the temporal dataset.")
    return {
        "format": "oceavera-environmental-coverage-crosstab",
        "temporal_rows": len(temporal),
        "row_count_reconciliation": {
            "cross_tab_total": reconciled_rows,
            "temporal_dataset_rows": len(temporal),
            "matches": reconciled_rows == len(temporal),
        },
        "unparseable_or_missing_flag_rows": invalid_flags,
        "group_priority": [
            "ON_LAND takes priority when both exact flags occur.",
            "MARINE_UNSURE excludes ON_LAND overlaps.",
            "Neither group means neither exact flag was parsed; malformed or missing flags are counted separately and are not evidence of marine location.",
        ],
        "marine_policy_context": "D-054 Policy B applies after this temporal diagnostic: exact ON_LAND and MARINE_UNSURE flags remain excluded; unflagged points inside the GSHHG water polygon are retained regardless of positional-uncertainty footprint. This cross-tab itself does not select records.",
        "rows": rows,
    }


def write_coverage_crosstab(report: dict[str, Any]) -> None:
    write_json(COVERAGE_CROSSTAB_PATH, report)
    lines = [
        "# Environmental coverage by geographic-quality flags and observation period",
        "",
        f"- Temporal observations: **{report['temporal_rows']:,}**",
        f"- Cross-tab reconciliation: **{report['row_count_reconciliation']['cross_tab_total']:,} / {report['row_count_reconciliation']['temporal_dataset_rows']:,} rows**",
        f"- Missing or invalid JSON flags: **{report['unparseable_or_missing_flag_rows']:,}** (not interpreted as marine verification)",
        "",
        "| Geographic-quality group | Period | Total records | Complete environment | Partial environment | No valid values | Distinct species-rank IDs |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        f"| {row['geographic_quality_group']} | {row['analysis_period']} | {row['total_observation_records']:,} | {row['complete_environmental_coverage']:,} | {row['partial_environmental_coverage']:,} | {row['no_valid_environmental_values']:,} | {row['distinct_species_rank_taxonomic_identifiers']:,} |"
        for row in report["rows"]
    )
    lines.extend([
        "",
        "Coverage is measured against the feature columns supported by that period, including static terrain. The groups are diagnostic only; they do not select species or filter observations. `ON_LAND` has priority over `MARINE_UNSURE`; malformed/missing flag arrays are counted separately and are not treated as proof of marine location.",
        "",
        "Current marine selection is Policy B under D-054. Exact `ON_LAND` and `MARINE_UNSURE` flags remain excluded; for other records, a water-centre match is required and uncertainty is recorded as a diagnostic.",
        "",
    ])
    COVERAGE_CROSSTAB_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def read_integration(root: Path, input_path: Path) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    if not input_path.is_file():
        raise FilterError(f"Full integrated GeoParquet is missing: {input_path}")
    manifest_path = INTEGRATION_REPORT_PATH if INTEGRATION_REPORT_PATH.is_absolute() else root / INTEGRATION_REPORT_PATH
    if not manifest_path.is_file():
        raise FilterError(f"Integration manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_hash = manifest.get("output", {}).get("sha256")
    if not expected_hash or hashlib.sha256(input_path.read_bytes()).hexdigest() != expected_hash:
        raise FilterError("Full GeoParquet checksum does not match the persisted integration manifest.")
    frame = gpd.read_parquet(input_path)
    required = {
        "resolved_event_year", "environment_period", "temporal_eligibility",
        "temporal_resolution_status", "integration_source_row", "raster_row",
        "raster_column", "raster_cell_id", "flags",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise FilterError(f"Integrated GeoParquet lacks required fields: {missing}")
    if frame.crs is None or frame.crs.to_epsg() != 4326:
        raise FilterError("Integrated GeoParquet geometry must use EPSG:4326.")
    if len(frame) != manifest.get("records", {}).get("cleaned_obis_rows"):
        raise FilterError("Integrated GeoParquet row count does not match the manifest's cleaned OBIS count.")
    if len(frame.columns) != manifest.get("records", {}).get("output_fields"):
        raise FilterError("Integrated GeoParquet field count does not match the manifest.")
    if manifest.get("records", {}).get("original_obis_field_count") != 112 or manifest.get("records", {}).get("original_obis_fields_preserved_exactly") != 112:
        raise FilterError("Integration manifest does not verify preservation of all 112 original OBIS fields.")
    feature_columns = manifest.get("feature_columns")
    if not isinstance(feature_columns, dict) or len(feature_columns) != 382:
        raise FilterError("Integration manifest does not contain the 382 environmental feature definitions.")
    if not set(feature_columns).issubset(frame.columns):
        raise FilterError("Full GeoParquet is missing environmental feature columns recorded in the manifest.")
    if frame["integration_source_row"].isna().any() or frame["integration_source_row"].duplicated().any():
        raise FilterError("Full GeoParquet contains missing or duplicate source-row identifiers.")
    return frame, manifest


def write_temporal_stage(
    frame: gpd.GeoDataFrame,
    output_path: Path,
    root: Path,
    integration_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    eligible_periods = set(ENVIRONMENT_PERIOD_LABELS)
    valid = frame["temporal_eligibility"].eq("eligible") & frame["environment_period"].isin(eligible_periods)
    temporal = frame.loc[valid].copy().reset_index(drop=True)
    temporal["analysis_period"] = temporal["environment_period"].map(ENVIRONMENT_PERIOD_LABELS)

    reasons = Counter()
    for _, row in frame.iterrows():
        raw_year = row["resolved_event_year"]
        if row["temporal_eligibility"] == "eligible":
            reasons["retained_2000_2026"] += 1
        elif row["temporal_eligibility"] == "ambiguous":
            reasons["ambiguous_temporal_assignment"] += 1
        elif pd.isna(raw_year) and row["temporal_eligibility"] == "unknown":
            reasons["missing_or_invalid_date"] += 1
        elif not pd.isna(raw_year) and raw_year < 2000:
            reasons["before_2000"] += 1
        elif not pd.isna(raw_year) and raw_year > 2026:
            reasons["after_2026"] += 1
        else:
            reasons["interval_outside_supported_periods"] += 1
    if sum(reasons.values()) != len(frame):
        raise FilterError("Temporal retain/exclusion reason counts do not reconcile with full integration rows.")
    output_checks = publish_geoparquet(temporal, output_path)
    readback = gpd.read_parquet(output_path)
    if len(readback) != len(temporal):
        raise FilterError("Temporal GeoParquet read-back row count changed.")
    if readback["integration_source_row"].tolist() != temporal["integration_source_row"].tolist():
        raise FilterError("Temporal GeoParquet read-back changed row identity or order.")
    if len(readback) and (
        not readback["temporal_eligibility"].eq("eligible").all()
        or not readback["environment_period"].isin(eligible_periods).all()
    ):
        raise FilterError("Temporal output contains ambiguous or unsupported date evidence.")

    temporal_year = pd.to_numeric(temporal["resolved_event_year"], errors="coerce").dropna()
    integration_manifest = integration_manifest or json.loads(INTEGRATION_REPORT_PATH.read_text(encoding="utf-8"))
    coverage_crosstab = environmental_coverage_crosstab(temporal, integration_manifest)
    write_coverage_crosstab(coverage_crosstab)

    report = {
        "format": "oceavera-temporal-filter-report-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": "data/interim/integrated/full/integrated_observations.parquet",
        "output": output_path.relative_to(root).as_posix(),
        "input_rows": len(frame),
        "retained_rows": len(temporal),
        "excluded_rows": len(frame) - len(temporal),
        "counts_by_reason": dict(reasons),
        "counts_by_analysis_period": dict(Counter(temporal["analysis_period"])),
        "counts_by_temporal_resolution_status": dict(Counter(temporal["temporal_resolution_status"])),
        "year_min": int(temporal_year.min()) if len(temporal_year) else None,
        "year_max": int(temporal_year.max()) if len(temporal_year) else None,
        "date_assignment_comparison": integration_manifest.get("date_resolution_comparison_to_previous_rule", {}),
        "environmental_coverage_by_geography_and_period": {
            "json": COVERAGE_CROSSTAB_PATH.relative_to(root).as_posix(),
            "markdown": COVERAGE_CROSSTAB_MD_PATH.relative_to(root).as_posix(),
            "row_count_reconciliation": coverage_crosstab["row_count_reconciliation"],
        },
        "marine_policy_context": "D-054 Policy B: temporal eligibility alone does not establish marine eligibility; see the spatial-grid report for current water-centre screening.",
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "geoparquet": output_checks,
        "limits": [
            "Rows are retained only when date evidence supports one Bio-ORACLE environmental period within 2000–2026; interval-only records are retained only when the interval is wholly within one period.",
            "Unresolved cross-period or contradictory date evidence remains in the full archive and is excluded from this strict temporal output.",
            "An environmental time slice is a decadal source approximation, not an annual measurement.",
            "Temporal eligibility does not establish marine eligibility.",
        ],
    }
    write_json(TEMPORAL_REPORT_PATH, report)
    lines = [
        "# Temporal filtering report",
        "",
        f"- Input rows: **{len(frame):,}**",
        f"- Retained rows with verified temporal eligibility from 2000 through 2026: **{len(temporal):,}**",
        f"- Excluded rows: **{len(frame) - len(temporal):,}**",
        f"- Output: `{output_path.relative_to(root).as_posix()}`",
        "",
        "| Period | Rows |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {period} | {count:,} |" for period, count in report["counts_by_analysis_period"].items())
    lines.extend(["", "| Exclusion or retention reason | Rows |", "| --- | ---: |"])
    lines.extend(f"| {reason} | {count:,} |" for reason, count in reasons.items())
    lines.extend([
        "",
        "The temporal stage keeps individual observations and their point geometry. Single-year evidence must agree by environmental period and be consistent with date intervals. Interval-only rows are retained only when the complete interval fits one supported period. Ambiguous records remain in the full archive. The year limit is not a marine boundary.",
        "",
        "This temporal dataset is independent of marine selection. Current marine candidates are produced by Policy B, which requires a valid unflagged point inside the sourced water polygon and records coordinate uncertainty without using it as an exclusion.",
        "",
        f"The geographic/environmental diagnostic cross-tab is in `{COVERAGE_CROSSTAB_MD_PATH.relative_to(root).as_posix()}`. It is a summary only and does not perform marine filtering or species selection.",
        "",
    ])
    TEMPORAL_REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    return report


def write_marine_blocker(root: Path, temporal_rows: int, reference_error: str | None = None) -> None:
    report = {
        "format": "oceavera-marine-filter-blocker-v1",
        "status": "blocked_missing_verified_marine_area",
        "temporal_rows_waiting_for_marine_review": temporal_rows,
        "checked_local_search": [
            "data/interim/", "data/raw/", "docs/records/", "docs/data/",
        ],
        "reason": "No local publisher-identified water polygon or independently validated land-sea mask was present. Bio-ORACLE's rectangular collection envelope, source marine flag, raster cell footprint, and terrain coastline/landmass layers are not accepted as independent proof that an observation is marine.",
        "not_produced": [
            "data/interim/integrated/marine/marine_observations.parquet",
            "data/interim/integrated/gridded/grid_observations.parquet",
            "data/interim/integrated/gridded/species_cell_period_summary.parquet",
        ],
        "next_input_required": "Restore the default prepared positive-water GeoPackage and its tracked provenance, or the official GSHHG archive for one-time preparation. Routine execution uses those project defaults; CLI overrides are optional.",
        "reference_error": reference_error,
        "source_records": [
            "docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md",
            "docs/records/2026-10-09-source-marine-regions-sri-lanka-eez-bounds.md",
        ],
    }
    write_json(MARINE_BLOCKER_PATH, report)
    markdown = [
        "# Marine filtering and grid-summary blocker",
        "",
        f"**Status: BLOCKED** — {temporal_rows:,} temporally eligible point records await an independently verified marine-area source.",
        "",
        report["reason"],
        "",
        "The collection rectangle and raster values do not distinguish all marine points from land points. The OBIS `marine` field can contradict that evidence and is not used alone. No marine or gridded output was published.",
        "",
        f"Next input: {report['next_input_required']}",
        "",
    ]
    MARINE_BLOCKER_MD_PATH.write_text("\n".join(markdown), encoding="utf-8")


def marine_exclusion_flags(value: Any) -> tuple[bool, bool, bool]:
    """Return exact ON_LAND, MARINE_UNSURE and valid-JSON-array states."""
    flags, valid = parse_obis_flags(value)
    return "ON_LAND" in flags, "MARINE_UNSURE" in flags, valid


def taxonomy_species_key(row: pd.Series) -> str | None:
    if str(row.get("taxonRank", "")).strip().casefold() != "species":
        return None
    for field in ("AphiaID", "aphiaID", "scientificNameID", "taxonID"):
        value = row.get(field)
        if value is not None and not pd.isna(value) and str(value).strip():
            return f"{field}:{str(value).strip()}"
    return None


def make_cell_polygon(longitudes: np.ndarray, latitudes: np.ndarray, row: int, column: int) -> Polygon:
    lon_edges = cell_edges(longitudes)
    lat_edges = cell_edges(latitudes)
    west, east = sorted((float(lon_edges[column]), float(lon_edges[column + 1])))
    south, north = sorted((float(lat_edges[row]), float(lat_edges[row + 1])))
    return Polygon([(west, south), (east, south), (east, north), (west, north), (west, south)])


def validate_grid_count_reconciliation(species_rows: pd.DataFrame, summary: pd.DataFrame) -> dict[str, Any]:
    """Verify each species/cell/period count and its total against source rows."""
    keys = ["taxonomy_species_key", "grid_cell_id", "raster_row", "raster_column", "analysis_period"]
    if species_rows.empty:
        expected: dict[tuple[Any, ...], int] = {}
    else:
        expected = {
            tuple(key if isinstance(key, tuple) else (key,)): int(count)
            for key, count in species_rows.groupby(keys, sort=True, dropna=False).size().items()
        }
    actual: dict[tuple[Any, ...], int] = {}
    for _, row in summary.iterrows():
        key = tuple(row[field] for field in keys)
        actual[key] = int(row["occurrence_record_count"])
    if expected != actual:
        raise FilterError("Gridded occurrence_record_count values do not reconcile with the source observations.")
    source_rows = len(species_rows)
    summary_rows = int(summary["occurrence_record_count"].sum()) if len(summary) else 0
    if source_rows != summary_rows:
        raise FilterError("Summed gridded occurrence counts do not equal eligible species/cell/period observations.")
    return {
        "source_species_rank_observations": source_rows,
        "summed_summary_occurrence_record_count": summary_rows,
        "matches": source_rows == summary_rows,
        "species_cell_period_keys_match": expected == actual,
    }


def read_grid_axes(root: Path, integration_manifest: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    expected = integration_manifest["spatial_grid"]
    if "latitude_axis_centres" not in expected or "longitude_axis_centres" not in expected:
        raise FilterError("Integration manifest lacks persisted raster coordinate axes; rerun Script 8 first.")
    latitudes = np.asarray(expected["latitude_axis_centres"], dtype=float)
    longitudes = np.asarray(expected["longitude_axis_centres"], dtype=float)
    if (len(latitudes), len(longitudes)) != (expected["rows"], expected["columns"]):
        raise FilterError("Persisted raster coordinate axes do not match the integration grid dimensions.")
    latitude_hash = hashlib.sha256(np.asarray(latitudes, dtype="<f8").tobytes()).hexdigest()
    longitude_hash = hashlib.sha256(np.asarray(longitudes, dtype="<f8").tobytes()).hexdigest()
    if latitude_hash != expected["latitude_axis_sha256"] or longitude_hash != expected["longitude_axis_sha256"]:
        raise FilterError("Persisted raster coordinate axes do not match their recorded fingerprints.")
    return longitudes, latitudes


def file_sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def prepare_default_marine_reference() -> dict[str, Any]:
    """Prepare the downloaded full-resolution source once; never download on a run."""
    if DEFAULT_MARINE_PATH.is_file():
        if not MARINE_PROVENANCE_PATH.is_file():
            raise FilterError("Prepared marine reference lacks its provenance record.")
        record = json.loads(MARINE_PROVENANCE_PATH.read_text(encoding="utf-8"))
        if record.get("prepared_sha256") != file_sha256(DEFAULT_MARINE_PATH):
            raise FilterError("Prepared marine reference checksum does not match provenance.")
        if record.get("status") != "validated" or record.get("study_bounds") != list(STUDY_BOUNDS):
            raise FilterError("Marine reference provenance has an unexpected status or extent.")
        return record
    if not GSHHG_ARCHIVE_PATH.is_file():
        raise FilterError("Official GSHHG archive is absent: data/raw/geography/gshhg/gshhg-shp-2.3.7.zip")
    if file_sha256(GSHHG_ARCHIVE_PATH) != GSHHG_SHA256:
        raise FilterError("GSHHG archive checksum differs from the recorded official download.")
    progress("Preparing reusable full-resolution GSHHG water geometry (first run only)")
    envelope = box(*STUDY_BOUNDS)
    levels = {}
    for level in (1, 2, 3, 4):
        layer = f"zip://{GSHHG_ARCHIVE_PATH}!GSHHS_shp/f/GSHHS_f_L{level}.shp"
        levels[level] = gpd.read_file(layer, bbox=STUDY_BOUNDS)
        if levels[level].crs is None or levels[level].crs.to_epsg() != 4326:
            raise FilterError("GSHHG has an unexpected CRS.")
        if not levels[level].geometry.is_valid.all():
            raise FilterError("GSHHG source geometry is invalid; no silent geometry repair is permitted.")
    # L1 outer coastline shells include all enclosed inland waters. Keep them
    # excluded rather than adding L2 lakes back into the positive ocean mask.
    land = levels[1].geometry.intersection(envelope).union_all()
    water = envelope.difference(land)
    if water.is_empty or not water.is_valid or water.geom_type not in {"Polygon", "MultiPolygon"}:
        raise FilterError("Prepared positive marine-water geometry is empty or invalid.")
    samples = [
        ("offshore_south", 80.0, 5.0, True),
        ("mainland_interior", 80.7, 7.5, False),
        ("Delft_island", 79.7, 9.51, False),
        ("Kandy_inland_water_location", 80.642, 7.291, False),
    ]
    tests = [{"name": name, "longitude": x, "latitude": y,
              "expected_marine": expected, "actual_marine": bool(water.contains(Point(x, y)))}
             for name, x, y, expected in samples]
    for index, lake in enumerate(levels[2].geometry):
        point = lake.intersection(envelope).representative_point()
        tests.append({"name": f"L2_inland_water_{index}", "expected_marine": False,
                      "actual_marine": bool(water.contains(point))})
    coastline = levels[1].loc[levels[1].geometry.contains(Point(80.7, 7.5))].geometry.iloc[0]
    boundary_point = Point(coastline.exterior.coords[len(coastline.exterior.coords) // 2])
    tests.append({"name": "exact_source_coast_boundary", "expected_marine": False,
                  "actual_marine": bool(water.contains(boundary_point))})
    if any(item["actual_marine"] != item["expected_marine"] for item in tests):
        raise FilterError(f"Marine reference location sanity check failed: {tests}")
    DEFAULT_MARINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    gpd.GeoDataFrame({"source": ["GSHHG 2.3.7 full resolution"]}, geometry=[water], crs=4326).to_file(
        DEFAULT_MARINE_PATH, layer="marine_water", driver="GPKG",
    )
    readback = gpd.read_file(DEFAULT_MARINE_PATH)
    if not readback.geometry.is_valid.all() or not readback.geometry.iloc[0].equals(water):
        raise FilterError("Prepared marine-water read-back failed.")
    record = {
        "status": "validated", "publisher": "Paul Wessel (SOEST) and Walter H. F. Smith (NOAA)",
        "dataset": "Global Self-consistent Hierarchical High-resolution Geography",
        "version": "2.3.7", "publication_date": "2017-06-15",
        "official_url": "https://ftp.soest.hawaii.edu/gshhg/gshhg-shp-2.3.7.zip",
        "documentation_url": "https://www.soest.hawaii.edu/wessel/gshhg/",
        "citation": "GSHHG 2.3.7, Wessel and Smith; DOI 10.1029/96JB00104; full-resolution coastline; D-048 collection envelope",
        "licence": "GNU Lesser General Public License, as distributed in archive",
        "retrieval_date_utc": "2026-10-15", "source_archive": GSHHG_ARCHIVE_PATH.relative_to(ROOT).as_posix(),
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive_bytes": GSHHG_ARCHIVE_PATH.stat().st_size, "archive_sha256": GSHHG_SHA256,
        "resolution": "full (f), original source resolution; no uniform metre accuracy claimed",
        "study_bounds": list(STUDY_BOUNDS), "scope": "D-048 source collection rectangle; no EEZ clipping or final modelling domain selection",
        "source_polygons_intersecting_extent_by_level": {str(k): len(v) for k, v in levels.items()},
        "topology": "Envelope minus union of L1 land outer shells. L2-L4 inspected; all enclosed freshwater remains excluded with land. No Bio-ORACLE masks used.",
        "crs": "EPSG:4326", "geometry_type": water.geom_type,
        "prepared_path": DEFAULT_MARINE_PATH.relative_to(ROOT).as_posix(),
        "prepared_sha256": file_sha256(DEFAULT_MARINE_PATH), "prepared_bytes": DEFAULT_MARINE_PATH.stat().st_size,
        "location_sanity_tests": tests,
        "limits": ["2017 source is not a current shoreline survey; small islands, lagoons and reclamation can differ.",
                   "Sanity tests check topology and sample locations, not metre-level coastal accuracy.",
                   "Marine mask covers the collection rectangle only; uncertainty beyond it is unverified."],
    }
    write_json(MARINE_PROVENANCE_PATH, record)
    return record


def geodesic_uncertainty_footprint(longitude: float, latitude: float, metres: float) -> Polygon:
    """Approximate a WGS84 uncertainty disk using 360 geodesic bearings."""
    bearings = np.arange(360, dtype=float)
    # Circumscribe the disk to avoid accepting a footprint through chord gaps.
    radius = metres / math.cos(math.pi / 360)
    xs, ys, _ = Geod(ellps="WGS84").fwd(
        np.full(360, longitude), np.full(360, latitude), bearings, np.full(360, radius),
    )
    return Polygon(zip(xs, ys))


def apply_marine_mask(
    temporal: gpd.GeoDataFrame,
    mask_path: Path,
    mask_source: str,
    output_path: Path,
    root: Path,
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    mask = gpd.read_file(mask_path)
    source_crs = str(mask.crs)
    if mask.crs is None:
        raise FilterError("Marine area has no CRS.")
    mask = mask.to_crs(4326)
    if mask.empty or not mask.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise FilterError("Marine area must contain polygon geometries.")
    if mask.geometry.isna().any() or not mask.geometry.is_valid.all():
        raise FilterError("Marine area contains missing or invalid geometry.")
    if temporal.crs is None or temporal.crs.to_epsg() != 4326:
        raise FilterError("Observation geometry must use EPSG:4326.")
    if "flags" not in temporal.columns:
        raise FilterError("Policy B requires the original OBIS JSON flags.")
    water = mask.geometry.union_all()
    prepared = prep(water)
    coverage = box(*mask.total_bounds)
    reasons, confidence, retained, known_verified, inside = [], [], [], [], []
    flag_states = [marine_exclusion_flags(value) for value in temporal["flags"]]
    boundary_count = 0
    for index, (_, row) in enumerate(temporal.iterrows()):
        point = row.geometry
        valid = (point is not None and not point.is_empty and point.geom_type == "Point"
                 and point.is_valid and math.isfinite(point.x) and math.isfinite(point.y)
                 and -180 <= point.x <= 180 and -90 <= point.y <= 90)
        is_inside = bool(valid and prepared.contains(point))
        inside.append(is_inside)
        on_land, unsure, valid_flags = flag_states[index]
        reason, category = "", "not_marine_by_centre"
        if is_inside:
            raw_uncertainty = row.get("coordinateUncertaintyInMeters")
            raw_text = "" if raw_uncertainty is None or pd.isna(raw_uncertainty) else str(raw_uncertainty).strip()
            if raw_text.casefold() in {"", "nan", "<na>", "none", "null"}:
                category = "unknown_uncertainty"
            else:
                try:
                    uncertainty = float(raw_text)
                except (TypeError, ValueError):
                    uncertainty = math.nan
                if not math.isfinite(uncertainty) or uncertainty <= 0:
                    category = "invalid_uncertainty"
                else:
                    footprint = geodesic_uncertainty_footprint(point.x, point.y, uncertainty)
                    if not coverage.contains(footprint):
                        category = "known_footprint_outside_reference_extent"
                    elif not prepared.contains(footprint):
                        category = "known_footprint_crosses_coast_or_land"
                    else:
                        category = "known_footprint_marine"
        if not valid:
            reason = "invalid_coordinates"
        elif not valid_flags:
            reason = "missing_or_invalid_flags"
        elif on_land:
            reason = "ON_LAND"
        elif unsure:
            reason = "MARINE_UNSURE"
        elif not is_inside:
            boundary = bool(water.intersects(point))
            reason = "marine_boundary" if boundary else "outside_marine_water"
        else:
            reason = "retained_policy_b_water_centre"
        if valid and water.intersects(point) and not is_inside:
            boundary_count += 1
        reasons.append(reason)
        confidence.append(category)
        retained.append(reason == "retained_policy_b_water_centre")
        known_verified.append(category == "known_footprint_marine")
    annotated = temporal.copy()
    annotated["marine_point_verified"] = inside
    annotated["marine_position_confidence"] = confidence
    annotated["marine_uncertainty_verified"] = known_verified
    annotated["marine_filter_reason"] = reasons
    marine = annotated.loc[retained].copy().reset_index(drop=True)
    checks = publish_geoparquet(marine, output_path)
    readback = gpd.read_parquet(output_path)
    if not readback.equals(marine):
        raise FilterError("Marine GeoParquet read-back changed observation values or identities.")
    reason_counts = Counter(reasons)
    flag_array = np.asarray(flag_states, dtype=bool).reshape(-1, 3)
    on_land, unsure, valid_flags = flag_array.T
    counts = {
        "input_temporal_rows": len(temporal), "inside_marine_polygon": sum(inside),
        "on_land_flagged_rows": int(on_land.sum()), "marine_unsure_flagged_rows": int(unsure.sum()),
        "rows_with_both_flags": int((on_land & unsure).sum()),
        "missing_or_invalid_flags_rows": int((~valid_flags).sum()),
        "excluded_by_geographic_quality_flags": int((on_land | unsure | ~valid_flags).sum()),
        "retained_verified_marine_rows": len(marine),
        "retained_policy_b_water_centre_candidates": len(marine),
        "retained_known_uncertainty_marine": int(marine["marine_position_confidence"].eq("known_footprint_marine").sum()),
        "retained_unknown_uncertainty": int(marine["marine_position_confidence"].isin(["unknown_uncertainty", "invalid_uncertainty"]).sum()),
        "retained_known_uncertainty_crosses_coast_or_land": int(marine["marine_position_confidence"].eq("known_footprint_crosses_coast_or_land").sum()),
        "retained_known_uncertainty_outside_reference": int(marine["marine_position_confidence"].eq("known_footprint_outside_reference_extent").sum()),
        "retained_invalid_uncertainty": int(marine["marine_position_confidence"].eq("invalid_uncertainty").sum()),
        "excluded_by_known_uncertainty": 0,
        "marine_polygon_boundary_excluded_by_strict_contains": boundary_count,
    }
    if sum(reason_counts.values()) != len(temporal) or sum(retained) != len(marine):
        raise FilterError("Marine exclusion reasons do not reconcile.")
    decisions = [{"integration_source_row": int(source), "reason": reason, "positional_confidence": category}
                 for source, reason, category in zip(temporal["integration_source_row"], reasons, confidence)]
    report = {
        "format": "oceavera-spatial-grid-report-v1", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "marine_mask": {"path": display_path(mask_path, root), "citation_or_source_id": mask_source,
                        "sha256": file_sha256(mask_path), "source_crs": source_crs, "polygon_count": len(mask),
                        "predicate": "strict contains; boundary excluded"},
        "counts": counts, "exclusive_decision_counts": dict(reason_counts), "observation_decisions": decisions,
        "position_confidence_counts": dict(Counter(confidence)),
        "retained_position_confidence_counts": dict(Counter(marine["marine_position_confidence"])),
        "policy_id": "D-054",
        "marine_policy": "Policy B: retain valid, unflagged observation points strictly inside the sourced GSHHG marine-water polygon. Known uncertainty footprints crossing land/coast or extending beyond the reference are retained and flagged; unknown or invalid uncertainty is explicit. ON_LAND and MARINE_UNSURE remain excluded.",
        "uncertainty_affects_eligibility": False,
        "uncertainty_method": "360 WGS84 geodesic bearings; circumradius inflation 1/cos(pi/360). Approximation inherits GSHHG shoreline accuracy.",
        "marine_output": display_path(output_path, root), "marine_geoparquet": checks,
        "on_land_and_marine_unsure_flags_are_excluded": True,
        "obis_marine_taxon_attribute_used_for_coordinate_verification": False,
        "limits": ["Policy B output is a marine water-centre candidate dataset, not proof of a precisely verified marine habitat footprint.",
                   "Known uncertainty footprints crossing land or outside reference coverage are retained for sensitivity analysis, not certified marine footprints.",
                   "Unknown or invalid uncertainty is not treated as zero.",
                   "Source shoreline accuracy, coastal change and unmapped features remain limitations."],
    }
    return marine, report


def build_grid_outputs(
    marine: gpd.GeoDataFrame,
    integration_manifest: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    longitudes, latitudes = read_grid_axes(root, integration_manifest)
    rows = pd.to_numeric(marine["raster_row"], errors="coerce")
    columns = pd.to_numeric(marine["raster_column"], errors="coerce")
    valid_cell = (rows.notna() & columns.notna() & rows.between(0, len(latitudes) - 1)
                  & columns.between(0, len(longitudes) - 1) & rows.eq(rows.round()) & columns.eq(columns.round()))
    expected_cell_ids = rows.fillna(-1).astype(int) * len(longitudes) + columns.fillna(-1).astype(int)
    existing_ids = pd.to_numeric(marine["raster_cell_id"], errors="coerce")
    if not np.array_equal(expected_cell_ids[valid_cell].to_numpy(), existing_ids[valid_cell].to_numpy(dtype=int)):
        raise FilterError("Raster cell IDs do not reconcile with the original source row/column indices.")

    grid = marine.copy().reset_index(drop=True)
    grid["grid_cell_id"] = pd.array([
        None if pd.isna(row) or pd.isna(column) else int(row) * len(longitudes) + int(column)
        for row, column in zip(rows.reset_index(drop=True), columns.reset_index(drop=True))
    ], dtype="Int64")
    if "analysis_period" not in grid.columns or not grid["analysis_period"].isin(ENVIRONMENT_PERIOD_LABELS.values()).all():
        raise FilterError("Marine rows lack a verified environmental analysis period.")
    grid_checks = publish_geoparquet(grid, GRID_OBSERVATIONS_PATH)
    grid_readback = gpd.read_parquet(GRID_OBSERVATIONS_PATH)
    if len(grid_readback) != len(grid) or grid_readback["integration_source_row"].tolist() != grid["integration_source_row"].tolist():
        raise FilterError("Individual gridded observations failed read-back reconciliation.")

    species_rows = []
    for _, row in grid.loc[valid_cell].iterrows():
        species_key = taxonomy_species_key(row)
        if species_key is None:
            continue
        species_rows.append({
            "taxonomy_species_key": species_key,
            "grid_cell_id": int(row["grid_cell_id"]),
            "raster_row": int(row["raster_row"]),
            "raster_column": int(row["raster_column"]),
            "analysis_period": row["analysis_period"],
            "event_year": None if pd.isna(row["resolved_event_year"]) else int(row["resolved_event_year"]),
            "source_row": int(row["integration_source_row"]),
        })
    species_frame = pd.DataFrame(species_rows)
    if species_frame.empty:
        summary_table = pd.DataFrame(columns=[
            "taxonomy_species_key", "grid_cell_id", "raster_row", "raster_column",
            "analysis_period", "occurrence_record_count", "first_event_year", "last_event_year", "geometry",
        ])
        summary = gpd.GeoDataFrame(summary_table, geometry="geometry", crs="EPSG:4326")
    else:
        grouping_fields = ["taxonomy_species_key", "grid_cell_id", "raster_row", "raster_column", "analysis_period"]
        summary = species_frame.groupby(
            grouping_fields,
            as_index=False,
            sort=True,
        ).agg(
            occurrence_record_count=("source_row", "size"),
            first_event_year=("event_year", "min"),
            last_event_year=("event_year", "max"),
        )
        environmental_columns = [column for column in grid.columns if column.startswith("bio_oracle__")]
        keyed_observations = grid.loc[valid_cell].copy()
        keyed_observations["taxonomy_species_key"] = [taxonomy_species_key(row) for _, row in keyed_observations.iterrows()]
        keyed_observations = keyed_observations.dropna(subset=["taxonomy_species_key"])
        if environmental_columns:
            environmental_groups = keyed_observations.groupby(grouping_fields, sort=True)[environmental_columns]
            variation = environmental_groups.nunique(dropna=True)
            if (variation > 1).to_numpy().any():
                raise FilterError("Environmental values vary within a single species, cell and period group.")
            environmental_summary = environmental_groups.first().reset_index()
            summary = summary.merge(environmental_summary, on=grouping_fields, how="left", validate="one_to_one")
        summary["geometry"] = [
            make_cell_polygon(longitudes, latitudes, int(row), int(column))
            for row, column in zip(summary["raster_row"], summary["raster_column"])
        ]
        summary = gpd.GeoDataFrame(summary, geometry="geometry", crs="EPSG:4326")
    count_reconciliation = validate_grid_count_reconciliation(species_frame, summary)
    summary_checks = publish_geoparquet(summary, GRID_SUMMARY_PATH)
    summary_readback = gpd.read_parquet(GRID_SUMMARY_PATH)
    if len(summary_readback) != len(summary):
        raise FilterError("Species/cell/period summary failed read-back reconciliation.")
    summary_counts = Counter(summary["analysis_period"].tolist()) if len(summary) else Counter()
    result = {
        "format": "oceavera-spatial-grid-report-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "marine_mask_note": "A sourced water polygon was applied; citation and scope are in the marine_mask object from the prior stage.",
        "marine_rows": len(marine),
        "individual_grid_rows": len(grid),
        "marine_rows_without_raster_cell": int((~valid_cell).sum()),
        "distinct_matched_grid_cells": int(grid.loc[valid_cell, "grid_cell_id"].nunique()),
        "species_rank_rows_with_taxonomy_key_and_grid_cell": len(species_frame),
        "ungrouped_taxonomy_observations": int(valid_cell.sum()) - len(species_frame),
        "unique_eligible_species_identifiers": int(species_frame["taxonomy_species_key"].nunique()) if len(species_frame) else 0,
        "individual_rows_by_period": dict(Counter(grid["analysis_period"])),
        "eligible_species_rows_by_period": dict(Counter(species_frame["analysis_period"])) if len(species_frame) else {},
        "ungrouped_taxonomy_by_period": dict(Counter(grid.loc[valid_cell & grid.apply(taxonomy_species_key, axis=1).isna(), "analysis_period"])),
        "species_cell_period_summary_rows": len(summary),
        "occurrence_count_reconciliation": count_reconciliation,
        "summary_rows_by_period": dict(summary_counts),
        "summary_key": "Explicit source taxonRank=species, keyed by AphiaID (fallback fields are recorded in the taxonomy_species_key prefix).",
        "summary_count_semantics": "occurrence_record_count is a count of OBIS rows, not abundance or population size.",
        "geometry": "Individual GeoParquet retains EPSG:4326 observation points; summary GeoParquet uses polygons constructed from adjacent Bio-ORACLE coordinate-axis midpoints.",
        "outputs": {
            "individuals": GRID_OBSERVATIONS_PATH.relative_to(root).as_posix(),
            "species_cell_period_summary": GRID_SUMMARY_PATH.relative_to(root).as_posix(),
        },
        "geoparquet": {"individuals": grid_checks, "summary": summary_checks},
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Filter observation dates, use the reusable GSHHG marine reference, and group Bio-ORACLE grid cells."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Ordinary execution discovers the prepared reference and provenance automatically. "
            "If needed, the existing official local archive is prepared once. No network access occurs on a routine run."
        ),
    )
    parser.add_argument(
        "--full", type=Path, default=FULL_PATH.relative_to(ROOT), metavar="PATH",
        help="Full integrated GeoParquet to filter by occurrence year.",
    )
    parser.add_argument(
        "--marine-mask", type=Path, default=None, metavar="PATH",
        help="Optional override for the default prepared marine-water reference.",
    )
    parser.add_argument(
        "--marine-source", default="", metavar="CITATION",
        help="Publisher/source identifier and scope; required with --marine-mask.",
    )
    args = parser.parse_args()
    root = ROOT
    full_path = args.full if args.full.is_absolute() else root / args.full
    mask_path = args.marine_mask
    if mask_path is not None and not mask_path.is_absolute():
        mask_path = root / mask_path
    if args.marine_mask is None and args.marine_source.strip():
        parser.error("--marine-source requires --marine-mask.")
    if args.marine_mask is not None and len(args.marine_source.strip()) < 10:
        parser.error("A meaningful --marine-source citation of at least 10 characters is required with --marine-mask.")
    if mask_path is not None and not mask_path.is_file():
        parser.error(f"Marine-area polygon not found: {display_path(mask_path, root)}")
    reference = None
    reference_error = None
    mask_source = args.marine_source
    if mask_path is None:
        try:
            reference = prepare_default_marine_reference()
            mask_path = DEFAULT_MARINE_PATH
            mask_source = reference["citation"]
        except (FilterError, OSError) as error:
            reference_error = str(error)
            progress(f"Marine reference unavailable: {reference_error}")

    total_steps = 3 if mask_path is not None else 2
    progress(f"Step 1/{total_steps}: reading integrated observations from {display_path(full_path, root)}")
    frame, integration_manifest = read_integration(root, full_path)
    progress(f"Step 2/{total_steps}: filtering {len(frame):,} observations to the 2000–2026 period")
    temporal_report = write_temporal_stage(frame, TEMPORAL_PATH, root, integration_manifest)
    progress(f"Temporal GeoParquet created with {temporal_report['retained_rows']:,} observations")
    print_temporal_summary(temporal_report)

    if mask_path is None:
        write_marine_blocker(root, temporal_report["retained_rows"], reference_error)
        print("\nMarine filtering and gridding were skipped for this run.")
        print("  The temporal stage completed successfully; this is a pending input, not a script error.")
        print(f"  Temporal output is ready: {display_path(TEMPORAL_PATH, root)}")
        print(
            f"  Next input: a documented marine-area polygon for {temporal_report['retained_rows']:,} "
            "eligible observations."
        )
        print(f"  Reference blocker: {reference_error}")
        print("  Restore the documented prepared reference/provenance or the official local GSHHG archive.")
        print("  This run did not create marine or gridded GeoParquet outputs.")
        print(f"  Blocker details: {display_path(MARINE_BLOCKER_MD_PATH, root)}")
        return 0

    progress(f"Step 3/{total_steps}: applying the supplied marine polygon from {display_path(mask_path, root)}")
    marine, marine_report = apply_marine_mask(
        gpd.read_parquet(TEMPORAL_PATH), mask_path, mask_source, MARINE_PATH, root,
    )
    progress(f"Marine polygon check retained {len(marine):,} observations; building grid outputs")
    marine_report.update(build_grid_outputs(marine, integration_manifest, root))
    marine_report["reference_provenance"] = reference
    write_json(GRID_REPORT_PATH, marine_report)
    write_json(MARINE_BLOCKER_PATH, {
        "status": "resolved",
        "resolved_by": GRID_REPORT_PATH.relative_to(root).as_posix(),
        "current_policy": "D-054 Policy B water-centre candidates; positional uncertainty is diagnostic only",
        "marine_observations": len(marine),
        "previous_strict_policy_results": "historical; see 2026-10-16-spatial-grid-report-strict-policy.json",
        "historical_blocker_preserved": "2026-10-16-pre-completion-evidence.json",
    })
    MARINE_BLOCKER_MD_PATH.write_text(
        "# Marine reference status\n\n**RESOLVED** — the validated GSHHG reference supports current D-054 Policy B water-centre candidates. "
        "Positional uncertainty is retained as a quality diagnostic and does not determine eligibility. See the "
        "[executed spatial-grid report](2026-10-16-spatial-grid-report.md) and "
        "[source provenance](2026-10-16-gshhg-marine-reference.json). Previous strict-policy results are preserved as "
        "[historical evidence](2026-10-16-spatial-grid-report-strict-policy.json); earlier blocker evidence remains in "
        "[pre-completion evidence](2026-10-16-pre-completion-evidence.json).\n", encoding="utf-8")
    GRID_REPORT_MD_PATH.write_text(
        "# Policy B marine filtering and spatial grid report\n\n"
        "The current outputs are **water-centre candidates**, not proof that every positional-uncertainty footprint is marine. "
        "Policy B excludes invalid points/flags, exact `ON_LAND` and `MARINE_UNSURE` flags, and points outside the GSHHG water polygon. "
        "It retains qualifying points regardless of uncertainty footprint and records that uncertainty for sensitivity review.\n\n"
        f"- Policy B water-centre observations retained: **{marine_report['counts']['retained_policy_b_water_centre_candidates']:,}**\n"
        f"- Known footprints fully inside water: **{marine_report['counts']['retained_known_uncertainty_marine']:,}**\n"
        f"- Known footprints crossing land/coast: **{marine_report['counts']['retained_known_uncertainty_crosses_coast_or_land']:,}**\n"
        f"- Known footprints extending beyond reference: **{marine_report['counts']['retained_known_uncertainty_outside_reference']:,}**\n"
        f"- Unknown or invalid uncertainty: **{marine_report['counts']['retained_unknown_uncertainty']:,}**\n"
        f"- Individual observations in the grid file: **{marine_report['individual_grid_rows']:,}**\n"
        f"- Identifier-bearing species-rank records: **{marine_report['species_rank_rows_with_taxonomy_key_and_grid_cell']:,}**\n"
        f"- Distinct occupied cells: **{marine_report['distinct_matched_grid_cells']:,}**\n"
        f"- Species/cell/period summary rows: **{marine_report['species_cell_period_summary_rows']:,}**\n"
        f"- Marine source: {marine_report['marine_mask']['citation_or_source_id']}\n\n"
        "Counts are occurrence records, not animal abundance. Bio-ORACLE extraction success does not independently establish marine location. "
        "No species selection, feature selection, target creation, background sampling or model training is performed.\n",
        encoding="utf-8",
    )
    progress("Marine and grid GeoParquet outputs passed read-back checks")
    print_marine_grid_summary(marine_report)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FilterError as error:
        print(f"Script 9 could not complete: {error}", file=sys.stderr)
        raise SystemExit(2)
    except (OSError, json.JSONDecodeError, UnicodeError) as error:
        print(f"Script 9 could not read or write a required file: {error}", file=sys.stderr)
        raise SystemExit(2)
