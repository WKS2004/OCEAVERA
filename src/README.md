# Reusable implementation

The project Python baseline is 3.14, recorded in the root
[`.python-version`](../.python-version). The current scripts remain compatible
with Python 3.10 or later. Third-party Python packages
used by code or notebooks belong in the root
[`requirements.txt`](../requirements.txt), with the selected exact version.
The current OBIS and Bio-ORACLE intake utilities use only the standard library. See the
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

**Current method:** the standard-library [`obis_occurrences.py`](data_collection/obis_occurrences.py)
downloads the complete paginated Area 230 response from the OBIS API. It
includes absence and dropped records, omits the `fields` parameter, applies no
taxon/date/depth/record filter, and saves each response body unchanged beneath
`data/raw/obis/json/` with a count/checksum manifest. Requests are sequential
and use the API's `after` cursor. A run is marked complete only when the API
total and unique record IDs agree. Interrupted or failed runs retain completed
pages and can be resumed with `--resume`.

From the repository root:

```text
python src/data_collection/obis_occurrences.py
```

The separate standard-library
[`obis_json_to_csv.py`](data_collection/obis_json_to_csv.py) converts only a
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
python src/data_collection/obis_json_to_csv.py
```

To select a particular complete run instead, pass its directory with
`--json-run`:

```text
python src/data_collection/obis_json_to_csv.py --json-run data/raw/obis/json/<run-directory>
```

## OBIS raw-to-interim handoff

[`stage_obis_csv.py`](data_preparation/stage_obis_csv.py) accepts the selected
OBIS CSV path at the first raw-to-interim boundary. Run it from the repository
root:

```text
python src/data_preparation/stage_obis_csv.py --obis-csv data/raw/obis/csv/<selected-run>.csv
```

The path is supplied once at this boundary. The script checks CSV row widths,
copies every byte unchanged, verifies the checksum and writes to the fixed
`data/interim/obis/source_validation/occurrences.csv` path with a fixed
`manifest.json` alongside it. Re-running replaces that phase's output after
validation rather than creating another run folder. Interim payloads and the
local manifest are ignored by Git.

This is structural validation and staging, not scientific cleaning: it removes
no rows or fields and does not decide exclusions, taxonomic rules, missing
values or feature extraction. Later OBIS transformations use separate stable
phase folders under `data/interim/obis/`; each script reads the preceding
phase's fixed path and writes its own fixed path without timestamps.

## Bio-ORACLE environmental source intake

[`bio_oracle_layers.py`](data_collection/bio_oracle_layers.py) is a static,
single-purpose collector. Run it from the repository root with no options:

```text
python src/data_collection/bio_oracle_layers.py
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

[`stage_bio_oracle_layers.py`](data_preparation/stage_bio_oracle_layers.py)
accepts the selected catalogue run manifest once. Run it from the repository
root and select a complete manifest under `data/raw/bio_oracle/_runs/`:

```text
python src/data_preparation/stage_bio_oracle_layers.py --run-manifest data/raw/bio_oracle/_runs/<complete-run>_bio_oracle_catalog.json
```

The script accepts only a complete D-047 catalogue run with the D-048 Sri Lanka
rectangle and requested 2000–2100 time bounds. It checks that the run counts,
layer IDs, variables and per-layer receipts agree, then checks free space on
the target drive. During copying it verifies each NetCDF signature, byte count
and SHA-256, and reports byte progress, current layer, transfer rate and ETA.
Receipt preflight progress is shown every 25 layers. To inspect the selected
run and available disk space without writing files or reading NetCDF payload
bytes, add `--dry-run`:

```text
python src/data_preparation/stage_bio_oracle_layers.py --run-manifest data/raw/bio_oracle/_runs/<complete-run>_bio_oracle_catalog.json --dry-run
```

The script writes all layer files and unchanged receipts beneath
`data/interim/bio_oracle/source_validation/<dataset-id>/`, copies the selected
catalogue run manifest, and writes a timestamp-free aggregate `manifest.json`.
The sidecar receipts retain their original raw-source references; the aggregate
manifest maps those raw paths to the interim copies.

This is structural source validation, not raster transformation or scientific
cleaning. Raw files remain unchanged. A complete replacement folder becomes
the stable output only after every layer passes validation. The preflight
requires space for the payloads and receipts plus a 64 MiB safety buffer. The
user reports a successful run; its local manifest records 356 layers, 2,392
variables and 4,017,532,960 payload bytes. The current local inventory contains
714 files totaling 4,021,176,513 bytes. The manifest and inventory were
inspected, but payload hashes were not independently recalculated during the
later UX update.

The three OBIS commands print readable status, progress and completion details
in the console. Their machine-readable provenance remains in the JSON manifests
saved alongside the raw or interim data; the converter does not print the full
receipt as JSON to the console.

The API currently reports a live total during retrieval; the actual count,
page hashes, response-body bytes and CSV fingerprint are recorded in the
[Area 230 source record](../docs/records/2026-10-08-source-obis-area-230-api-csv.md).
The failed AWS/GeoParquet attempt remains historical under [D-035](../docs/records/2026-10-07-decision-obis-area-230-geoparquet.md);
[D-036](../docs/records/2026-10-08-decision-obis-area-230-api-csv.md) selects
the current API/CSV method. The workflow does not clean, deduplicate, select
species, integrate environmental data, construct targets or model observations.

Place future preparation, spatial integration, modelling or evaluation logic
here only as those stages are authorised. Keep notebooks focused on
explanation and analysis rather than duplicated implementation.

## Member responsibilities

Reusable logic follows the working biological/target/baseline ownership of
Sanuda, environmental/integration ownership of Ushan, preprocessing/intermediate-model
ownership of Adithya and training/validation/evaluation ownership of Wanshaja.
Feature work and candidate training retain the joint ownership in the
canonical matrix. See the [complete responsibility plan](../docs/project/member-responsibilities.md)
for all activities, shared roles and handovers. Planned ownership does not
establish an artefact or completed contribution.
