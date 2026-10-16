"""OCEAVERA — EDA of the frozen full-population presence/background GeoParquet.

Run from anywhere: python src/data_preparation/11_explore_presence_background_data.py
Sections A–F generate figures, CSV tables, and an insight log. No input is edited.
This stage DOES NOT choose species, alter features, split data, or train models.
"""
from __future__ import annotations

import hashlib
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")  # Safe for WSL/headless Codex execution.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from shapely.geometry import box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/interim/pseudo_absence/presence_background_candidates.parquet"
REPORTS = ROOT / "reports/eda"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"
RECORDS = ROOT / "docs/records"
SUMMARY_JSON = RECORDS / "2026-10-16-eda-summary.json"
SUMMARY_MD = RECORDS / "2026-10-16-eda-report.md"
INSIGHTS_MD = RECORDS / "2026-10-16-eda-insight-log.md"
INTEGRATION_MANIFEST = RECORDS / "2026-10-16-integration-manifest.json"
GSHHG_ARCHIVE = ROOT / "data/raw/geography/gshhg/gshhg-shp-2.3.7.zip"
GSHHG_REFERENCE = RECORDS / "2026-10-16-gshhg-marine-reference.json"
GSHHG_METRIC_CRS = "EPSG:32644"  # Local UTM zone for Sri Lanka; used only for distance diagnostics.

# These are the frozen inputs named in the task. A mismatch stops the run before
# reports are written; the post-run pass confirms every file stayed byte-identical.
EXPECTED_SHA256 = {
    "data/interim/pseudo_absence/presence_background_candidates.parquet": "234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f",
    "data/interim/integrated/full/integrated_observations.parquet": "34e756d9fa0d5478da14b6a2d627c16076c486d8e43317363d387d69a661ee34",
    "data/interim/integrated/temporal/observations_2000_2026.parquet": "6669327ec1aba406bf8aa8346dc743d1ab721a1237c0266705119881cc21479a",
    "data/interim/integrated/marine/marine_observations.parquet": "76a2812ae4d031bc9515d15931a2a97221d584b2b24cfad7e1e2fb5e77ba1d49",
    "data/interim/integrated/gridded/grid_observations.parquet": "71fa9ff9ad959122811ef01117a2157baf0498fbcc1e93bfb340ba87d94d2fc0",
    "data/interim/integrated/gridded/species_cell_period_summary.parquet": "eb14bebd83f993894672f143f16a452470cdd1c924c390c3c061b580b8c77433",
    "src/data_preparation/08_integrate_spatiotemporal_data.py": "2e32fa62316269f876e33fb00d4320bac72d902ac71b97e2013b3a3ea444c154",
    "src/data_preparation/09_filter_and_grid_data.py": "00ba641c0ff430267825740756c3d86295b04ab651caa0cfe0aa5c3640881f10",
    "src/data_preparation/10_construct_pseudo_absences.py": "3ec6ba32d9f0dd8f615c6a0fe0be3aa42d2c9c09e5cd5fa405f08461e40a0429",
    "data/interim/geography/sri_lanka_marine_water.gpkg": "ef21fe8791b16e314a441480781f9e5e8cb2a47bf3e9030f57e6b2bc0f02ce8e",
    "data/raw/geography/gshhg/gshhg-shp-2.3.7.zip": "8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41",
}

CORE = {
    "bio_oracle__thetao_mean__depthsurf": "Ocean temperature (°C)",
    "bio_oracle__so_mean__depthsurf": "Salinity (PSU)",
    "bio_oracle__o2_mean__depthsurf": "Dissolved oxygen (source units; verify)",
    "bio_oracle__chl_mean__depthsurf": "Chlorophyll (mg m⁻³)",
    "bio_oracle__ph_mean__depthsurf": "pH",
    "bio_oracle__bathymetry_mean__benthic": "Bathymetry (m)",
}
PERIOD_ORDER = ["2000-2009", "2010-2019", "2020-2026"]
TARGET = "presence_background_label"
KEY = "target_taxon_key"
PERIOD = "analysis_period"
CELL = "grid_cell_id"
ELIGIBLE = "eligible_species_level_ml"
SEED = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_csv(frame: pd.DataFrame, name: str) -> str:
    dst = TABLES / name
    frame.to_csv(dst, index=False)
    return str(dst.relative_to(ROOT))


def save_fig(name: str) -> str:
    dst = FIGURES / name
    plt.savefig(dst, dpi=160, bbox_inches="tight")
    plt.close()
    return str(dst.relative_to(ROOT))


def numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return frame[columns].apply(pd.to_numeric, errors="coerce").replace(
        [np.inf, -np.inf], np.nan
    )


def nice_axes(ax, title: str, ylabel: str = "") -> None:
    ax.set_title(title)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.20)


def package_versions() -> dict[str, str]:
    """Capture the versions actually running this analysis."""
    names = ["python", "numpy", "pandas", "geopandas", "pyarrow", "matplotlib", "seaborn"]
    versions = {"python": ".".join(map(str, __import__("sys").version_info[:3]))}
    for name in names[1:]:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = "unavailable"
    return versions


