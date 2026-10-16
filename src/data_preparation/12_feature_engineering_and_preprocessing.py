"""OCEAVERA Script 12: leakage-conscious, read-only ML data preparation.

Seven phases: eligible population -> spatial split -> feature screening ->
engineering -> feature sets -> unfitted preprocessing pipelines -> validation.

This script does NOT fit any scaler, imputer, encoder, selector or predictive model.
Run in the configured OCEAVERA WSL environment, without CLI arguments.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/interim/pseudo_absence/presence_background_candidates.parquet"
OUT = ROOT / "data/interim/model_preparation"
EVIDENCE = ROOT / "docs/records"
DATASET = OUT / "ml_candidates.parquet"
JSON_REPORT = EVIDENCE / "2026-10-16-feature-preprocessing-summary.json"
MD_REPORT = EVIDENCE / "2026-10-16-feature-preprocessing-report.md"
FEATURE_LOG = EVIDENCE / "2026-10-16-preprocessing-feature-log.md"
INTEGRATION_REPORT = EVIDENCE / "2026-10-16-integration-final-technical-report.json"
CONSTRUCTION_REPORT = EVIDENCE / "2026-10-16-full-population-presence-background-construction.json"
FEATURE_SET_MANIFEST = OUT / "feature_set_manifest.json"
SEED = 20261016
BLOCK_DEGREES = 0.5
OPTIONAL_MIN_TRAINING_COVERAGE = 0.80
EXPECTED_SOURCE_SHA256 = "234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f"

TARGET = "presence_background_label"
TAXON = "target_taxon_key"
PERIOD = "analysis_period"
GRID = "grid_cell_id"
CENTER_LAT = "raster_cell_center_latitude"
CENTER_LON = "raster_cell_center_longitude"
CORE = [
    "bio_oracle__thetao_mean__depthsurf",  # sea temperature (degree C)
    "bio_oracle__so_mean__depthsurf",     # salinity
    "bio_oracle__o2_mean__depthsurf",     # dissolved oxygen (confirm source units)
    "bio_oracle__chl_mean__depthsurf",    # chlorophyll
    "bio_oracle__ph_mean__depthsurf",     # pH
    "bio_oracle__bathymetry_mean__benthic",  # depth is negative offshore
]
# A small, domain-specified optional expansion. Verify availability from the source.
OPTIONAL = [
    "bio_oracle__no3_mean__depthsurf",
    "bio_oracle__po4_mean__depthsurf",
    "bio_oracle__slope__benthic",
    "bio_oracle__silicate_mean__depthsurf",
    "bio_oracle__sio4_mean__depthsurf",
    "bio_oracle__pp_mean__depthsurf",
    "bio_oracle__mlotst_mean__depthsurf",
]
ENG_DEPTH = "eng_water_depth_m"
ENG_LOG_DEPTH = "eng_log1p_water_depth"
ENG_TEMP_SAL = "eng_temperature_salinity_interaction"
NEW_FEATURES = [ENG_DEPTH, ENG_LOG_DEPTH, ENG_TEMP_SAL]
PERIOD_TO_SOURCE_SLICE = {
    "2000-2009": "baseline_2000",
    "2010-2019": "baseline_2010",
    "2020-2026": "ssp245_2020",
}


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def numeric(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan)


def validate_source(df: gpd.GeoDataFrame) -> list[str]:
    expected = [TARGET, TAXON, PERIOD, GRID, CENTER_LAT, CENTER_LON,
                "sample_id", "integration_source_row", "paired_presence_source_row",
                "eligible_species_level_ml", "ml_eligibility_reason", "sample_type", *CORE]
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(f"Required input columns missing: {sorted(missing)}")
    environmental = sorted(c for c in df.columns if c.startswith("bio_oracle__"))
    if df.shape != (4706, 527) or len(environmental) != 382:
        raise ValueError(f"Unexpected accepted input schema: {df.shape}, env={len(environmental)}")
    nonnumeric = [column for column in environmental
                  if not pd.api.types.is_numeric_dtype(df[column].dtype)]
    if nonnumeric:
        raise ValueError(f"Environmental source columns must be numeric: {nonnumeric}")
    if df.crs is None or df.crs.to_epsg() != 4326:
        raise ValueError("Only EPSG:4326 source accepted")
    if not df.geometry.notna().all() or not df.geometry.is_valid.all() or not df.geometry.geom_type.eq("Point").all():
        raise ValueError("Input has missing/invalid/non-Point geometries")
    if not df["sample_id"].is_unique or df[TARGET].value_counts().to_dict() != {1: 2353, 0: 2353}:
        raise ValueError("Incorrect source ID uniqueness or binary labels")
    if df.loc[df[TARGET].eq(0), "integration_source_row"].notna().any():
        raise ValueError("Synthetic backgrounds must not inherit source observation IDs")
    return environmental


def load_quarantine_map() -> dict[str, list[str]]:
    """Read the accepted integration audit's authoritative period quarantines."""
    report = json.loads(INTEGRATION_REPORT.read_text(encoding="utf-8"))
    raw = report.get("quarantined_columns_and_periods", {})
    if not isinstance(raw, dict):
        raise ValueError("Integration quarantine manifest is not a mapping")
    return {str(feature): [str(period) for period in periods]
            for feature, periods in raw.items()}


def load_quarantine_reasons() -> dict[tuple[str, str], str]:
    """Load the recorded scientific reason for each quarantined feature-period."""
    report = json.loads(CONSTRUCTION_REPORT.read_text(encoding="utf-8"))
    entries = report.get("environmental_coverage", {}).get("quarantines", [])
    reasons = {(str(item["feature"]), str(item["period"])): str(item["reason"])
               for item in entries}
    if not reasons:
        raise ValueError("No scientific quarantine reasons found in the accepted D-056 report")
    return reasons


