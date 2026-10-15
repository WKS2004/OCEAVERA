# Decision D-051 — OBIS–Bio-ORACLE spatiotemporal integration rework

> Historical decision record: its original output counts and first-parseable date policy describe the 15 October snapshot. [D-052](2026-10-16-decision-integration-filtering-corrections.md) refines the current temporal and unit rules and links to the regenerated outputs and independent verification. D-051's two-script architecture and marine-polygon gate remain in force.

- **ID:** D-051
- **Date:** 15 October 2026
- **Status:** Original implementation scope retained; processing details refined by D-052; marine filtering and gridded outputs remain blocked pending a documented marine-area source
- **Decision owner:** Project group, under the user's explicit implementation request
- **Decision basis:** The user requested a complete replacement of the D-050 integration implementation and its published interim table, while retaining source datasets and historical evidence.

## Decision

Replace the initial D-050 integration with two processing scripts:

1. [`08_integrate_spatiotemporal_data.py`](../../src/data_preparation/08_integrate_spatiotemporal_data.py) builds a full row-preserving catalog and integrated GeoParquet.
2. [`09_filter_and_grid_data.py`](../../src/data_preparation/09_filter_and_grid_data.py) filters resolved years and proceeds to marine filtering and grid summaries only when a documented marine-area polygon is supplied.

Use the existing cleaned OBIS CSV and cleaned Bio-ORACLE manifest. Inventory all 356 cleaned environmental products; integrate 55 baseline products, 50 SSP245 products and the one static terrain product. Select variable names from the manifest, confirm scenario and depth against NetCDF title metadata, and use the actual NetCDF time coordinate for every temporal slice. Preserve source values with netCDF4 automatic masking and scaling enabled; do not apply `scale_factor` or `add_offset` a second time. The output catalog records source identity, checksum, variable metadata, units, depth, time coordinates and the one pre-existing cleaning review.

Preserve all 23,371 cleaned OBIS records and all 112 source fields in the full output. Resolve dates in this order: `year`, `eventDate`, `date_start`, `date_mid`, `date_end`, then `date_year`. Map 2000–2009 to the actual baseline coordinate 2000, 2010–2019 to baseline coordinate 2010, and 2020–2026 to SSP245 coordinate 2020. The SSP245 choice is an explicit decadal approximation, not an annual observation or a forecast for a specific year. Keep out-of-period, missing-date, unmatched and masked values explicit. Treat terrain as static from its NetCDF title; do not interpret its 1970 coordinate as an observation date.

Use the shared one-dimensional Bio-ORACLE axes for deterministic nearest in-extent cell matching. Retain original OBIS point geometry in EPSG:4326, zero-based raster row/column, stable cell index, cell-centre coordinates and point-to-centre distance. Do not interpolate, impute, clamp outside points or treat a raster footprint or `landmass`/`coastline` values as a marine mask.

Write the fixed stage outputs:

- `data/interim/integrated/full/integrated_observations.parquet`
- `data/interim/integrated/temporal/observations_2000_2026.parquet`
- `data/interim/integrated/marine/marine_observations.parquet` only after a sourced marine polygon is supplied
- `data/interim/integrated/gridded/grid_observations.parquet` and `species_cell_period_summary.parquet` only after the marine stage succeeds

This is a narrow D-049 exception for the integrated family because the user requested separately validated full and temporal outputs and gated marine/grid outputs. Keep fixed paths, preserve prior states through source data and code, and validate each output before replacing it. D-049 continues to govern OBIS and Bio-ORACLE interim storage.

Use only rows explicitly marked `taxonRank=species` in the species/cell/period summary. Prefer the source AphiaID and identify fallbacks in the key. `occurrence_record_count` counts OBIS records; it is not population abundance. Retain individual point rows in the gridded observations table.

## Implementation evidence

The full stage read back as **23,371 rows × 509 columns**: all 112 cleaned OBIS fields, 382 feature columns and integration metadata. It uses GeoParquet 1.1.0, EPSG:4326 point geometry and ZSTD compression. All 23,371 source coordinates matched an in-extent grid cell, and the implementation checked the axes across all 106 selected source products. The 382 feature columns represent 139 distinct NetCDF variable names across their declared depth strata and source availability. The full run verified every selected cleaned-product SHA-256 against the cleaning manifest and compared every original OBIS field after GeoParquet read-back.

The temporal stage retained **9,681 records** from 2000 through 2026: 653 in 2000–2009, 2,562 in 2010–2019 and 6,466 in 2020–2026. It excluded 10,409 records before 2000 and 3,281 with missing or invalid dates. Its read-back passed GeoParquet 1.1.0 and ZSTD checks.

The catalog preserves 356 product identities. The one `review_required` product remains flagged because the existing Bio-ORACLE cleaning review concerns an unresolved marine-mask convention and one masked environmental value within the candidate non-fill domain. The value stays null; no candidate-domain assumption was applied.

No independently documented marine-water polygon or land-sea mask was present in the local project data and records. Therefore no marine or gridded dataset was created. The OBIS marine flag and Bio-ORACLE terrain/cell coverage are not substitutes. The exact blocker and required source metadata are recorded in the [marine-filter blocker](2026-10-15-marine-filter-blocker.md). The optional mask path in the second script requires a polygon layer, CRS and publisher/source citation, then applies strict polygon containment and excludes explicit nonmarine OBIS flags.

## Supersession and attribution

This decision supersedes the D-050 implementation and retires `integrate_obis_bio_oracle.py`, `data/interim/integrated/integrated_dataset.parquet` and its branch notebook after the replacement outputs passed read-back checks. D-050 and its audit/report files remain historical evidence and are not current output references.

AI-assisted data integration and integrated-dataset cleaning are recorded under **Adithya Gunawardana**. Spatial data integration, raster-axis/cell matching, marine gating and grid geometry are recorded under **Ushan Srinuka**. This split follows the user's explicit direction and the existing responsibility matrix; it records AI-assisted work, not individual human authorship or acceptance.

## Affected records and artefacts

- [Variable catalog (Markdown)](2026-10-15-integration-variable-catalog.md) and [catalog (JSON)](2026-10-15-integration-variable-catalog.json)
- [Integration summary](2026-10-15-integration-summary.md) and [integration manifest](2026-10-15-integration-manifest.json)
- [Temporal filter report](2026-10-15-temporal-filter-report.md) and [marine-filter blocker](2026-10-15-marine-filter-blocker.md)
- [Branch work notebook](../../notebooks/branch_work/05_pipeline_data_integration_and_data_cleaning.ipynb)
- [Adithya's integration/cleaning AI-usage log](../ai-contribution/AdithyaGunawardana-ai-usage.md) and [Ushan's spatial integration AI-usage log](../ai-contribution/Ushan-Srinuka-ai-usage.md)
- [Storage guidance](../data/data-storage-and-provenance.md), [requirements](../../PROJECT_REQUIREMENTS.md), [readiness](../project/repository-readiness-and-alignment.md), [decision register](../project/decision-register.md), [data guide](../../data/README.md) and [source guide](../../src/README.md)