def protected_fingerprints() -> dict[str, str]:
    """Hash every immutable data and source file required for this EDA task."""
    missing = [name for name in EXPECTED_SHA256 if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Required frozen input(s) missing: {missing}")
    actual = {name: sha256(ROOT / name) for name in EXPECTED_SHA256}
    wrong = {name: {"expected": EXPECTED_SHA256[name], "actual": digest}
             for name, digest in actual.items() if digest != EXPECTED_SHA256[name]}
    if wrong:
        raise RuntimeError(f"Frozen input fingerprint mismatch; no EDA outputs written: {wrong}")
    return actual


def require_valid_input(df: gpd.GeoDataFrame) -> tuple[list[str], dict]:
    must = [TARGET, KEY, PERIOD, CELL, ELIGIBLE, "sample_id", "sample_type",
            "paired_presence_source_row", "integration_source_row", "taxonRank",
            "ml_eligibility_reason", "AphiaID", "raster_cell_center_longitude",
            "raster_cell_center_latitude", *CORE]
    missing = sorted(set(must) - set(df.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    environment = sorted(c for c in df.columns if c.startswith("bio_oracle__"))
    if df.shape != (4706, 527) or len(environment) != 382:
        raise ValueError(f"Unexpected frozen schema {df.shape}, {len(environment)} environmental columns")
    if df.crs is None or df.crs.to_epsg() != 4326:
        raise ValueError("Expected EPSG:4326 GeoParquet")
    if not (df.geometry.notna().all() and df.geometry.is_valid.all()
            and df.geometry.geom_type.eq("Point").all()):
        raise ValueError("Every geometry must be a valid WGS84 Point")
    counts = df[TARGET].value_counts(dropna=False).to_dict()
    if counts != {1: 2353, 0: 2353}:
        raise ValueError(f"Unexpected class label distribution: {counts}")
    if not df["sample_id"].is_unique:
        raise ValueError("Sample IDs are not unique")
    if df[ELIGIBLE].isna().any():
        raise ValueError("Species-level eligibility flag contains missing values")
    if df.loc[df[TARGET].eq(0), "integration_source_row"].notna().any():
        raise ValueError("A sampled background has an original observation row ID")
    if df.loc[df[TARGET].eq(1), "integration_source_row"].isna().any():
        raise ValueError("An observed presence is missing its original observation row ID")
    pairs = pd.crosstab(df["paired_presence_source_row"], df[TARGET])
    if not ((pairs.get(0, 0) == 1) & (pairs.get(1, 0) == 1)).all() or len(pairs) != 2353:
        raise ValueError("Expected exactly one positive and one background per source row")
    source_cells = set(df.loc[df[TARGET].eq(1), CELL].dropna())
    background_cells = set(df.loc[df[TARGET].eq(0), CELL].dropna())
    background_cell_rows = df.loc[df[TARGET].eq(0), CELL]
    if background_cell_rows.isna().any() or background_cell_rows.nunique() != len(background_cell_rows):
        raise ValueError("Sampled backgrounds are missing grid cells or reuse a background cell")
    if source_cells.intersection(background_cells):
        raise ValueError("A sampled background overlaps an original source cell")
    return environment, {
        "rows": len(df), "columns": len(df.columns),
        "class_counts": {str(k): int(v) for k, v in counts.items()},
        "taxon_keys": int(df[KEY].nunique()),
        "occupied_positive_cells": len(source_cells),
        "distinct_background_cells": len(background_cells),
        "background_cells_unique": background_cell_rows.is_unique,
        "positive_background_cell_overlap": 0,
        "source_paired_records": len(pairs),
    }


def section_a(df: gpd.GeoDataFrame, env: list[str], eligible: gpd.GeoDataFrame) -> dict:
    """A. Dataset dimensions, row meaning, types and target/eligibility overview."""
    def category(c: str) -> str:
        if c in env:
            return "environmental predictor candidate"
        if c == "geometry":
            return "spatial geometry (not a predictor by default)"
        if c == TARGET:
            return "constructed supervised target"
        if c in (KEY, "AphiaID", "taxonRank", "scientificName", "species", "speciesid"):
            return "taxonomic identity/conditioning"
        if c in ("sample_id", "paired_presence_source_row", "integration_source_row", "occurrenceID"):
            return "provenance/identity (exclude from predictors)"
        if c.startswith("raster_") or c in ("analysis_period", "environment_period"):
            return "spatial/temporal metadata (leakage review needed)"
        return "source/quality metadata (not automatically a predictor)"

    dictionary = pd.DataFrame({
        "column": df.columns, "dtype": [str(t) for t in df.dtypes],
        "role": [category(c) for c in df.columns],
        "non_null_count": [int(df[c].notna().sum()) for c in df.columns],
        "null_count": [int(df[c].isna().sum()) for c in df.columns],
    })
    save_csv(dictionary, "A_data_dictionary.csv")
    class_tables = []
    for population, frame in [("complete_population", df),
                              ("eligible_species_subset", eligible)]:
        group = frame.groupby([PERIOD, TARGET], observed=True).size().rename("rows").reset_index()
        group.insert(0, "population", population)
        class_tables.append(group)
    classes = pd.concat(class_tables, ignore_index=True)
    save_csv(classes, "A_class_counts_by_period.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.countplot(data=df, x=PERIOD, hue=TARGET, order=PERIOD_ORDER, ax=ax)
    nice_axes(ax, "Presence (1) and background (0) by environmental period", "Rows")
    ax.set_xlabel("Observation period (2020–2026 uses SSP245 projection)")
    ax.legend(title="Constructed label")
    save_fig("A_target_by_period.png")
    return {"total_rows": len(df), "columns": len(df.columns), "environment_columns": len(env),
            "eligible_rows": len(eligible), "eligible_positive_rows": int(eligible[TARGET].eq(1).sum()),
            "eligible_background_rows": int(eligible[TARGET].eq(0).sum()),
            "full_unique_taxa": int(df.loc[df[TARGET].eq(1), KEY].nunique()),
            "eligible_unique_taxa": int(eligible.loc[eligible[TARGET].eq(1), KEY].nunique()),
            "period_class_counts_csv": "A_class_counts_by_period.csv",
            "files": ["A_data_dictionary.csv", "A_class_counts_by_period.csv"]}


def section_b(df: gpd.GeoDataFrame, env: list[str]) -> dict:
    """B. Nulls, placeholder blanks, duplicate keys and environmental coverage."""
    arrays = numeric(df, env)
    raw = df[env].apply(pd.to_numeric, errors="coerce")
    populations = [("complete_population", df),
                   ("eligible_species_subset", df.loc[df[ELIGIBLE].astype(bool)])]
    rows = []
    for population, frame in populations:
        indexes = frame.index
        numeric_values = arrays.loc[indexes]
        for name in env:
            x = raw.loc[indexes, name]
            rows.append({
                "population": population, "feature": name, "rows": len(frame),
                "non_null": int(numeric_values[name].notna().sum()),
                "missing": int(numeric_values[name].isna().sum()),
                "missing_pct": float(100 * numeric_values[name].isna().mean()) if len(frame) else 0.0,
                "positive_infinity": int(np.isposinf(x.to_numpy(dtype=float, na_value=np.nan)).sum()),
                "negative_infinity": int(np.isneginf(x.to_numpy(dtype=float, na_value=np.nan)).sum()),
                "missing_presence": int(numeric_values.loc[frame[TARGET].eq(1), name].isna().sum()),
                "missing_background": int(numeric_values.loc[frame[TARGET].eq(0), name].isna().sum()),
            })
    nulls = pd.DataFrame(rows).sort_values(
        ["population", "missing_pct", "feature"], ascending=[True, False, True])
    save_csv(nulls, "B_environmental_missingness.csv")
    per_period = []
    for population, frame in populations:
        values = arrays.loc[frame.index]
        for period in PERIOD_ORDER:
            for label in (1, 0):
                mask = frame[PERIOD].eq(period) & frame[TARGET].eq(label)
                subset = values.loc[mask]
                pattern_count = int(subset.isna().astype("uint8").drop_duplicates().shape[0]) if len(subset) else 0
                for name in env:
                    per_period.append({"population": population, "period": period, "label": label,
                                       "feature": name, "rows": len(subset),
                                       "missing": int(subset[name].isna().sum()),
                                       "distinct_missingness_patterns": pattern_count})
    save_csv(pd.DataFrame(per_period), "B_missingness_by_period_class.csv")

    # Blank OBIS strings are preserved in existing source data; not to be conflated with NaN.
    obj = df.select_dtypes(include=["object", "string"])
    blanks = []
    for name in obj.columns:
        if name == "geometry":
            continue
        series = obj[name].dropna().astype(str)
        n = int(series.str.strip().eq("").sum())
        if n:
            blanks.append({"column": name, "blank_non_null_strings": n})
    save_csv(pd.DataFrame(blanks, columns=["column", "blank_non_null_strings"]), "B_blank_strings.csv")

    repeated_rows = []
    for population, frame in populations:
        pos = frame.loc[frame[TARGET].eq(1)]
        sample_key = [KEY, PERIOD, CELL]
        counts = pos.groupby(sample_key, dropna=False).size().rename("source_records").reset_index()
        repeated = counts.loc[counts["source_records"].gt(1)].copy()
        repeated.insert(0, "population", population)
        repeated_rows.append(repeated)
    duplicates = pd.concat(repeated_rows, ignore_index=True)
    save_csv(duplicates, "B_repeated_positive_taxon_cell_period.csv")
    fig, ax = plt.subplots(figsize=(9, 5))
    top = nulls.loc[nulls["population"].eq("complete_population")].head(20).iloc[::-1]
    ax.barh(top["feature"].str.replace("bio_oracle__", "", regex=False), top["missing_pct"])
    nice_axes(ax, "Top 20 environmental columns by missingness")
    ax.set_xlabel("Missing (%) — full candidate dataset")
    ax.tick_params(axis="y", labelsize=8)
    save_fig("B_environment_missingness.png")
    full = nulls.loc[nulls["population"].eq("complete_population")]
    eligible = nulls.loc[nulls["population"].eq("eligible_species_subset")]
    full_repeats = duplicates.loc[duplicates["population"].eq("complete_population")]
    eligible_repeats = duplicates.loc[duplicates["population"].eq("eligible_species_subset")]
    return {"environment_fully_nonmissing_features": int((full["missing"] == 0).sum()),
            "environment_all_missing_features": int((full["non_null"] == 0).sum()),
            "eligible_fully_nonmissing_features": int((eligible["missing"] == 0).sum()),
            "eligible_all_missing_features": int((eligible["non_null"] == 0).sum()),
            "positive_infinity_positions": int(nulls["positive_infinity"].sum()),
            "negative_infinity_positions": int(nulls["negative_infinity"].sum()),
            "repeated_positive_taxon_cell_period_groups_full": len(full_repeats),
            "positive_rows_in_repeated_groups_full": int(full_repeats["source_records"].sum()),
            "extra_records_beyond_one_per_repeated_group_full": int((full_repeats["source_records"] - 1).sum()),
            "repeated_positive_taxon_cell_period_groups_eligible": len(eligible_repeats),
            "positive_rows_in_repeated_groups_eligible": int(eligible_repeats["source_records"].sum()),
            "extra_records_beyond_one_per_repeated_group_eligible": int((eligible_repeats["source_records"] - 1).sum()),
            "blank_string_columns": len(blanks),
            "blank_string_values": int(sum(item["blank_non_null_strings"] for item in blanks))}


def section_c(df: gpd.GeoDataFrame) -> dict:
    """C. Taxa, top occurrence records, grid cells, eligibility and time."""
    positives = df.loc[df[TARGET].eq(1)].copy()
    grouped = positives.groupby(KEY, dropna=False)
    taxa = grouped.agg(original_records=(TARGET, "size"),
                       distinct_occupied_cells=(CELL, "nunique"),
                       active_periods=(PERIOD, "nunique")).reset_index()
    full_cell_periods = (positives[[KEY, PERIOD, CELL]].drop_duplicates()
                         .groupby(KEY, dropna=False).size().rename("distinct_cell_periods").reset_index())
    taxa = taxa.merge(full_cell_periods, on=KEY, how="left", validate="1:1")
    eligible_positive = positives.loc[positives[ELIGIBLE].astype(bool)]
    eligible_taxa = eligible_positive.groupby(KEY, dropna=False).agg(
        eligible_source_records=(TARGET, "size"), eligible_distinct_cells=(CELL, "nunique")
    ).reset_index()
    eligible_cell_periods = (eligible_positive[[KEY, PERIOD, CELL]].drop_duplicates()
                             .groupby(KEY, dropna=False).size().rename("eligible_cell_periods").reset_index())
    eligible_taxa = eligible_taxa.merge(eligible_cell_periods, on=KEY, how="left", validate="1:1")
    taxa = taxa.merge(eligible_taxa, on=KEY, how="left", validate="1:1")
    taxa[["eligible_source_records", "eligible_distinct_cells", "eligible_cell_periods"]] = (
        taxa[["eligible_source_records", "eligible_distinct_cells", "eligible_cell_periods"]].fillna(0).astype(int))
    name_frame = grouped["scientificName"].first().rename("reported_name").reset_index()
    taxa = taxa.merge(name_frame, on=KEY, how="left", validate="1:1")
    for period in PERIOD_ORDER:
        period_rows = positives.loc[positives[PERIOD].eq(period)]
        period_table = period_rows.groupby(KEY, dropna=False).agg(
            **{f"records_{period}": (TARGET, "size"),
               f"distinct_cells_{period}": (CELL, "nunique")}).reset_index()
        taxa = taxa.merge(period_table, on=KEY, how="left", validate="1:1")
    count_columns = [c for c in taxa if c.startswith(("records_", "distinct_cells_"))]
    taxa[count_columns] = taxa[count_columns].fillna(0).astype(int)
    taxa.sort_values(["eligible_source_records", "distinct_occupied_cells", "original_records"],
                     ascending=False, inplace=True)
    save_csv(taxa, "C_taxon_counts_distinct_cells.csv")
    reasons = df.groupby([TARGET, "ml_eligibility_reason"], dropna=False).size().rename("rows").reset_index()
    save_csv(reasons, "C_eligibility_reasons.csv")
    period = df.groupby([PERIOD, TARGET, ELIGIBLE]).size().rename("rows").reset_index()
    save_csv(period, "C_period_class_eligibility.csv")
    fig, ax = plt.subplots(figsize=(10, 6))
    best = taxa.head(15).iloc[::-1].copy()
    best["display"] = best["reported_name"].fillna(best[KEY]).astype(str).str.slice(0, 45)
    ax.barh(best["display"], best["distinct_occupied_cells"])
    nice_axes(ax, "Top taxa by occupied observed grid cells")
    ax.set_xlabel("Unique observed raster cells (not independent observations)")
    save_fig("C_top_taxa_cells.png")
    return {"taxon_keys": int(len(taxa)), "eligible_positive_records": int(positives[ELIGIBLE].sum()),
            "ineligible_positive_records": int((~positives[ELIGIBLE].astype(bool)).sum()),
            "taxa_with_eligible_records": int((taxa["eligible_source_records"] > 0).sum()),
            "distinct_positive_cells_full": int(positives[CELL].nunique()),
            "distinct_positive_cells_eligible": int(positives.loc[positives[ELIGIBLE].astype(bool), CELL].nunique()),
            "distinct_positive_cell_periods_full": int(positives[[PERIOD, CELL]].drop_duplicates().shape[0]),
            "distinct_positive_cell_periods_eligible": int(positives.loc[positives[ELIGIBLE].astype(bool), [PERIOD, CELL]].drop_duplicates().shape[0]),
            "top_taxon_key_by_eligible_records": str(taxa.iloc[0][KEY]) if len(taxa) else None}


def section_d(df: gpd.GeoDataFrame) -> dict:
    """D. Core environment distributions, missingness and descriptive IQR outliers."""
    core = list(CORE)
    sub = df[[TARGET, PERIOD, ELIGIBLE] + core].copy()
    sub[core] = numeric(df, core)
    by_period = []
    overall = []
    outliers = []
    for population, frame in [("complete_population", sub),
                              ("eligible_species_subset", sub.loc[sub[ELIGIBLE].astype(bool)])]:
        for (period, label), group in frame.groupby([PERIOD, TARGET], observed=True):
            for feature in core:
                x = group[feature].dropna()
                by_period.append({"population": population, "period": period, "label": int(label),
                                  "feature": feature, "n": len(x),
                                  "mean": float(x.mean()) if len(x) else np.nan,
                                  "median": float(x.median()) if len(x) else np.nan,
                                  "std": float(x.std()) if len(x) > 1 else np.nan,
                                  "q25": float(x.quantile(.25)) if len(x) else np.nan,
                                  "q75": float(x.quantile(.75)) if len(x) else np.nan,
                                  "min": float(x.min()) if len(x) else np.nan,
                                  "max": float(x.max()) if len(x) else np.nan})
        for label, group in frame.groupby(TARGET, observed=True):
            for feature in core:
                x = group[feature].dropna()
                overall.append({"population": population, "label": int(label), "feature": feature,
                                "n": len(x), "mean": float(x.mean()) if len(x) else np.nan,
                                "median": float(x.median()) if len(x) else np.nan,
                                "std": float(x.std()) if len(x) > 1 else np.nan,
                                "q25": float(x.quantile(.25)) if len(x) else np.nan,
                                "q75": float(x.quantile(.75)) if len(x) else np.nan,
                                "min": float(x.min()) if len(x) else np.nan,
                                "max": float(x.max()) if len(x) else np.nan})
                if x.empty:
                    count = 0
                else:
                    q1, q3 = x.quantile([.25, .75]); width = q3 - q1
                    count = int(((x < q1 - 1.5 * width) | (x > q3 + 1.5 * width)).sum())
                outliers.append({"population": population, "label": int(label), "feature": feature,
                                 "non_null": len(x), "iqr_flagged_rows_descriptive_only": count})
    save_csv(pd.DataFrame(by_period), "D_core_by_period_class_stats.csv")
    save_csv(pd.DataFrame(overall), "D_core_overall_class_stats.csv")
    iqr_outliers = []
    save_csv(pd.DataFrame(outliers), "D_core_IQR_flags.csv")
    plot_data = sub.copy()
    plot_data["class"] = plot_data[TARGET].map({1: "Observed presence (1)", 0: "Sampled background (0)"})
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, (feature, label) in zip(axes.ravel(), CORE.items()):
        if plot_data[feature].notna().any():
            sns.histplot(data=plot_data, x=feature, hue="class", stat="density", common_norm=False,
                         element="step", fill=False, bins=30, ax=ax)
            nice_axes(ax, label, "Density")
        else:
            ax.text(.5, .5, "No non-missing values", ha="center", va="center", transform=ax.transAxes)
            nice_axes(ax, label)
        ax.set_xlabel(label)
    fig.suptitle("Overall core environmental distributions by observed/background class")
    fig.tight_layout()
    save_fig("D_core_distributions_by_class.png")
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (feature, label) in zip(axes.ravel(), CORE.items()):
        if plot_data[feature].notna().any():
            sns.boxplot(data=plot_data, x=PERIOD, y=feature, hue="class", order=PERIOD_ORDER,
                        hue_order=["Observed presence (1)", "Sampled background (0)"],
                        ax=ax, showfliers=False)
            nice_axes(ax, label)
        else:
            ax.text(.5, .5, "No non-missing values", ha="center", va="center", transform=ax.transAxes)
            nice_axes(ax, label)
        ax.set_xlabel("Analysis period")
        ax.set_ylabel(label)
        ax.tick_params(axis="x", labelrotation=20)
        if ax.legend_:
            ax.legend_.remove()
    fig.suptitle("Core environment by period; 2020–2026 is SSP245 projected")
    fig.tight_layout()
    save_fig("D_core_distributions_by_period.png")
    bathymetry = {}
    six_core_complete_by_class = {}
    for population, frame in [("complete_population", sub),
                              ("eligible_species_subset", sub.loc[sub[ELIGIBLE].astype(bool)])]:
        bathymetry[population] = {}
        six_core_complete_by_class[population] = {}
        for label in (1, 0):
            sample = frame.loc[frame[TARGET].eq(label)]
            complete_count = int(sample[core].notna().all(axis=1).sum())
            six_core_complete_by_class[population][str(label)] = {
                "rows": len(sample), "all_six_nonmissing": complete_count,
                "one_or_more_missing": len(sample) - complete_count}
        for (period, label), group in frame.groupby([PERIOD, TARGET], observed=True):
            values = group["bio_oracle__bathymetry_mean__benthic"].dropna()
            bathymetry[population][f"{period}|label_{int(label)}"] = {
                "n": len(values), "median_m": None if values.empty else float(values.median()),
                "q25_m": None if values.empty else float(values.quantile(.25)),
                "q75_m": None if values.empty else float(values.quantile(.75)),
            }
    return {"core_count": len(CORE),
            "complete_six_core_rows": {
                "complete_population": int(sub[core].notna().all(axis=1).sum()),
                "eligible_species_subset": int(sub.loc[sub[ELIGIBLE].astype(bool), core].notna().all(axis=1).sum())},
            "six_core_completeness_by_class": six_core_complete_by_class,
            "bathymetry_median_by_period_and_class": bathymetry,
            "interpretation": "Differences describe this constructed sample and do not establish a biological effect."}


def section_e(df: gpd.GeoDataFrame, env: list[str], feature_catalog: dict) -> dict:
    """E. Period-specific redundancy screening on distinct grid-cell profiles."""
    profile_sets = {
        "complete_population": df.drop_duplicates([PERIOD, CELL]).copy(),
        "eligible_species_subset": df.loc[df[ELIGIBLE].astype(bool)].drop_duplicates([PERIOD, CELL]).copy(),
    }
    statuses = []
    pairs = []
    for population, profiles in profile_sets.items():
        matrix = numeric(profiles, env)
        for name in env:
            meta = feature_catalog.get(name, {})
            values = matrix[name]
            qperiods = meta.get("quarantined_periods", [])
            statuses.append({
                "population": population, "feature": name, "unique_cell_period_profiles": len(profiles),
                "valid_profiles": int(values.notna().sum()),
                "missing_profiles": int(values.isna().sum()),
                "missing_pct_profiles": float(100 * values.isna().mean()) if len(values) else 0.0,
                "distinct_nonnull_values": int(values.nunique(dropna=True)),
                "constant_or_empty": values.nunique(dropna=True) <= 1,
                "quarantined_periods_in_manifest": ", ".join(qperiods),
                "quarantine_reasons_in_manifest": json.dumps(meta.get("quarantine_reasons_by_period", {}), ensure_ascii=False),
            })
        for period in PERIOD_ORDER:
            current = profiles.loc[profiles[PERIOD].eq(period)]
            x = numeric(current, env)
            # Keep features with useful coverage and variation; this only controls
            # pairwise calculation, never removes columns from the source table.
            keep = x.columns[(x.notna().mean() >= .80) & (x.nunique(dropna=True) > 1)].tolist()
            if len(current) < 10 or len(keep) < 2:
                continue
            rho = x[keep].corr(method="spearman", min_periods=max(10, int(len(current) * .70)))
            r, c = np.triu_indices(len(keep), 1)
            vals = rho.to_numpy()[r, c]
            strong = np.flatnonzero(np.isfinite(vals) & (np.abs(vals) >= .95))
            for i in strong:
                a, b = keep[r[i]], keep[c[i]]
                pairs.append({"population": population, "period": period,
                              "feature_a": a, "feature_b": b,
                              "spearman_rho": float(vals[i]),
                              "paired_valid_profiles": int(x[[a, b]].dropna().shape[0]),
                              "unique_cell_period_profiles": len(current)})
    status = pd.DataFrame(statuses)
    save_csv(status, "E_feature_profile_screen.csv")
    correlations = pd.DataFrame(pairs, columns=["population", "period", "feature_a", "feature_b",
                                                "spearman_rho", "paired_valid_profiles",
                                                "unique_cell_period_profiles"])
    if not correlations.empty:
        correlations.sort_values("spearman_rho", key=lambda s: s.abs(), ascending=False,
                                 inplace=True)
    save_csv(correlations, "E_redundant_feature_pairs_by_period.csv")
    core = list(CORE)
    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    for row_idx, (population, profiles) in enumerate(profile_sets.items()):
        for col_idx, period in enumerate(PERIOD_ORDER):
            ax = axes[row_idx, col_idx]
            this = profiles.loc[profiles[PERIOD].eq(period)]
            corr = numeric(this, core).corr(method="spearman")
            sns.heatmap(corr, ax=ax, cmap="vlag", vmin=-1, vmax=1, annot=True,
                        fmt=".2f", square=True, cbar=False,
                        xticklabels=[c.replace("bio_oracle__", "").split("__")[0] for c in core],
                        yticklabels=[c.replace("bio_oracle__", "").split("__")[0] for c in core])
            ax.set_title(f"{population.replace('_', ' ')} · {period} (n={len(this)} cells)")
            ax.tick_params(axis="x", labelrotation=60)
    fig.suptitle("Core Spearman correlations — distinct cell/period profiles; screening only")
    fig.tight_layout()
    save_fig("E_core_spearman_by_period.png")
    qfeatures = {name for name, meta in feature_catalog.items() if meta.get("quarantined_periods")}
    return {"unique_cell_period_profiles": {name: len(frame) for name, frame in profile_sets.items()},
            "environmental_definitions_screened": len(env),
            "constant_or_empty_feature_counts": {
                name: int(status.loc[status["population"].eq(name), "constant_or_empty"].sum())
                for name in profile_sets},
            "features_with_quarantined_periods_in_manifest": len(qfeatures),
            "quarantined_period_definition_count": int(sum(len(feature_catalog.get(name, {}).get("quarantined_periods", [])) for name in qfeatures)),
            "high_correlation_pair_rows_at_abs_rho_ge_0_95": len(correlations),
            "note": "Pair screens use distinct cells within period. They are exploratory flags; no feature was removed."}


def haversine_min_km(bg_lat: np.ndarray, bg_lon: np.ndarray,
                     p_lat: np.ndarray, p_lon: np.ndarray) -> np.ndarray:
    """Nearest recorded point distance. Each taxon group is small; use broadcasting."""
    if not len(p_lat):
        return np.full(len(bg_lat), np.nan)
    rlat1 = np.radians(bg_lat)[:, None]
    rlon1 = np.radians(bg_lon)[:, None]
    rlat2 = np.radians(p_lat)[None, :]
    rlon2 = np.radians(p_lon)[None, :]
    a = (np.sin((rlat2 - rlat1) / 2) ** 2
         + np.cos(rlat1) * np.cos(rlat2) * np.sin((rlon2 - rlon1) / 2) ** 2)
    return 2 * 6371.0088 * np.arcsin(np.sqrt(np.clip(a, 0, 1))).min(axis=1)


def load_gshhg_coastline() -> tuple[object, list[float]]:
    """Read local GSHHG L1 land outlines and remove the collection-window edge."""
    if not GSHHG_ARCHIVE.is_file() or not GSHHG_REFERENCE.is_file():
        raise FileNotFoundError("The local GSHHG coastline archive and reference record are required for Section F")
    reference = json.loads(GSHHG_REFERENCE.read_text(encoding="utf-8"))
    bounds = [float(value) for value in reference["study_bounds"]]
    window = box(*bounds)
    uri = f"zip://{GSHHG_ARCHIVE.as_posix()}!GSHHS_shp/f/GSHHS_f_L1.shp"
    land = gpd.read_file(uri, bbox=tuple(bounds))
    clipped = [geometry.intersection(window) for geometry in land.geometry if geometry is not None]
    clipped = [geometry for geometry in clipped if not geometry.is_empty]
    if not clipped:
        raise ValueError("No GSHHG L1 land polygons intersect the recorded collection envelope")
    land_union = unary_union(clipped)
    # The rectangle intersection creates artificial edge segments. Removing them
    # leaves the source coastline pieces inside the study window.
    coast = land_union.boundary.difference(window.boundary)
    if coast.is_empty:
        raise ValueError("Could not extract a coastline inside the recorded study window")
    return coast, bounds


def section_f(df: gpd.GeoDataFrame, coastline: object | None = None) -> dict:
    """F. Spatial spread, repeated cells, coastline distance and class separation."""
    if coastline is None:
        coastline, bounds = load_gshhg_coastline()
    else:
        bounds = None
    plot = pd.DataFrame({"lon": df.geometry.x, "lat": df.geometry.y,
                         "label": df[TARGET].to_numpy(),
                         "period": df[PERIOD].to_numpy(),
                         "taxon": df[KEY].to_numpy(), "cell": df[CELL].to_numpy(),
                         "sample_id": df["sample_id"].to_numpy()})
    # Use persisted raster-cell centres for the coastline-distance comparison,
    # so occurrence and background coordinates refer to the same grid support.
    centre_points = gpd.GeoSeries(
        gpd.points_from_xy(df["raster_cell_center_longitude"], df["raster_cell_center_latitude"]),
        crs="EPSG:4326")
    coast_m = gpd.GeoSeries([coastline], crs="EPSG:4326").to_crs(GSHHG_METRIC_CRS).iloc[0]
    centre_m = centre_points.to_crs(GSHHG_METRIC_CRS)
    plot["distance_to_coast_km"] = centre_m.distance(coast_m).to_numpy() / 1000.0
    plot["bathymetry_m"] = numeric(df, ["bio_oracle__bathymetry_mean__benthic"]).iloc[:, 0].to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharex=True, sharey=True)
    for ax, label, title in zip(axes, [1, 0], ["Recorded occurrences", "Sampled backgrounds"]):
        x = plot.loc[plot["label"].eq(label)]
        points = ax.scatter(x["lon"], x["lat"], c=x["distance_to_coast_km"],
                            cmap="viridis", s=9, alpha=.55, rasterized=True)
        ax.set_xlabel("Longitude (EPSG:4326)"); ax.set_ylabel("Latitude (EPSG:4326)")
        ax.set_title(title)
        ax.grid(alpha=.15)
        ax.set_aspect("equal", adjustable="box")
    fig.subplots_adjust(top=.88, bottom=.24, left=.08, right=.96, wspace=.10)
    colorbar_axis = fig.add_axes([.30, .12, .40, .025])
    colorbar = fig.colorbar(points, cax=colorbar_axis, orientation="horizontal")
    colorbar.set_label("Distance from raster-cell centre to GSHHG coast (km)")
    fig.suptitle("Locations and nearshore/offshore gradient — diagnostic only")
    save_fig("F_spatial_presence_background.png")

    distances = []
    populations = [("complete_population", plot),
                   ("eligible_species_subset", plot.loc[df[ELIGIBLE].astype(bool).to_numpy()])]
    for population, frame in populations:
        for (period, taxon), group in frame.groupby(["period", "taxon"], dropna=False):
            pos = group.loc[group["label"].eq(1)]
            bg = group.loc[group["label"].eq(0)]
            closest = haversine_min_km(bg["lat"].to_numpy(float), bg["lon"].to_numpy(float),
                                       pos["lat"].to_numpy(float), pos["lon"].to_numpy(float))
            distances.extend({"population": population, "period": period,
                              "taxon_key": str(taxon), "sample_id": sample_id,
                              "background_cell_id": cell, "nearest_presence_km": float(value)}
                             for sample_id, cell, value in zip(bg["sample_id"], bg["cell"], closest)
                             if np.isfinite(value))
    near = pd.DataFrame(distances, columns=["population", "period", "taxon_key", "sample_id",
                                           "background_cell_id", "nearest_presence_km"])
    save_csv(near, "F_background_distance_to_same_taxon_presence.csv")
    fig, ax = plt.subplots(figsize=(9, 4))
    full_near = near.loc[near["population"].eq("complete_population")]
    if not full_near.empty:
        sns.histplot(data=full_near, x="nearest_presence_km", hue="period", bins=35,
                     element="step", fill=False, common_norm=False, ax=ax)
    nice_axes(ax, "Background distance to nearest same-taxon, same-period presence")
    ax.set_xlabel("Great-circle distance (km)")
    save_fig("F_nearest_presence_distances.png")
    cell_rows = []
    coast_summary = []
    for population, frame in populations:
        for (label, period, taxon, cell), group in frame.groupby(["label", "period", "taxon", "cell"], dropna=False):
            cell_rows.append({"population": population, "label": int(label), "period": period,
                              "taxon_key": str(taxon), "grid_cell_id": cell,
                              "records_in_cell_period": len(group),
                              "distance_to_coast_median_km": float(group["distance_to_coast_km"].median()),
                              "bathymetry_median_m": float(group["bathymetry_m"].median())
                              if group["bathymetry_m"].notna().any() else np.nan})
        for (period, label), group in frame.groupby(["period", "label"], observed=True):
            unique_cells = group.drop_duplicates("cell")
            dist = unique_cells["distance_to_coast_km"]
            coast_summary.append({"population": population, "period": period, "label": int(label),
                                  "unique_cells": len(unique_cells),
                                  "median_distance_to_coast_km": float(dist.median()),
                                  "q25_distance_to_coast_km": float(dist.quantile(.25)),
                                  "q75_distance_to_coast_km": float(dist.quantile(.75)),
                                  "p90_distance_to_coast_km": float(dist.quantile(.90)),
                                  "median_bathymetry_m": float(unique_cells["bathymetry_m"].median())})
    cells = pd.DataFrame(cell_rows)
    save_csv(cells.sort_values(["population", "period", "label", "records_in_cell_period"],
                               ascending=[True, True, True, False]),
             "F_observation_records_per_grid_cell_period.csv")
    coast = pd.DataFrame(coast_summary)
    positives = df.loc[df[TARGET].eq(1)]
    cell_reuse = positives.groupby(CELL).agg(
        source_records=(TARGET, "size"), distinct_taxa=(KEY, "nunique"),
        active_periods=(PERIOD, "nunique")).reset_index()
    full = near.loc[near["population"].eq("complete_population"), "nearest_presence_km"]
    return {"gshhg_reference_bounds": bounds, "distance_crs": GSHHG_METRIC_CRS,
            "nearshore_offshore_summary_by_period_class": coast.to_dict(orient="records"),
            "background_nearest_same_taxon_period_presence_km": {
                "n": len(full), "median": None if full.empty else float(full.median()),
                "p90": None if full.empty else float(full.quantile(.90))},
            "positive_cell_reuse": {
                "distinct_cells": len(cell_reuse),
                "cells_with_multiple_source_records": int(cell_reuse["source_records"].gt(1).sum()),
                "cells_shared_by_multiple_taxa": int(cell_reuse["distinct_taxa"].gt(1).sum()),
                "cells_used_in_multiple_periods": int(cell_reuse["active_periods"].gt(1).sum())},
            "max_source_records_per_taxon_cell_period": int(
                cells.loc[(cells["population"].eq("complete_population")) & (cells["label"].eq(1)),
                          "records_in_cell_period"].max()),
            "interpretation": "Distances use persisted raster-cell centres and the 2017 GSHHG coastline; these are geographic diagnostics, not survey-effort or habitat-suitability estimates."}


def markdown_table(frame: pd.DataFrame, columns: list[str], limit: int | None = None) -> str:
    """Render a small Markdown table without adding a documentation dependency."""
    view = frame[columns].copy()
    if limit is not None:
        view = view.head(limit)
    header = "| " + " | ".join(columns) + " |"
    rule = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join("" if pd.isna(value) else str(value) for value in row) + " |"
            for row in view.itertuples(index=False, name=None)]
    return "\n".join([header, rule, *body])


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Missing frozen EDA input: {SOURCE}")
    print("[EDA] Checking expected SHA-256 fingerprints for frozen datasets, scripts and shoreline source.", flush=True)
    fingerprints_before = protected_fingerprints()
    REPORTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    RECORDS.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    print(f"[EDA] Reading {SOURCE.relative_to(ROOT)}", flush=True)
    df = gpd.read_parquet(SOURCE)
    env, validation = require_valid_input(df)
    eligible = df.loc[df[ELIGIBLE].astype(bool)].copy()
    catalog = json.loads(INTEGRATION_MANIFEST.read_text(encoding="utf-8"))
    feature_catalog = catalog.get("feature_columns", {})
    if set(feature_catalog) != set(env):
        raise ValueError("Current integration feature catalogue does not reconcile to the 382 source columns")
    sections = {}
    jobs = [("A", lambda: section_a(df, env, eligible)),
            ("B", lambda: section_b(df, env)),
            ("C", lambda: section_c(df)),
            ("D", lambda: section_d(df)),
            ("E", lambda: section_e(df, env, feature_catalog)),
            ("F", lambda: section_f(df))]
    for label, action in jobs:
        print(f"[EDA] Section {label}/F", flush=True)
        sections[label] = action()

    required_tables = [
        "A_data_dictionary.csv", "A_class_counts_by_period.csv",
        "B_environmental_missingness.csv", "B_missingness_by_period_class.csv",
        "B_blank_strings.csv", "B_repeated_positive_taxon_cell_period.csv",
        "C_taxon_counts_distinct_cells.csv", "C_eligibility_reasons.csv",
        "C_period_class_eligibility.csv", "D_core_by_period_class_stats.csv",
        "D_core_overall_class_stats.csv", "D_core_IQR_flags.csv",
        "E_feature_profile_screen.csv", "E_redundant_feature_pairs_by_period.csv",
        "F_background_distance_to_same_taxon_presence.csv",
        "F_observation_records_per_grid_cell_period.csv",
    ]
    required_figures = [
        "A_target_by_period.png", "B_environment_missingness.png", "C_top_taxa_cells.png",
        "D_core_distributions_by_class.png", "D_core_distributions_by_period.png",
        "E_core_spearman_by_period.png", "F_spatial_presence_background.png",
        "F_nearest_presence_distances.png",
    ]
    absent = [f"reports/eda/tables/{name}" for name in required_tables if not (TABLES / name).is_file()]
    absent += [f"reports/eda/figures/{name}" for name in required_figures if not (FIGURES / name).is_file()]
    if absent:
        raise RuntimeError(f"EDA artifact creation incomplete: {absent}")
    fingerprints_after = {name: sha256(ROOT / name) for name in EXPECTED_SHA256}
    if fingerprints_before != fingerprints_after:
        changed = [name for name in EXPECTED_SHA256 if fingerprints_before[name] != fingerprints_after[name]]
        raise RuntimeError(f"Protected input changed during EDA: {changed}")

    source_meta = {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "sha256_before": fingerprints_before[str(SOURCE.relative_to(ROOT).as_posix())],
        "sha256_after": fingerprints_after[str(SOURCE.relative_to(ROOT).as_posix())],
        "bytes": SOURCE.stat().st_size,
        "shape": [len(df), len(df.columns)],
        "crs": f"EPSG:{df.crs.to_epsg()}" if df.crs.to_epsg() else str(df.crs),
        "geometry_type": sorted(df.geometry.geom_type.unique().tolist()),
        "environment_features": len(env),
    }
    quarantined = {name: meta.get("quarantined_periods", [])
                   for name, meta in feature_catalog.items() if meta.get("quarantined_periods")}
    warnings_list = [
        "Label 1 is an OBIS record; label 0 is an artificial sampled background, not a confirmed biological absence.",
        "Repeated occurrence records in a raster cell are not independent environmental samples.",
        "The 2020–2026 environmental assignment uses the Bio-ORACLE SSP245 2020 projected slice; it is not annual observation data.",
        "Presence/background bathymetry and coastline-distance contrasts may reflect sampling design and the broad accessible domain.",
        "GSHHG 2.3.7 is a 2017 coastline reference; shoreline distance is a descriptive grid-centre metric, not current metre-accuracy truth.",
        "Identifier, quality, lineage, geometry and target-construction fields can leak information if treated as predictors.",
        "Feature and species recommendations are exploratory only; no feature deletion, imputation, scaling, split or model fit was performed.",
    ]
    details = {
        "status": "All EDA sections A–F executed; downstream ML decisions remain open",
        "utc_generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": package_versions(),
        "source": source_meta,
        "protected_sha256_before": fingerprints_before,
        "protected_sha256_after": fingerprints_after,
        "all_protected_inputs_unchanged": fingerprints_before == fingerprints_after,
        "source_validation": validation,
        "complete_population_rows": len(df),
        "eligible_species_subset_rows": len(eligible),
        "environmental_features": len(env),
        "catalogue_quarantines": quarantined,
        "catalogue_feature_coverage_by_period": catalog.get("usable_features_by_period", {}),
        "sections": sections,
        "artifacts": {"tables": [f"reports/eda/tables/{n}" for n in required_tables],
                      "figures": [f"reports/eda/figures/{n}" for n in required_figures],
                      "report_json": SUMMARY_JSON.relative_to(ROOT).as_posix(),
                      "report_markdown": SUMMARY_MD.relative_to(ROOT).as_posix(),
                      "insight_log": INSIGHTS_MD.relative_to(ROOT).as_posix()},
        "warnings": warnings_list,
    }

    class_table = pd.read_csv(TABLES / "A_class_counts_by_period.csv")
    taxon_table = pd.read_csv(TABLES / "C_taxon_counts_distinct_cells.csv")
    missing_table = pd.read_csv(TABLES / "B_environmental_missingness.csv")
    core_table = pd.read_csv(TABLES / "D_core_overall_class_stats.csv")
    pair_table = pd.read_csv(TABLES / "E_redundant_feature_pairs_by_period.csv")
    eligibility_table = pd.read_csv(TABLES / "C_eligibility_reasons.csv")
    coast_table = pd.DataFrame(sections["F"]["nearshore_offshore_summary_by_period_class"])
    species_candidates = taxon_table.sort_values(
        ["eligible_distinct_cells", "eligible_source_records"], ascending=False)
    summary_table = pd.DataFrame([
        {"Measure": "Rows", "Value": f"{len(df):,}"},
        {"Measure": "Columns", "Value": f"{len(df.columns):,}"},
        {"Measure": "Bio-ORACLE definitions", "Value": f"{len(env):,}"},
        {"Measure": "Eligible-subset rows", "Value": f"{len(eligible):,}"},
        {"Measure": "Unique positive taxon keys", "Value": f"{df.loc[df[TARGET].eq(1), KEY].nunique():,}"},
        {"Measure": "Distinct positive grid cells", "Value": f"{df.loc[df[TARGET].eq(1), CELL].nunique():,}"},
        {"Measure": "Positive cell-periods", "Value": f"{df.loc[df[TARGET].eq(1), [PERIOD, CELL]].drop_duplicates().shape[0]:,}"},
    ])
    md = (
        "# OCEAVERA — Exploratory Data Analysis (Sections A–F)\n\n"
        "**Status:** Descriptive EDA completed on the frozen candidate table. This is not a target, species, predictor or modelling approval.\n\n"
        "## Input and population\n\n"
        f"- Source: `{source_meta['path']}` ({source_meta['bytes']:,} bytes)\n"
        f"- SHA-256: `{source_meta['sha256_before']}` (identical after execution)\n"
        f"- Shape/CRS/geometry: **{len(df):,} × {len(df.columns)}**, {source_meta['crs']}, {', '.join(source_meta['geometry_type'])}\n"
        f"- Environmental definitions: **{len(env)}**; all were retained in the input.\n"
        f"- Preliminary species-level eligible subset: **{len(eligible):,} rows** ({int(eligible[TARGET].eq(1).sum()):,} positives, {int(eligible[TARGET].eq(0).sum()):,} sampled backgrounds).\n\n"
        "A positive is a recorded OBIS occurrence. A background row is a sampled marine cell and is **not** a verified absence. Repeated records may share a grid cell.\n\n"
        "## Period and class counts\n\n" + markdown_table(class_table, ["population", "analysis_period", TARGET, "rows"]) +
        "\n\n## Taxa and environmental completeness\n\n"
        f"- Positive taxon keys: **{int(df.loc[df[TARGET].eq(1), KEY].nunique()):,}** (eligible-positive taxon keys: **{int(eligible.loc[eligible[TARGET].eq(1), KEY].nunique()):,}**).\n"
        f"- Distinct positive grid cells: **{int(df.loc[df[TARGET].eq(1), CELL].nunique()):,}**; distinct cell-periods: **{int(df.loc[df[TARGET].eq(1), [PERIOD, CELL]].drop_duplicates().shape[0]):,}**.\n"
        f"- Repeated positive taxon/cell/period groups: **{sections['B']['repeated_positive_taxon_cell_period_groups_full']:,}**, covering **{sections['B']['positive_rows_in_repeated_groups_full']:,}** records ({sections['B']['extra_records_beyond_one_per_repeated_group_full']:,} beyond one per group).\n"
        f"- Blank string values occur **{sections['B']['blank_string_values']:,}** times across {sections['B']['blank_string_columns']} source/metadata columns; null and blank counts remain separate.\n"
        f"- Environmental fields fully populated in complete population: **{sections['B']['environment_fully_nonmissing_features']} / {len(env)}**; completely empty: **{sections['B']['environment_all_missing_features']}**.\n"
        f"- Eligible subset fully populated features: **{sections['B']['eligible_fully_nonmissing_features']} / {len(env)}**; infinities found: **{sections['B']['positive_infinity_positions'] + sections['B']['negative_infinity_positions']}**.\n\n"
        "### Taxonomic eligibility reasons\n\n" + markdown_table(
            eligibility_table, [TARGET, "ml_eligibility_reason", "rows"]) +
        "\n\n### Species with broad eligible cell support for review\n\n" + markdown_table(
            species_candidates, [KEY, "reported_name", "eligible_source_records", "eligible_distinct_cells",
                                 "eligible_cell_periods", "active_periods"], 10) +
        "\n\nThese are candidates for group review, not an automatic focal-species choice. Some taxa and records may need ecological, taxonomic and observation-quality assessment.\n\n"
        "### Taxon overview (first 15 by eligible record support)\n\n" + markdown_table(
            taxon_table, [KEY, "reported_name", "original_records", "distinct_occupied_cells",
                          "eligible_source_records", "eligible_distinct_cells", "active_periods"], 15) +
        "\n\n## Core environment\n\n"
        "Values below are descriptive; units follow source/catalogue conventions. In particular, the oxygen unit notation requires interpretation.\n\n" +
        markdown_table(core_table, ["population", "label", "feature", "n", "median", "mean", "q25", "q75"]) +
        "\n\n### Six-core complete rows\n\n"
        f"- Complete population: **{sections['D']['complete_six_core_rows']['complete_population']:,}**\n"
        f"- Eligible subset: **{sections['D']['complete_six_core_rows']['eligible_species_subset']:,}**\n"
        f"- Of full-population positives, **{sections['D']['six_core_completeness_by_class']['complete_population']['1']['all_six_nonmissing']:,} / 2,353** have all six core values; backgrounds: **{sections['D']['six_core_completeness_by_class']['complete_population']['0']['all_six_nonmissing']:,} / 2,353**.\n"
        "- This asymmetry reflects the candidate construction's six-core completeness rule for sampled backgrounds and must be considered before interpreting class contrasts or choosing preprocessing.\n"
        "- IQR flags are descriptive only; no values were removed. Median depth and nearshore contrasts require review as potential sampling-domain confounding.\n\n"
        "## Correlation screening\n\n"
        f"- Distinct cell-period profiles: `{json.dumps(sections['E']['unique_cell_period_profiles'])}`\n"
        f"- Features with period-specific source quarantines in the accepted catalogue: **{sections['E']['features_with_quarantined_periods_in_manifest']}**; affected feature-period definitions: **{sections['E']['quarantined_period_definition_count']}**.\n"
        f"- High-correlation candidate pairs at |Spearman ρ| ≥ 0.95: **{len(pair_table):,} rows** across cohorts/periods.\n\n"
        "### Highest-correlation candidate pairs\n\n" + (markdown_table(
            pair_table, ["population", "period", "feature_a", "feature_b", "spearman_rho", "paired_valid_profiles"], 12)
            if not pair_table.empty else "No pairs met the screening threshold.") +
        "\n\nThese are redundancy prompts, not causal relationships or feature-removal decisions. Repeated cells and period-specific environmental slices constrain interpretation.\n\n"
        "### Feature-selection investigation candidates\n\n"
        "1. Review highly correlated max/range and related summary-statistic pairs within each environmental family, period and raster-cell support.\n"
        "2. Compare depth and coast-distance contrasts under a scientifically justified accessible marine domain before treating bathymetry or location as predictive signal.\n"
        "3. Resolve or retain quarantine/missingness treatment for the affected feature-period definitions, and exclude IDs, provenance, target-construction and quality fields from predictor candidates unless a leakage-safe use is justified.\n\n"
        "These steps identify what to investigate next; they do not remove or approve features.\n\n"
        "## Spatial and sampling diagnostics\n\n"
        f"- Same-taxon, same-period background-to-nearest-recorded-point distance: median **{sections['F']['background_nearest_same_taxon_period_presence_km']['median']:.2f} km**, p90 **{sections['F']['background_nearest_same_taxon_period_presence_km']['p90']:.2f} km** (n={sections['F']['background_nearest_same_taxon_period_presence_km']['n']:,}).\n"
        f"- Maximum observed source records in a taxon/cell/period: **{sections['F']['max_source_records_per_taxon_cell_period']}**.\n"
        "- Coast-distance summaries use raster-cell centres and GSHHG 2.3.7 in a local projected CRS. They are descriptive nearshore/offshore diagnostics; the shoreline is from 2017 and not metre-accuracy current truth.\n\n"
        "### Coastline-distance and bathymetry by class/period\n\n" + markdown_table(
            coast_table, ["population", "period", "label", "unique_cells", "median_distance_to_coast_km",
                          "q25_distance_to_coast_km", "q75_distance_to_coast_km", "median_bathymetry_m"]) +
        "\n\n## Source quarantines and interpretation limits\n\n"
        f"- The accepted feature catalogue records **{len(quarantined)} feature definitions** with quarantined period(s); **{sections['E']['quarantined_period_definition_count']} feature-period definitions** are affected. All **{len(env)}** columns remain present, including quarantined definitions.\n"
        "- 2020–2026 environmental assignment uses SSP245 2020 projected data; it is not an annual measurement.\n"
        "- A 1:1 sample class ratio does not represent prevalence. Environmental separation does not establish biological absence or causal habitat preference.\n"
        "- Do not treat repeated occurrence records as independent cells, interpret maps as suitability, or include identifiers/lineage/quality fields as predictors without leakage review.\n\n"
        "## Evidence artefacts\n\n"
        f"- **{len(required_tables)} CSV tables**: [`reports/eda/tables/`](../../reports/eda/tables/)\n"
        f"- **{len(required_figures)} figures**: [`reports/eda/figures/`](../../reports/eda/figures/)\n"
        f"- Machine-readable summary: [`{SUMMARY_JSON.name}`]({SUMMARY_JSON.name})\n"
        f"- Insight log: [`{INSIGHTS_MD.name}`]({INSIGHTS_MD.name})\n\n"
        "## Next evidence gate\n\n"
        "Review candidate species using independent occupied-cell support, agree an accessible marine background domain and a cell-grouped spatial validation design, then justify any feature handling within training folds. No species was selected automatically. No splitting, imputation, scaling, feature deletion or model training occurred.\n"
    )
    SUMMARY_MD.write_text(md, encoding="utf-8")
    insight_text = (
        "# OCEAVERA — Exploratory Data Analysis Insight Log\n\n"
        "This log records descriptive evidence and follow-up questions. It does not approve a modelling population, features or method.\n\n"
        "| Section | Observed evidence | Follow-up implication | Current status |\n| --- | --- | --- | --- |\n"
        f"| A | {len(df):,} rows, {len(env)} environmental definitions, {len(class_table)} period/class/cohort cells. | Preserve label meaning and screen metadata fields for leakage. | Descriptive |\n"
        f"| B | {sections['B']['environment_fully_nonmissing_features']} features are complete in the full sample; {sections['B']['environment_all_missing_features']} are all-null; {sections['B']['positive_infinity_positions'] + sections['B']['negative_infinity_positions']} infinity positions. | Review source quarantines and missingness patterns before preprocessing. | No cleaning decisions |\n"
        f"| C | {sections['C']['taxon_keys']:,} positive taxon keys; {sections['C']['distinct_positive_cells_full']:,} occupied cells; {sections['C']['distinct_positive_cell_periods_full']:,} cell-periods. | Compare candidate taxa using distinct cells and repeats, not record count alone. | No species selected |\n"
        f"| D | Complete-case six-core rows: {sections['D']['complete_six_core_rows']['complete_population']:,} full, {sections['D']['complete_six_core_rows']['eligible_species_subset']:,} eligible. | Investigate depth/coast differences as sampling-domain confounding. | Descriptive only |\n"
        f"| E | {sections['E']['high_correlation_pair_rows_at_abs_rho_ge_0_95']:,} period/cohort pair rows crossed |ρ| ≥ 0.95; {sections['E']['features_with_quarantined_periods_in_manifest']} definitions have quarantined periods. | Review feature family redundancy and dependence before any selection. | Screening only |\n"
        f"| F | Background same-taxon/period nearest-presence median {sections['F']['background_nearest_same_taxon_period_presence_km']['median']:.2f} km; maximum repeated cell-period count {sections['F']['max_source_records_per_taxon_cell_period']}. | Use spatial cell groups; review accessible domain and positional uncertainty. | Validation design open |\n\n"
        "**Target limits:** label 0 is sampled background, not a confirmed absence. Presence repeats are not statistically independent raster cells. The 2020–2026 environmental assignment is an SSP245 2020 projection assumption. Figures are not habitat-suitability predictions.\n\n"
        "**Preservation:** all 382 environmental feature definitions and source columns remain unchanged; no dataset, processing script 08–10, or model input was rewritten. Feature-selection candidates are listed for later group review only.\n"
    )
    INSIGHTS_MD.write_text(insight_text, encoding="utf-8")
    SUMMARY_JSON.write_text(json.dumps(details, indent=2, ensure_ascii=False, default=str) + "\n",
                            encoding="utf-8")
    print("[EDA] Completed Sections A–F; frozen input fingerprints match before and after.")
    print(f"[EDA] {len(required_tables)} CSV tables: {TABLES.relative_to(ROOT)}")
    print(f"[EDA] {len(required_figures)} figures: {FIGURES.relative_to(ROOT)}")
    print(f"[EDA] Readable report: {SUMMARY_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