def audit_quarantines(
    df: gpd.GeoDataFrame,
    quarantine_map: dict[str, list[str]],
    quarantine_reasons: dict[tuple[str, str], str],
) -> dict:
    """Confirm quarantined source feature-period values remain null."""
    audits = []
    for feature, source_periods in sorted(quarantine_map.items()):
        if feature not in df.columns:
            raise ValueError(f"Quarantined source feature is missing: {feature}")
        for source_period in source_periods:
            matching_periods = [period for period, slice_name in PERIOD_TO_SOURCE_SLICE.items()
                                if slice_name == source_period]
            if not matching_periods:
                raise ValueError(f"Unmapped quarantined source period: {source_period}")
            rows = df.loc[df[PERIOD].isin(matching_periods)]
            nonnull = int(numeric(rows, feature).notna().sum())
            audits.append({"feature": feature, "source_period": source_period,
                           "analysis_periods": matching_periods,
                           "rows_checked": int(len(rows)),
                           "nonnull_values_in_quarantine": nonnull,
                           "reason": quarantine_reasons.get((feature, source_period),
                                                            "Reason not found in D-056 report")})
    violations = [item for item in audits if item["nonnull_values_in_quarantine"]]
    missing_reasons = [item for item in audits if item["reason"] == "Reason not found in D-056 report"]
    if violations:
        raise ValueError(f"Quarantined source values are unexpectedly populated: {violations}")
    if missing_reasons:
        raise ValueError(f"Scientific quarantine reason is missing from D-056 report: {missing_reasons}")
    return {"quarantined_features": len(quarantine_map),
            "quarantined_feature_periods": len(audits),
            "all_quarantined_values_null": True, "checks": audits}


