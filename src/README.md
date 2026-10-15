# Reusable implementation

The project Python baseline is 3.14, recorded in the root
[`.python-version`](../.python-version). The current scripts remain compatible
with Python 3.10 or later. Third-party Python packages
used by code or notebooks belong in the root
[`requirements.txt`](../requirements.txt), with the selected exact version.
OBIS and Bio-ORACLE intake and cleaning use the standard library. The
spatiotemporal integration uses pinned NumPy, pandas, netCDF4, GeoPandas and
PyArrow for source extraction and GeoParquet publication/read-back. See the
[dependency policy](../CONTRIBUTING.md#python-dependencies) for the package
manifest and update rule. Users can install the listed requirements with:

```text
python -m pip install -r requirements.txt
```

Follow the [root Conda setup instructions](../README.md#create-the-conda-environment)
to create and activate the `OCEAVERA` environment with Python 3.14. These
commands are user-led. Agents require explicit prior user authorisation before
creating, modifying or
removing an environment or installing, upgrading or removing packages. This
repository does not store a Python environment.

## Script run order

The numeric prefixes show the full pipeline order when rebuilding the derived
outputs. The OBIS and Bio-ORACLE collection paths can be prepared separately;
the integration step needs both cleaned inputs.

1. [`01_obis_occurrences.py`](data_collection/01_obis_occurrences.py) — download the OBIS occurrence pages.
2. [`02_obis_json_to_csv.py`](data_collection/02_obis_json_to_csv.py) — convert a complete OBIS JSON run to CSV.
3. [`03_stage_obis_csv.py`](data_preparation/03_stage_obis_csv.py) — validate the selected raw CSV and write its source manifest.
4. [`04_clean_obis_occurrences_csv.py`](data_preparation/04_clean_obis_occurrences_csv.py) — create the cleaned OBIS table.
5. [`05_bio_oracle_layers.py`](data_collection/05_bio_oracle_layers.py) — retrieve the selected Bio-ORACLE products.
6. [`06_stage_bio_oracle_layers.py`](data_preparation/06_stage_bio_oracle_layers.py) — validate and stage the selected product bundle.
7. [`07_clean_bio_oracle_layers.py`](data_preparation/07_clean_bio_oracle_layers.py) — verify and publish the current cleaned product bundle.
8. [`08_integrate_spatiotemporal_data.py`](data_preparation/08_integrate_spatiotemporal_data.py) — join the cleaned occurrences to the selected environmental products.
9. [`09_filter_and_grid_data.py`](data_preparation/09_filter_and_grid_data.py) — create temporal/marine outputs and grid summaries using the reusable GSHHG reference and recorded uncertainty policy.

**Current method:** the standard-library [`01_obis_occurrences.py`](data_collection/01_obis_occurrences.py)
downloads the complete paginated Area 230 response from the OBIS API. It
includes absence and dropped records, omits the `fields` parameter, applies no
taxon/date/depth/record filter, and saves each response body unchanged beneath
`data/raw/obis/json/` with a count/checksum manifest. Requests are sequential
and use the API's `after` cursor. A run is marked complete only when the API
total and unique record IDs agree. Interrupted or failed runs retain completed
pages and can be resumed with `--resume`.

From the repository root:

```text
python src/data_collection/01_obis_occurrences.py
```

The separate standard-library
[`02_obis_json_to_csv.py`](data_collection/02_obis_json_to_csv.py) converts only a
complete, checksum-verified JSON run. It writes the union of every top-level
field and every record to `data/raw/obis/csv/`, serialises nested arrays and
objects as compact JSON strings, and checks each CSV row against the raw JSON.
By default it uses the newest complete run; `--json-run` selects a specific
run directory. The CSV includes all top-level API fields plus the 68 named
columns on OBIS's Data Access page; missing documented keys are blank, and
`AphiaID` mirrors the API's `aphiaID` while preserving that original column.
`--replace-existing` refreshes output only when its receipt proves it comes
from the same JSON run. Neither script writes occurrence data to
`data/interim/` or deletes earlier runs. The exact raw responses remain the
lossless source for the CSV copy.

From the repository root, convert the newest complete JSON run with:

```text
python src/data_collection/02_obis_json_to_csv.py
```

To select a particular complete run instead, pass its directory with
`--json-run`:

```text
python src/data_collection/02_obis_json_to_csv.py --json-run data/raw/obis/json/<run-directory>
```

## OBIS raw-to-interim handoff

[`03_stage_obis_csv.py`](data_preparation/03_stage_obis_csv.py) accepts the selected
OBIS CSV path at the first raw-to-interim boundary. Run it from the repository
root:

```text
python src/data_preparation/03_stage_obis_csv.py --obis-csv data/raw/obis/csv/<selected-run>.csv
```

The path is supplied once at this boundary. The script checks CSV row widths,
calculates the source checksum and writes its dimensions and provenance to
`data/interim/obis/cleaning/source_validation_manifest.json`. It does not copy
or modify the raw CSV. Re-running safely replaces the manifest. The `cleaning/`
directory is shared with the cleaner, so source validation does not create a
sibling `source_validation/` directory.

This is structural validation and staging, not scientific cleaning: it removes
no rows or fields and does not decide exclusions, taxonomic rules, missing
values or feature extraction. Under [D-049](../docs/records/2026-10-11-decision-interim-one-current-dataset.md),
`data/interim/obis/` has only the `cleaning/` directory, which contains the
source manifest, cleaned CSV and JSON diagnostics. Pipeline scripts regenerate
prior states from raw inputs when needed instead of retaining sibling
phase directories.

## OBIS occurrence cleaning

[`04_clean_obis_occurrences_csv.py`](data_preparation/04_clean_obis_occurrences_csv.py)
reads the raw CSV identified by the verified source-validation manifest and
writes the sole OBIS interim output directory,
`data/interim/obis/cleaning/`. It contains `occurrences_cleaned.csv`,
`column_completeness.json`, `cleaning_summary.json` and
`source_validation_manifest.json`.
Run it from the repository root:

```text
python src/data_preparation/04_clean_obis_occurrences_csv.py
```

The configurable column threshold is 10% usable values after field-specific sentinels are excluded. Essential OBIS
fields are retained even below that threshold. Row checks remove records
explicitly marked `dropped=true`, with invalid coordinates, or with no usable
taxonomic name or identifier at any rank, including taxonID. No row-wide missingness cutoff is applied; optional dates, species-level fields and metadata are reported separately. Only exact full-source duplicate rows are removed.
Absence, marine classification, quality flags, repeated IDs and combinations
that become identical after column reduction are preserved. No values are
imputed or normalised, and all taxa remain in the output. See the
[cleaning decision and results](../docs/records/2026-10-11-obis-area-230-cleaning.md)
and the [earlier column-screen record](../docs/records/2026-10-10-obis-area-230-column-screening.md).

## Bio-ORACLE environmental source intake

[`05_bio_oracle_layers.py`](data_collection/05_bio_oracle_layers.py) is a static,
single-purpose collector. Run it from the repository root with no options:

```text
python src/data_collection/05_bio_oracle_layers.py
```

It uses the rectangle formed from the Marine Regions Sri Lankan EEZ v12
extrema: 77.02333333333333–85.23291666666667° E and
2.5665–11.44883333333333° N. This is a rectangle, not the irregular EEZ
polygon; no marine mask is applied. The script requests the
2000-01-01 through 2100-01-01 UTC window. At each run it inventories the live
Bio-ORACLE catalogue internally and downloads every matching v3 grid, all of
its data variables, and all values on additional axes such as depth.

The time window describes the requested bounds, not annual coverage. The
previously retrieved metadata exposed baseline labels at 2000 and 2010 and SSP
labels from 2020 through 2090, with no separate 2100 coordinate. The script
uses only values Bio-ORACLE supplies; it does not create missing years. SSP
data are projections. The collection rectangle can include land or waters
outside the EEZ polygon.

Running the script starts the full retrieval after catalogue metadata have
been checked. It has no preview or single-layer mode. If any matching layer
cannot be planned from its metadata, it stops before saving payloads. Each
publisher response is preserved unchanged under
`data/raw/bio_oracle/<dataset-id>/` with a query/checksum manifest; an
incremental run manifest records layer statuses. Matching payloads are reused
only when their query, bounds, time range, byte count and SHA-256 agree.
The terminal reports the collection stages, checks reusable files, shows
periodic transfer progress, retries transient response failures for up to three
attempts per layer, and finishes with complete/failed layer and variable
counts, payload size, elapsed time and the run-manifest path. Responses above
512 MiB are rejected. The final Python-file run selected 356 regional grids and
2,392 variables, downloaded 4,017,532,960 payload bytes and completed with no
failed or pending layers. Every payload passed a byte-count, SHA-256,
NetCDF-signature and receipt-scope audit. The earlier complete snapshot and the
subsequent partial manual snapshot were deleted at the user's request; their
history and the final run manifest are detailed in the [regional intake source
record](../docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md).

The earlier D-046 test payload and its manifest were also deleted at the user's
request; historical measurements remain in the [source
record](../docs/records/2026-10-09-source-bio-oracle-oceantemperature.md). The
retained OBIS Area 230 CSV has measured coordinate extrema of
2.93300008774–11.31666667° N and 77.133–85.06° E across 23,934 records. These
observed-record bounds are documented in the [OBIS source record](../docs/records/2026-10-08-source-obis-area-230-api-csv.md);
they are not the environmental collection rectangle selected in D-048. The
selected region and its provenance are recorded in the [D-048
record](../docs/records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md) and
[Marine Regions extent record](../docs/records/2026-10-09-source-marine-regions-sri-lanka-eez-bounds.md).

## Bio-ORACLE raw-to-interim handoff

[`06_stage_bio_oracle_layers.py`](data_preparation/06_stage_bio_oracle_layers.py)
accepts the selected catalogue run manifest once. Run it from the repository
root and select a complete manifest under `data/raw/bio_oracle/_runs/`:

```text
python src/data_preparation/06_stage_bio_oracle_layers.py --run-manifest data/raw/bio_oracle/_runs/<complete-run>_bio_oracle_catalog.json
```

The script accepts only a complete D-047 catalogue run with the D-048 Sri Lanka
rectangle and requested 2000–2100 time bounds. It checks that the run counts,
layer IDs, variables and per-layer receipts agree, then checks free space on
the target drive. During copying it verifies each NetCDF signature, byte count
and SHA-256, and reports byte progress, current layer, transfer rate and ETA.
Receipt preflight progress is shown every 25 layers. To inspect the selected
run and available disk space without writing files, add `--dry-run`. If an
interim stage already exists, the script also verifies its recorded payload
hashes before reporting whether that stage can safely be replaced:

```text
python src/data_preparation/06_stage_bio_oracle_layers.py --run-manifest data/raw/bio_oracle/_runs/<complete-run>_bio_oracle_catalog.json --dry-run
```

The script writes all layer files and unchanged receipts beneath
`data/interim/bio_oracle/source_validation/<dataset-id>/`, copies the selected
catalogue run manifest, and writes a timestamp-free aggregate `manifest.json`.
The sidecar receipts retain their original raw-source references; the aggregate
manifest maps those raw paths to the interim copies. If `cleaning/` is the
current stage, a successful rerun replaces it with this earlier
source-validation state so the family never has sibling stage directories.

This is structural source validation, not raster transformation or scientific
cleaning. Raw files remain unchanged. A complete replacement bundle becomes
current only after every layer passes validation. Successful source-staging
publication replaces the one current stage directory as a whole. Under D-049,
this can regenerate the earlier `source_validation/` state from raw inputs;
the validated cleaning stage can then be regenerated from that bundle.
The preflight
requires space for the payloads and receipts plus a 64 MiB safety buffer. The
source-validation run's local manifest recorded 356 layers, 2,392 variables
and 4,017,532,960 payload bytes; its interim inventory contained 714 files
totaling 4,021,176,513 bytes. Payload hashes were not recalculated during an
earlier UX update. Before the later cleaning transition replaced that stage,
all 714 staged files were independently rechecked against their sources and
receipts.

## Bio-ORACLE environmental cleaning

[`07_clean_bio_oracle_layers.py`](data_preparation/07_clean_bio_oracle_layers.py)
scans all products referenced by the current Bio-ORACLE manifest and publishes
the validated byte-for-byte NetCDF products under
`data/interim/bio_oracle/cleaning/<dataset-id>/`, alongside `manifest.json`
and `cleaning_summary.json`. When the sole current stage is
`source_validation/`, the cleaner scans those existing products and promotes
that directory to `cleaning/` by rename after the scan succeeds. Full per-layer
diagnostics are spooled during scanning to bound RAM; no second dataset copy
is made. Raw publisher files remain unchanged. Run staging, then cleaning,
from the repository root:

```text
python src/data_preparation/06_stage_bio_oracle_layers.py --run-manifest data/raw/bio_oracle/_runs/<catalog-run>.json
python src/data_preparation/07_clean_bio_oracle_layers.py
```

The standard-library reader inspects every NetCDF header and array, then checks
file and receipt inventories and checksums, variable metadata and fill values,
finite/range statistics, coordinate order and grid alignment, CRS, temporal
coordinates, candidate-domain consistency, and exact duplicate arrays. Each
interim NetCDF copy is verified against its raw size and SHA-256 before the
current stage is replaced. A repeat run rehashes raw products and receipts,
verifies interim product hashes, and reuses the saved array diagnostics. Add
`--force-full-scan` to read every array again. The default run makes no network
requests. It preserves source values when no verified correction is justified.

The current evidence covers 356/356 readable products and 2,392 variable
instances (139 names): all 356 NetCDF products are materialized in interim,
355 are validated/reused and one requires review because `kdpar_mean_range`
has one fill cell in its 2000 slice. Interim products are byte-identical to
raw because no correction was justified; no products were excluded. Fourteen groups of
identical all-zero sea-ice summaries and the sparse `coastline` layer are
reported without deduplication or interpreting their fill cells as continuous
marine missingness. The `landmass` non-fill pattern matches 24,503 candidate
cells, but its numeric land/water convention is undocumented, so the code does
not treat that pattern as an authoritative marine mask. See the [cleaning
record](../docs/records/2026-10-11-bio-oracle-cleaning.md) for the complete
evidence and limits.

## OBIS–Bio-ORACLE spatiotemporal integration

Run the two scripts in the existing WSL OCEAVERA Python 3.14 environment:

```bash
python src/data_preparation/08_integrate_spatiotemporal_data.py
python src/data_preparation/09_filter_and_grid_data.py
```

Script 08 inventories 356 products and reads 106 selected baseline/SSP245/static products. It preserves all 23,371 cleaned OBIS observations and 112 original fields, adds 382 environmental feature columns and writes the full GeoParquet. Actual NetCDF coordinates establish time and grid choices; automatic masking/scaling is applied once.

Original baseline absolute tas metadata conflicts with decoded values, while original tas_range and clt_sd have unresolved semantics. Their affected period values are quarantined as null, with columns and source metadata preserved. SSP245 absolute Celsius temperatures stay unchanged. Counts of expected usable features exclude these quarantines. Numeric OBIS date_start/date_mid/date_end always use milliseconds; year/date_year use years. There are 22 true ambiguous-date records and 9,681 temporal rows.

Script 09 independently reads the completed full GeoParquet and saved grid axes. It never imports Script 08 or reads environmental arrays. Ordinary execution finds data/interim/geography/sri_lanka_marine_water.gpkg and its tracked source provenance. When absent but the documented local GSHHG archive exists, it prepares that reference once; routine runs do not download sources.

The full-resolution GSHHG water mask uses the established collection rectangle without EEZ clipping. Script 09 applies Policy B: valid JSON flags without exact `ON_LAND` or `MARINE_UNSURE`, and a point strictly inside GSHHG marine water. Known uncertainty footprints crossing land/coast (1,025) or extending beyond reference coverage (29) are retained and flagged; 709 known footprints are fully within water and 590 uncertainties are unknown. The current output has 2,353 marine water-centre candidates, the same 2,353 individual grid records, 2,009 identifier-bearing species-rank records, 362 occupied cells and 1,389 species/cell/period summaries. The strict D-053 policy yielded 1,299 marine rows by excluding those 1,054 known crossing/outside footprints; its evidence is archived as historical.

All five output tables are interim GeoParquet 1.1.0, EPSG:4326, ZSTD under data/interim/integrated/. Source records and point geometries are preserved. Grid polygons use persisted coordinate-centre midpoints and stable cell IDs. No minimum species/cell thresholds, targets or model preprocessing are applied.

See the [D-054 Policy B decision](../docs/records/2026-10-16-decision-policy-b-marine-water-centre.md), [execution report](../docs/records/2026-10-16-policy-b-execution-report.md), [D-053 historical report](../docs/records/2026-10-16-integration-final-technical-report.md), [manifest](../docs/records/2026-10-16-integration-manifest.json), [catalogue](../docs/records/2026-10-16-integration-variable-catalog.json), [independent source comparison](../docs/records/2026-10-16-independent-environmental-verification.md) and [current spatial report](../docs/records/2026-10-16-spatial-grid-report.md).

Progress and concise results are printed to the console. Detailed machine-readable evidence stays in docs/records/. Optional path overrides and Script 08's read-only preflight remain available:

```bash
python src/data_preparation/08_integrate_spatiotemporal_data.py --help
python src/data_preparation/08_integrate_spatiotemporal_data.py --dry-run
python src/data_preparation/09_filter_and_grid_data.py --help
```

The three OBIS commands print readable status, progress and completion details
in the console. Their machine-readable provenance remains in the JSON manifests
saved alongside the raw or interim data; the converter does not print the full
receipt as JSON to the console.

The API currently reports a live total during retrieval; the actual count,
page hashes, response-body bytes and CSV fingerprint are recorded in the
[Area 230 source record](../docs/records/2026-10-08-source-obis-area-230-api-csv.md).
The failed AWS/GeoParquet attempt remains historical under [D-035](../docs/records/2026-10-07-decision-obis-area-230-geoparquet.md);
[D-036](../docs/records/2026-10-08-decision-obis-area-230-api-csv.md) selects
the current API/CSV method. These acquisition scripts do not select species,
construct targets or model observations; spatial integration is implemented
in the two scripts above.

Place later target construction, modelling or evaluation logic here only as
those stages are authorised. Keep notebooks focused on explanation and
analysis rather than duplicated implementation.

## Member responsibilities

Reusable logic follows the working biological/target/baseline ownership of
Sanuda, environmental/integration ownership of Ushan, preprocessing/intermediate-model
ownership of Adithya and training/validation/evaluation ownership of Wanshaja.
Feature work and candidate training retain the joint ownership in the
canonical matrix. See the [complete responsibility plan](../docs/project/member-responsibilities.md)
for all activities, shared roles and handovers. Planned ownership does not
establish an artefact or completed contribution.