def build_eligible_pairs(df: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """Keep one source representative per taxon/cell/period and its background.

    All 4,706 original rows stay frozen in SOURCE. The representatives are a
    derived modelling view only, not deletion of ecological records.
    """
    eligible = df.loc[df["eligible_species_level_ml"].fillna(False).astype(bool)].copy()
    positive = eligible.loc[eligible[TARGET].eq(1)].copy()
    background = eligible.loc[eligible[TARGET].eq(0)].copy()
    assert len(positive) == len(background) == 1729, "Unexpected preliminary eligible cohort"
    positive["integration_source_row"] = numeric(positive, "integration_source_row")
    if positive["integration_source_row"].isna().any():
        raise ValueError("Eligible positive lost its source row identity")
    positive.sort_values("integration_source_row", kind="stable", inplace=True)
    # Same taxon, raster cell and period share identical extracted environmental
    # profiles: repetitions do not add independent training support.
    dedup_keys = [TAXON, GRID, PERIOD]
    selected = positive.drop_duplicates(dedup_keys, keep="first")
    ids = selected["integration_source_row"].to_list()
    match = background.set_index("paired_presence_source_row")
    if not match.index.is_unique:
        raise ValueError("Eligible paired backgrounds do not have unique source-presence identifiers")
    if not set(ids).issubset(match.index):
        raise ValueError("Unable to find paired background for a selected positive")
    chosen_bg = match.loc[ids].reset_index(drop=False)
    result = gpd.GeoDataFrame(
        pd.concat([selected, chosen_bg], ignore_index=True),
        geometry="geometry", crs="EPSG:4326",
    )
    if len(result) != 2 * len(selected) or result[TARGET].value_counts().nunique() != 1:
        raise AssertionError("Deduplication produced an unbalanced cohort")
    if len(background) - len(chosen_bg) != len(positive) - len(selected):
        raise AssertionError("Positive and paired-background repeat counts do not reconcile")
    if not result["sample_id"].is_unique:
        raise AssertionError("Selected samples are duplicated")
    ineligible = df.loc[~df["eligible_species_level_ml"].fillna(False).astype(bool)]
    reason_counts_by_label: dict[str, dict[str, int]] = {}
    for label, excluded in ineligible.groupby(TARGET, dropna=False):
        reason_counts: dict[str, int] = {}
        for value in excluded["ml_eligibility_reason"].dropna().astype(str):
            for reason in (part.strip() for part in value.split(";")):
                if reason:
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
        reason_counts_by_label[str(label)] = reason_counts
    repeated_groups = positive.groupby(dedup_keys, dropna=False).size()
    report = {
        "source_rows": len(df), "eligible_input_rows": len(eligible),
        "excluded_rows_before_eligibility": int(len(df) - len(eligible)),
        "excluded_positive_rows_before_eligibility": int(ineligible[TARGET].eq(1).sum()),
        "excluded_background_rows_before_eligibility": int(ineligible[TARGET].eq(0).sum()),
        "excluded_distinct_taxa_by_label": {
            str(label): int(rows[TAXON].nunique(dropna=True))
            for label, rows in ineligible.groupby(TARGET, dropna=False)
        },
        "eligible_distinct_taxa_by_label": {
            str(label): int(rows[TAXON].nunique(dropna=True))
            for label, rows in eligible.groupby(TARGET, dropna=False)
        },
        "ineligible_reason_counts_by_label_nonexclusive": reason_counts_by_label,
        "eligible_source_presences": len(positive),
        "eligible_paired_backgrounds": len(background),
        "eligible_taxa_before_deduplication": int(positive[TAXON].nunique()),
        "positive_rows_after_taxon_cell_period_dedup": len(selected),
        "positive_repeats_omitted_from_derived_view": len(positive) - len(selected),
        "paired_background_rows_omitted_due_to_positive_dedup": len(background) - len(chosen_bg),
        "repeated_taxon_cell_period_groups": int((repeated_groups > 1).sum()),
        "balanced_candidate_rows": len(result),
        "candidate_presence_rows": int(result[TARGET].eq(1).sum()),
        "candidate_background_rows": int(result[TARGET].eq(0).sum()),
        "selected_taxon_keys": int(selected[TAXON].nunique()),
        "distinct_positive_cells": int(selected[GRID].nunique()),
    }
    return result, report


def add_engineered_features(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Deterministic, unit-aware transformations; no fit/statistics learned."""
    frame = df.copy()
    bathy = numeric(frame, CORE[-1])
    temp = numeric(frame, CORE[0]); sal = numeric(frame, CORE[1])
    # Negative bathymetry represents sea-floor depth below the surface. Valid
    # coastline/zero-depth cells remain 0; missing values remain missing.
    frame[ENG_DEPTH] = (-bathy).clip(lower=0)
    frame[ENG_LOG_DEPTH] = np.log1p(frame[ENG_DEPTH])
    # Exploratory interaction; avoid interpreting as a physical state equation.
    frame[ENG_TEMP_SAL] = temp * sal
    for name in NEW_FEATURES:
        if np.isinf(pd.to_numeric(frame[name], errors="coerce")).any():
            raise AssertionError(f"Engineered infinity in {name}")
    return frame


def add_spatial_blocks(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Group ALL taxa/periods by the grid-cell centre, not noisy OBIS points."""
    frame = df.copy()
    lat = numeric(frame, CENTER_LAT); lon = numeric(frame, CENTER_LON)
    if lat.isna().any() or lon.isna().any():
        raise ValueError("Cannot assign spatial blocks without raster centres")
    bx = np.floor(lon.to_numpy(float) / BLOCK_DEGREES).astype(int)
    by = np.floor(lat.to_numpy(float) / BLOCK_DEGREES).astype(int)
    frame["spatial_block_id"] = [f"lon{x}_lat{y}" for x, y in zip(bx, by)]
    # Same grid cell may recur for several taxa and periods; it MUST have one block.
    if frame.groupby(GRID)["spatial_block_id"].nunique().max() != 1:
        raise AssertionError("Same Bio-ORACLE cell assigned conflicting spatial groups")
    return frame


def split_spatial_blocks(df: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """Spatially hold out ~15% test and ~15% validation blocks, globally.

    Test/validation assignment is determined without using environmental values
    or predictive modelling. A small search checks representation of both labels.
    """
    labels = df[TARGET].astype(int).to_numpy()
    groups = df["spatial_block_id"].to_numpy()
    if len(np.unique(groups)) < 8:
        raise ValueError("Too few distinct spatial groups for three-way spatial validation")
    X_dummy = np.zeros((len(df), 1), dtype=np.int8)
    best = None
    for trial in range(30):
        random_seed = SEED + trial
        first = GroupShuffleSplit(n_splits=1, test_size=.15, random_state=random_seed)
        rest_i, test_i = next(first.split(X_dummy, labels, groups=groups))
        second = GroupShuffleSplit(n_splits=1, test_size=.15/.85, random_state=random_seed + 1000)
        train_rel, valid_rel = next(second.split(X_dummy[rest_i], labels[rest_i], groups=groups[rest_i]))
        train_i, valid_i = rest_i[train_rel], rest_i[valid_rel]
        chunks = (train_i, valid_i, test_i)
        if any(len(chunk) == 0 or len(set(labels[chunk])) != 2 for chunk in chunks):
            continue
        fractions = np.asarray([len(i) / len(df) for i in chunks])
        class_props = np.asarray([labels[i].mean() for i in chunks])
        score = float(np.abs(fractions - [.7, .15, .15]).sum() +
                      .5 * np.abs(class_props - .5).sum())
        if best is None or score < best[0]:
            best = (score, random_seed, chunks)
    if best is None:
        raise ValueError("No three-way spatial split has both labels in all partitions")
    _, seed, (train_i, val_i, test_i) = best
    result = df.copy()
    result["split"] = "unassigned"
    # Positional array assignment, not index-label assignment.
    col = result.columns.get_loc("split")
    for name, rows in [("train", train_i), ("validation", val_i), ("test", test_i)]:
        result.iloc[rows, col] = name
    if (result["split"] == "unassigned").any():
        raise AssertionError("Unassigned split rows")
    cell_overlap = 0
    block_overlap = 0
    parts = [set(result.loc[result["split"].eq(name), GRID]) for name in ("train", "validation", "test")]
    blocks = [set(result.loc[result["split"].eq(name), "spatial_block_id"]) for name in ("train", "validation", "test")]
    for a in range(3):
        for b in range(a+1, 3):
            cell_overlap += len(parts[a] & parts[b])
            block_overlap += len(blocks[a] & blocks[b])
    if cell_overlap or block_overlap:
        raise AssertionError("Spatial leakage between partitions")
    matrix = result.groupby(["split", TARGET]).size().unstack(fill_value=0)
    split_sizes = {}
    for name in ("train", "validation", "test"):
        piece = result.loc[result["split"].eq(name)]
        positives = piece.loc[piece[TARGET].eq(1)]
        split_sizes[name] = {
            "rows": int(len(piece)), "row_fraction": float(len(piece) / len(result)),
            "presence_rows": int(piece[TARGET].eq(1).sum()),
            "background_rows": int(piece[TARGET].eq(0).sum()),
            "distinct_grid_cells": int(piece[GRID].nunique()),
            "distinct_spatial_blocks": int(piece["spatial_block_id"].nunique()),
            "taxon_keys": int(piece[TAXON].nunique()),
            "positive_taxon_keys": int(positives[TAXON].nunique()),
            "positive_distinct_cells": int(positives[GRID].nunique()),
        }
    train_taxa = set(result.loc[(result["split"] == "train") & (result[TARGET] == 1), TAXON])
    unseen = result.loc[(result["split"] != "train") & (result[TARGET] == 1) &
                        (~result[TAXON].isin(train_taxa))]
    pair_audit = {"verified": False, "pairs": 0, "same_partition": 0,
                  "cross_partition": 0}
    if {"integration_source_row", "paired_presence_source_row"}.issubset(result.columns):
        source_rows = numeric(result.loc[result[TARGET].eq(1)], "integration_source_row")
        if source_rows.isna().any() or source_rows.duplicated().any():
            raise ValueError("Eligible positive source-row identifiers are missing or duplicated")
        positive_splits = pd.Series(
            result.loc[result[TARGET].eq(1), "split"].to_numpy(), index=source_rows.to_numpy())
        paired = result.loc[result[TARGET].eq(0)]
        pair_ids = numeric(paired, "paired_presence_source_row")
        partner_splits = pair_ids.map(positive_splits)
        if pair_ids.isna().any() or partner_splits.isna().any() or pair_ids.duplicated().any():
            raise ValueError("Candidate background-to-presence pairing is incomplete or duplicated")
        pair_audit = {
            "verified": True, "pairs": int(len(paired)),
            "same_partition": int(partner_splits.eq(paired["split"].to_numpy()).sum()),
            "cross_partition": int(partner_splits.ne(paired["split"].to_numpy()).sum()),
        }
    return result, {"selected_seed": seed, "candidate_seed_count": 30,
                    "block_degrees": BLOCK_DEGREES, "split_sizes": split_sizes,
                    "split_class_counts": {str(k): {str(j): int(v) for j, v in s.items()}
                                           for k, s in matrix.to_dict(orient="index").items()},
                    "positive_rows_for_taxa_unseen_in_training": int(len(unseen)),
                    "positive_taxon_keys_unseen_in_training": int(unseen[TAXON].nunique()),
                    "cross_split_cell_overlap": cell_overlap,
                    "cross_split_spatial_block_overlap": block_overlap,
                    "paired_background_split_audit": pair_audit}


def make_feature_sets(
    df: gpd.GeoDataFrame,
    quarantine_map: dict[str, list[str]] | None = None,
) -> tuple[dict[str, list[str]], dict]:
    """Domain feature proposals; check optional availability from TRAIN only."""
    quarantine_map = quarantine_map or {}
    train = df.loc[df["split"].eq("train")]
    domain_expand = []
    rejected = {}
    for column in OPTIONAL:
        if column not in df.columns:
            rejected[column] = "source column unavailable"
            continue
        if column in quarantine_map:
            rejected[column] = "source quarantined in: " + ", ".join(quarantine_map[column])
            continue
        coverage = float(numeric(train, column).notna().mean())
        if coverage < OPTIONAL_MIN_TRAINING_COVERAGE or numeric(train, column).nunique(dropna=True) <= 1:
            rejected[column] = (f"training coverage {coverage:.2%} below "
                                f"{OPTIONAL_MIN_TRAINING_COVERAGE:.0%}, or constant")
            continue
        domain_expand.append(column)
    core = list(CORE)
    # The second configuration tests all six core predictors plus every
    # engineered feature; raw positive depth and log depth are distinct.
    engineered = list(dict.fromkeys(core + NEW_FEATURES))
    expanded = list(dict.fromkeys(engineered + domain_expand))
    return {
        "core_six": core,
        "core_plus_engineered": engineered,
        "domain_expanded": expanded,
    }, {"optional_columns_admitted_from_training_only": domain_expand,
        "optional_columns_rejected": rejected,
        "optional_min_training_coverage": OPTIONAL_MIN_TRAINING_COVERAGE,
        "quarantined_columns_and_periods": quarantine_map,
        "excluded_sources": ["sample_id", "integration_source_row", "paired_presence_source_row",
                             "originalOccurrenceID", "eventDate", "geometry", "latitude", "longitude",
                             CENTER_LAT, CENTER_LON, "grid_cell_id", "raster_cell_id", "spatial_block_id",
                             "split", TARGET, PERIOD, "eligible_species_level_ml", "ml_eligibility_reason",
                             "sample_type", "coordinateUncertaintyInMeters", "environmental_coverage_status"],
        "categorical_conditioning_feature": TAXON,
        "categorical_feature_role": "Retained separately for the shared multi-species model; not included in numeric feature-set lists."}


def build_preprocessor(feature_names: list[str], scaled: bool) -> ColumnTransformer:
    """Return an UNFITTED sklearn pipeline for later fit on training folds only."""
    numeric_steps = [("imputer", SimpleImputer(strategy="median", add_indicator=False,
                                                keep_empty_features=True))]
    if scaled:
        numeric_steps.append(("standard_scaler", StandardScaler()))
    return ColumnTransformer(
        transformers=[
            ("numerical", Pipeline(numeric_steps), feature_names),
            ("species", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [TAXON]),
        ],
        remainder="drop", sparse_threshold=0,
        verbose_feature_names_out=True,
    )


def support_table(df: gpd.GeoDataFrame) -> pd.DataFrame:
    positives = df.loc[df[TARGET].eq(1)]
    grp = positives.groupby(TAXON, dropna=False).agg(
        positive_cell_periods=("sample_id", "size"),
        positive_distinct_cells=(GRID, "nunique"),
        positive_distinct_spatial_blocks=("spatial_block_id", "nunique"),
    ).reset_index()
    for split in ["train", "validation", "test"]:
        tmp = positives.loc[positives["split"].eq(split)].groupby(TAXON).agg(
            **{f"{split}_positive_rows": ("sample_id", "size"),
               f"{split}_positive_cells": (GRID, "nunique")}
        ).reset_index()
        grp = grp.merge(tmp, how="left", on=TAXON, validate="1:1")
    for col in grp.select_dtypes(include="number"):
        grp[col] = grp[col].fillna(0).astype(int)
    grp["spatial_evaluation_supported_provisionally"] = (
        (grp["train_positive_cells"] >= 3) &
        (grp["validation_positive_cells"] >= 1) &
        (grp["test_positive_cells"] >= 1)
    )
    return grp.sort_values(["positive_distinct_cells", TAXON], ascending=[False, True])


def run() -> dict:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    original_hash = checksum(SOURCE)
    if original_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError("Source input is NOT the frozen accepted D-056 dataset")
    data = gpd.read_parquet(SOURCE)
    source_features = validate_source(data)
    quarantine_map = load_quarantine_map()
    quarantine_reasons = load_quarantine_reasons()
    quarantine_report = audit_quarantines(data, quarantine_map, quarantine_reasons)
    # Phase 1: eligibility + one source record per taxon/grid/period.
    candidates, population_report = build_eligible_pairs(data)
    # Phase 4 is deterministic and may be computed before splitting, as it learns nothing.
    candidates = add_engineered_features(candidates)
    # Phase 2: spatial blocks and three-way holdouts.
    candidates = add_spatial_blocks(candidates)
    candidates, split_report = split_spatial_blocks(candidates)
    # Phase 3/5: domain features plus availability screen ONLY on TRAIN.
    feature_sets, feature_report = make_feature_sets(candidates, quarantine_map)
    # Screen every original environmental column on training data only.
    train = candidates.loc[candidates["split"] == "train"]
    proposed = set(sum(feature_sets.values(), []))
    admitted = set(feature_report["optional_columns_admitted_from_training_only"])
    core_features = set(CORE)
    def screening_decision(column: str) -> str:
        if column in core_features:
            return "prespecified core feature"
        if column in quarantine_map:
            return "source quarantine; excluded from optional candidates"
        if column in admitted:
            return "admitted to domain-expanded hypothesis from training-only screening"
        if column in feature_report["optional_columns_rejected"]:
            return feature_report["optional_columns_rejected"][column]
        return "not in the prespecified core or optional candidate list"

    feature_coverage = pd.DataFrame([
        {"feature": column,
         "train_present_count": int(numeric(train, column).notna().sum()),
         "train_missing_count": int(numeric(train, column).isna().sum()),
         "train_present_fraction": float(numeric(train, column).notna().mean()),
         "train_distinct_finite": int(numeric(train, column).nunique(dropna=True)),
         "all_null_in_training": bool(numeric(train, column).notna().sum() == 0),
         "constant_in_training": bool(numeric(train, column).nunique(dropna=True) <= 1),
         "source_quarantined_periods": ", ".join(quarantine_map.get(column, [])),
         "role": "core predictor" if column in core_features else
                 "optional candidate" if column in OPTIONAL else "source Bio-ORACLE",
         "in_any_proposed_feature_set": column in proposed,
         "admitted_to_domain_expanded_set": column in admitted,
         "screening_decision": screening_decision(column),
         "screen_scope": "train partition only"}
        for column in source_features
    ])
    # Phase 6: serialise only UNFITTED transformers (no .fit/.fit_transform calls).
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    saved_pipelines = {}
    for set_name, features in feature_sets.items():
        for mode, scaled in [("tree", False), ("scaled", True)]:
            pipe = build_preprocessor(features, scaled=scaled)
            if hasattr(pipe, "transformers_"):
                raise AssertionError("No transformer may be fitted during this stage")
            dst = OUT / f"unfitted_{set_name}_{mode}_preprocessor.joblib"
            joblib.dump(pipe, dst)
            check = joblib.load(dst)
            if hasattr(check, "transformers_"):
                raise AssertionError("Serialized pipeline unexpectedly fitted")
            saved_pipelines[f"{set_name}_{mode}"] = {"path": dst.relative_to(ROOT).as_posix(),
                                                     "sha256": checksum(dst)}
    feature_manifest = {
        "status": "provisional feature configurations; no final selection approved",
        "source_feature_count": len(source_features),
        "feature_sets": feature_sets,
        "categorical_conditioning_feature": TAXON,
        "preprocessing_configurations": list(saved_pipelines),
        "screening_scope": ("Optional environmental coverage and variation were measured on training rows only; "
                            f"minimum coverage={OPTIONAL_MIN_TRAINING_COVERAGE:.0%}, nonconstant required."),
        "scientific_quarantines": quarantine_report,
        "excluded_predictor_fields": feature_report["excluded_sources"],
        "optional_candidates": {
            "admitted": feature_report["optional_columns_admitted_from_training_only"],
            "rejected": feature_report["optional_columns_rejected"],
        },
        "note": "All 382 source environmental fields remain in the frozen source dataset; this manifest describes only the new candidate view.",
    }
    FEATURE_SET_MANIFEST.write_text(json.dumps(feature_manifest, indent=2) + "\n", encoding="utf-8")
    # Keep only useful, auditable modelling columns in this NEW GeoParquet.
    columns = ["sample_id", "integration_source_row", "paired_presence_source_row", "sample_type", TARGET, TAXON, PERIOD,
               GRID, CENTER_LAT, CENTER_LON, "spatial_block_id", "split",
               "geometry", *CORE, *NEW_FEATURES, *feature_report["optional_columns_admitted_from_training_only"]]
    columns = list(dict.fromkeys(columns))
    publish = gpd.GeoDataFrame(candidates[columns].copy(), geometry="geometry", crs="EPSG:4326")
    class_counts = publish[TARGET].value_counts()
    if set(class_counts.index) != {0, 1} or class_counts.nunique() != 1:
        raise AssertionError("Derived population class balance lost")
    positive_rows = publish.loc[publish[TARGET].eq(1)]
    background_rows = publish.loc[publish[TARGET].eq(0)]
    positive_sources = numeric(positive_rows, "integration_source_row")
    paired_sources = numeric(background_rows, "paired_presence_source_row")
    if positive_sources.isna().any() or positive_sources.duplicated().any():
        raise AssertionError("Published positives lost unique OBIS source-row lineage")
    if (paired_sources.isna().any() or paired_sources.duplicated().any()
            or not set(paired_sources).issubset(set(positive_sources))):
        raise AssertionError("Published backgrounds lost unique paired-presence lineage")
    if positive_rows.duplicated([TAXON, GRID, PERIOD]).any():
        raise AssertionError("Published positives repeat a taxon/cell/period combination")
    pending = DATASET.with_name(".ml_candidates.pending.parquet")
    try:
        publish.to_parquet(pending, index=False, compression="zstd",
                           geometry_encoding="WKB", schema_version="1.1.0")
        reread = gpd.read_parquet(pending)
        if (reread.shape != publish.shape or list(reread.columns) != list(publish.columns)
                or reread.crs.to_epsg() != 4326):
            raise AssertionError("Model candidate GeoParquet readback failed")
        if not reread["sample_id"].equals(publish["sample_id"]):
            raise AssertionError("Source sample lineage changed at readback")
        if not reread.geometry.geom_equals(publish.geometry).all():
            raise AssertionError("GeoParquet geometry changed at readback")
        if (not reread[TARGET].equals(publish[TARGET])
                or set(reread[TARGET].unique()) != {0, 1}
                or not reread["integration_source_row"].equals(publish["integration_source_row"])
                or not reread["paired_presence_source_row"].equals(publish["paired_presence_source_row"])):
            raise AssertionError("GeoParquet target or occurrence-pair lineage changed at readback")
        pending.replace(DATASET)
    finally:
        pending.unlink(missing_ok=True)
    # Phase 7: evidence, invariants, source fingerprints.
    if checksum(SOURCE) != original_hash:
        raise AssertionError("Frozen source modified during preparation")
    support = support_table(candidates)
    support.to_csv(OUT / "taxon_spatial_support.csv", index=False)
    feature_coverage.to_csv(OUT / "feature_screen_train_only.csv", index=False)
    parquet_metadata = pq.read_metadata(DATASET)
    geo_metadata = json.loads(parquet_metadata.metadata[b"geo"].decode("utf-8"))
    candidate_feature_quality = {}
    selected_numeric_features = list(dict.fromkeys(
        [*CORE, *NEW_FEATURES, *feature_report["optional_columns_admitted_from_training_only"]]))
    for feature in selected_numeric_features:
        values = numeric(publish, feature)
        candidate_feature_quality[feature] = {
            "rows": int(len(values)),
            "missing": int(values.isna().sum()),
            "finite_nonmissing": int(values.notna().sum()),
            "zero_values": int(values.eq(0).sum()),
            "minimum": None if values.notna().sum() == 0 else float(values.min()),
            "maximum": None if values.notna().sum() == 0 else float(values.max()),
        }
    versions = {}
    for package in ["numpy", "pandas", "geopandas", "pyarrow", "scikit-learn",
                    "scipy", "joblib", "narwhals", "threadpoolctl"]:
        versions[package] = importlib.metadata.version(package)
    report = {
        "status": "prepared candidates and UNFITTED pipelines; ecological/model approval pending",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), **versions},
        "input": {"path": SOURCE.relative_to(ROOT).as_posix(),
                  "rows": len(data), "columns": len(data.columns),
                  "bytes": SOURCE.stat().st_size,
                  "sha256_before_after": [original_hash, checksum(SOURCE)]},
        "population": population_report,
        "spatial_split": split_report,
        "source_quarantine_audit": quarantine_report,
        "engineering": {
            ENG_DEPTH: "max(0, -bathymetry_mean); do not replace null",
            ENG_LOG_DEPTH: "log1p(eng_water_depth_m)",
            ENG_TEMP_SAL: "temperature_celsius * salinity_psu; exploratory, not a physical state equation",
        },
        "original_environment_features": len(source_features),
        "training_feature_screen": {
            "path": (OUT / "feature_screen_train_only.csv").relative_to(ROOT).as_posix(),
            "features_screened": int(len(feature_coverage)),
            "all_null_in_training": feature_coverage.loc[feature_coverage["all_null_in_training"], "feature"].tolist(),
            "constant_in_training": feature_coverage.loc[feature_coverage["constant_in_training"], "feature"].tolist(),
            "quarantined_columns": sorted(quarantine_map),
        },
        "feature_sets": feature_sets,
        "feature_set_manifest": FEATURE_SET_MANIFEST.relative_to(ROOT).as_posix(),
        "feature_screening": feature_report,
        "candidate_feature_quality": candidate_feature_quality,
        "unfitted_transformers": saved_pipelines,
        "taxon_support": {"taxa": len(support),
                          "taxa_with_provisional_support_in_all_splits": int(support["spatial_evaluation_supported_provisionally"].sum())},
        "output": {"path": DATASET.relative_to(ROOT).as_posix(),
                   "rows": len(publish), "columns": len(publish.columns),
                   "bytes": DATASET.stat().st_size,
                   "sha256": checksum(DATASET),
                   "crs": str(reread.crs),
                   "geometry_types": sorted(reread.geometry.geom_type.unique().tolist()),
                   "geoparquet_version": geo_metadata.get("version"),
                   "compression": sorted({
                       parquet_metadata.row_group(group).column(column).compression
                       for group in range(parquet_metadata.num_row_groups)
                       for column in range(parquet_metadata.row_group(group).num_columns)
                   })},
        "limitations": [
            "One-to-one pseudo-backgrounds are NOT confirmed biological absences.",
            "SSP245 2020 projection is used as an assumption for 2020–2026 occurrences.",
            "Global background sampling is biased toward deep offshore cells; interpret scores carefully.",
            "Source-cell repeat observations are reduced only in derived modelling candidates.",
            "Spatial blocks prevent shared-cell leakage but do not fully remove spatial autocorrelation.",
            "Background/positive pairing links may cross geographic blocks; pair source IDs are never predictors.",
            "Many rare taxa are not independently supported across all splits; review support CSV.",
            "Unseen validation/test taxon categories receive all-zero one-hot encoding; do not evaluate unseen taxa as established suitability models.",
            "One-hot species identity and all environment variables must be supplied consistently at inference.",
            "No imputers, scalers, encoders, selectors or models have been fitted. Fit training-only inside each validation fold.",
            "No final ecological feature or species selection and no source data mutation occurred.",
        ],
    }
    JSON_REPORT.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    split_table = "\n".join(
        f"| {name} | {stats['rows']:,} | {stats['row_fraction']:.1%} | "
        f"{stats['presence_rows']:,} | {stats['background_rows']:,} | "
        f"{stats['positive_taxon_keys']:,} | {stats['positive_distinct_cells']:,} | "
        f"{stats['distinct_spatial_blocks']:,} |"
        for name, stats in split_report["split_sizes"].items())
    taxon_exclusion_lines = []
    for label, reason_counts in sorted(population_report["ineligible_reason_counts_by_label_nonexclusive"].items()):
        for reason, count in sorted(reason_counts.items()):
            taxon_exclusion_lines.append(f"| {label} | {reason} | {count:,} |")
    exclusion_table = "\n".join(taxon_exclusion_lines) or "| — | None | 0 |"
    taxon_eligibility_table = "\n".join(
        f"| {label} | {population_report['eligible_distinct_taxa_by_label'].get(label, 0):,} | "
        f"{population_report['excluded_distinct_taxa_by_label'].get(label, 0):,} |"
        for label in sorted(set(population_report["eligible_distinct_taxa_by_label"]) |
                            set(population_report["excluded_distinct_taxa_by_label"])))
    feature_set_table = "\n".join(
        f"| {name} | {len(features)} | `{', '.join(features)}` |"
        for name, features in feature_sets.items())
    quality_table = "\n".join(
        f"| `{feature}` | {stats['missing']:,} | {stats['zero_values']:,} | "
        f"{stats['minimum'] if stats['minimum'] is not None else '—'} | "
        f"{stats['maximum'] if stats['maximum'] is not None else '—'} |"
        for feature, stats in candidate_feature_quality.items())
    all_null = report["training_feature_screen"]["all_null_in_training"]
    MD_REPORT.write_text(
        "# OCEAVERA — Feature Selection, Engineering and Preprocessing\n\n"
        "**Status:** provisional candidates for review; no species, target, feature set or model is approved.\n\n"
        f"Frozen source: `{SOURCE.relative_to(ROOT)}` — {len(data):,} × {len(data.columns)}, "
        f"SHA-256 `{original_hash}`. The source remains unchanged.\n\n"
        f"Derived GeoParquet: `{DATASET.relative_to(ROOT)}` — **{publish.shape[0]:,} × {publish.shape[1]}**, "
        f"{DATASET.stat().st_size:,} bytes, SHA-256 `{checksum(DATASET)}`; "
        f"GeoParquet {geo_metadata.get('version')}, EPSG:4326, ZSTD.\n\n"
        "## Population and repeats\n\n"
        f"The {population_report['eligible_source_presences']:,} eligible positive observations are paired with "
        f"{population_report['eligible_paired_backgrounds']:,} existing background rows. "
        f"Eligibility excludes {population_report['excluded_positive_rows_before_eligibility']:,} positive and "
        f"{population_report['excluded_background_rows_before_eligibility']:,} paired background rows. "
        f"Deduplication retains {population_report['positive_rows_after_taxon_cell_period_dedup']:,} positives and "
        f"{population_report['positive_repeats_omitted_from_derived_view']:,} fewer repeated taxon/cell/period positives, "
        f"plus their matched backgrounds, yielding {publish.shape[0]:,} rows. These are records, not independent cells.\n\n"
        "Exclusion reasons below are nonexclusive: a row with multiple eligibility reasons contributes to each reason count.\n\n"
        "| Label | Exclusion reason | Rows |\n|---:|---|---:|\n" + exclusion_table + "\n\n"
        "| Label | Eligible distinct taxa | Excluded distinct taxa |\n|---:|---:|---:|\n" +
        taxon_eligibility_table + "\n\n"
        "## Spatial split\n\n"
        f"Raster-centre blocks are {BLOCK_DEGREES}° wide; selected seed: {split_report['selected_seed']}. "
        f"Cross-partition cell overlap: {split_report['cross_split_cell_overlap']}; "
        f"block overlap: {split_report['cross_split_spatial_block_overlap']}.\n\n"
        "| Partition | Rows | Row share | Presence rows | Background rows | Positive taxa | Positive cells | Blocks |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|\n" + split_table + "\n\n"
        "## Feature configurations\n\n"
        "All 382 source Bio-ORACLE features were screened on training rows only. "
        f"All-null training features: {len(all_null)}. The source audit has "
        f"{quarantine_report['quarantined_features']} quarantined feature definitions and "
        f"{quarantine_report['quarantined_feature_periods']} feature-period entries; "
        "the associated values were confirmed null and were not admitted as predictors.\n\n"
        "| Configuration | Numeric environmental predictors | Features |\n|---|---:|---|\n" + feature_set_table +
        "\n\n`target_taxon_key` is a separate categorical condition for the shared multi-species model. "
        "It is not included in numeric feature counts. Optional candidates were admitted using training coverage only.\n\n"
        "## Candidate feature missingness and ranges\n\n"
        "Counts describe derived candidate rows before imputation. Zero is a valid value; missing values remain missing.\n\n"
        "| Predictor | Missing rows | Exact zeros | Minimum | Maximum |\n|---|---:|---:|---:|---:|\n" +
        quality_table + "\n\n"
        "## Engineering and preprocessing\n\n"
        f"- `{ENG_DEPTH}` = `max(0, -bathymetry)`; source nulls stay null and zero depth remains valid.\n"
        f"- `{ENG_LOG_DEPTH}` = `log1p({ENG_DEPTH})`.\n"
        f"- `{ENG_TEMP_SAL}` = temperature × salinity; exploratory interaction only.\n"
        "- Six `ColumnTransformer` templates were serialized and reloaded without fitting: median imputation, "
        "optional `StandardScaler`, and `OneHotEncoder(handle_unknown='ignore')` for species.\n\n"
        "## Limitations\n\n" + "\n".join(f"- {p}" for p in report["limitations"]) + "\n",
        encoding="utf-8")
    feature_log_rows = [
        ("Source and target", "Use frozen D-056 source; label 1 is observed presence and 0 is sampled background.",
         "EDA source/hash and label dictionary", "Preserve full source; use paired eligible records.",
         "Keep the established 1:1 paired candidates", "No source rewrite; no absence claim.",
         "Lineage fields are not predictors", "Conclusions remain conditional on background sampling.",
         "2026-10-16-eda-report.md; 2026-10-16-full-population-presence-background-construction.md"),
        ("Repeated records", "Retain one positive per taxon/cell/period and its paired background.",
         f"{population_report['positive_repeats_omitted_from_derived_view']} repeated positives omitted from this view.",
         "Keep every row or reduce repeated cell-period records.", "Use one representative in this derived view.",
         "Avoid treating identical cell-period environmental profiles as independent samples.",
         "Deduplicate before spatial partitioning", "Candidate population is smaller than source occurrence population.",
         "2026-10-16-feature-preprocessing-summary.json"),
        ("Spatial validation", "Assign shared 0.5-degree raster-centre blocks to one of three partitions.",
         "No cell/block overlap; split support varies by taxon.", "Random rows or geographic blocks.",
         "Use deterministic global block groups, approximately 70/15/15.",
         "Reduce repeated-cell and local spatial leakage.", "Do not use held-out environmental values to choose features.",
         "Small and rare taxa may lack independent support.", "2026-10-16-feature-preprocessing-summary.json; taxon_spatial_support.csv"),
        ("Source quarantines and missingness", "Screen all 382 environmental fields on training rows; verify period-specific quarantines.",
         f"{quarantine_report['quarantined_features']} quarantined definitions, {quarantine_report['quarantined_feature_periods']} affected periods.",
         "Use quarantined values or exclude affected measurements.", "Require quarantined source values to remain null; do not propose quarantined optional layers.",
         "Respect unresolved source semantics; preserve all source columns.", "Coverage screening is training-only.",
         "Null values require fold-local imputation only if the feature is later approved.",
         "2026-10-16-integration-final-technical-report.json; feature_screen_train_only.csv"),
        ("Feature engineering", "Add positive water depth, log depth and temperature-by-salinity interaction.",
         "Bathymetry has a negative offshore sign; retain null and valid zero-depth values.",
         "Keep raw bathymetry or use derived transforms.", "Expose both raw core bathymetry and all three engineered features.",
         "Provide interpretable alternative representations for later comparison.",
         "Operations are deterministic and use no fitted statistics.", "No predictive benefit is established.",
         "2026-10-16-feature-preprocessing-summary.json; test_feature_preprocessing.py"),
        ("Feature configurations", "Compare core-six, core-plus-engineered and domain-expanded hypotheses.",
         "Optional layer coverage and variation are measured only on training rows.",
         "Use core predictors, add engineered predictors, or add supported optional layers.",
         "Retain three provisional schemas and species as a categorical condition.",
         "Make alternatives reproducible without finalizing selection.", "No test-driven or supervised selection.",
         "Feature list remains subject to group review and spatial support.",
         "feature_set_manifest.json; feature_screen_train_only.csv"),
        ("Preprocessing", "Store six unfitted numerical/categorical templates.",
         "Templates reload without fitted attributes.", "Fit here or save unfitted reusable pipelines.",
         "Save median imputation, optional scaling and unknown-safe one-hot encoding templates.",
         "Allow later fit within training folds.", "No transform/fit call on project data.",
         "Later validation must repeat each fit inside its fold.", "unfitted_*_preprocessor.joblib"),
        ("Model training", "No classifiers or learned preprocessing are fitted in this stage.",
         "Preparation evidence only.", "Train now or hand off to evaluation stage.",
         "Do not train models.", "Keep this stage descriptive and reproducible.",
         "Held-out partitions remain unused.", "No model performance or final model claim.",
         "2026-10-16-feature-preprocessing-report.md"),
    ]
    header = ("| Date | Field or issue | EDA evidence | Options considered | Chosen treatment | Rationale | "
              "Leakage control | Effect on evaluation | Reproduction reference |\n"
              "|---|---|---|---|---|---|---|---|---|\n")
    table = "\n".join("| 2026-10-16 | " + " | ".join(row) + " |" for row in feature_log_rows)
    FEATURE_LOG.write_text(
        "# OCEAVERA — Preprocessing and Feature Decision Log\n\n"
        "**Status:** provisional technical preparation; shared ecological and feature approval remains pending.\n\n"
        f"- **Dataset/version:** `{SOURCE.relative_to(ROOT)}` ({len(data):,} × {len(data.columns)}; "
        f"SHA-256 `{original_hash}`).\n"
        f"- **Evaluation design:** global {BLOCK_DEGREES}° raster-centre spatial blocks with train/validation/test partitions.\n"
        f"- **Derived candidate:** `{DATASET.relative_to(ROOT)}` ({publish.shape[0]:,} × {publish.shape[1]}).\n\n"
        + header + table + "\n",
        encoding="utf-8")
    print(f"[Script 12] Derived {publish.shape[0]:,} × {publish.shape[1]} GeoParquet, no models trained")
    print(f"[Script 12] Source SHA-256 unchanged: {original_hash}")
    print(f"[Script 12] Split counts: {split_report['split_class_counts']}")
    print(f"[Script 12] Files: {DATASET.relative_to(ROOT)}, {JSON_REPORT.relative_to(ROOT)}")
    return report


if __name__ == "__main__":
    run()
