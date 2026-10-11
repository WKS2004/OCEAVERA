# Data directory

| Directory | Purpose |
| --- | --- |
| `raw/` | Unmodified source downloads in the formats actually supplied |
| `interim/` | Reproducible cleaning, extraction and spatial integration products; GeoParquet for compatible spatial tables |
| `processed/` | Reviewed analysis-ready tables; GeoParquet where geometry is retained, Parquet for compatible non-spatial ML tables |

## Interim dataset policy

Under [D-049](../docs/records/2026-10-11-decision-interim-one-current-dataset.md),
`data/interim/` holds one current dataset per family. Where a family uses stage
directories, only the active stage directory remains directly beneath that
family path; a later stage replaces it only after its complete output passes
validation. Do not keep sibling phase directories. Prior interim dataset
versions are not retained because raw sources and scripts allow a state to be
regenerated.
Timestamped raw snapshots and provenance remain unchanged. Manifests,
completeness reports and run summaries are support metadata, not additional
dataset versions.

| Dataset family | Current interim dataset or planned destination | Status |
| --- | --- | --- |
| OBIS | One stage directory: `interim/obis/cleaning/`, containing `occurrences_cleaned.csv`, JSON reports and `source_validation_manifest.json` | This is the only directory directly under `interim/obis/`. The source validator writes its manifest here; it does not create a sibling `source_validation/` directory. Current output: 23,371 rows × 112 columns. See the [cleaning record](../docs/records/2026-10-11-obis-area-230-cleaning.md). |
| Bio-ORACLE | Current stage directory: `interim/bio_oracle/source_validation/<dataset-id>/` | Its NetCDF files and receipts/manifests are one collection bundle. `source_validation/` is the only current stage directory under `interim/bio_oracle/`. When cleaning is implemented, its validated `cleaning/` output must replace the current directory rather than be added beside it. The current manifest records 356 layers and 2,392 variables (4,017,532,960 payload bytes). |
| Integrated dataset | `interim/integrated/integrated_dataset.parquet` | Planned single current table; use GeoParquet when the selected integrated output retains spatial geometry. No integrated interim dataset exists yet. |
| Analysis-ready dataset | `processed/modeling_dataset.parquet` | Stable destination convention; not generated. |

The OBIS validation utility accepts a CSV under `data/raw/obis/`, checks CSV
row widths, calculates its SHA-256 and dimensions, and atomically writes
`interim/obis/cleaning/source_validation_manifest.json`. It does not copy or
modify the raw CSV or create a separate source-validation directory. The
cleaner verifies that manifest and source, then writes the cleaned CSV, a JSON
completeness report and a JSON run summary into that same sole `cleaning/`
directory. It keeps
protected fields and other columns with at least 10% usable values after
field-specific sentinels are excluded. Rows require valid coordinates and a
taxonomic name or identifier at any rank; explicit `dropped=true` records and
exact full-source duplicates are excluded. Missing dates, species-level
fields, coordinate uncertainty and optional metadata do not exclude rows. The
cleaner does not filter by `absence`, `marine` or quality flags. The prior 90%
screen and first row-filter experiment remain historical in their [dated
records](../docs/records/2026-10-10-obis-area-230-column-screening.md) and
[row-cleaning record](../docs/records/2026-10-10-obis-area-230-cleaning.md);
the current run is documented in the [cleaning
record](../docs/records/2026-10-11-obis-area-230-cleaning.md).
Under D-047 and D-048,
[`bio_oracle_layers.py`](../src/data_collection/bio_oracle_layers.py) is a
fixed, no-option collector. A run inventories the live catalogue, then
downloads every matching Bio-ORACLE v3 grid and all its data variables for the
EEZ-extrema rectangle and 2000–2100 request window. The rectangle may include
land and waters outside the irregular EEZ polygon; no spatial mask is applied.
Bio-ORACLE supplies decade-level values rather than annual records, and the
download includes only available coordinates within the requested time window.
The latest user-requested Python-file run completed all 356 planned layers and
2,392 variables. Independent checks matched every payload's size, SHA-256,
NetCDF signature and recorded request scope; no failed, pending or partial
files remain. The source record retains the earlier partial run as history and
identifies the current run manifest and audit evidence.
The earlier D-046 test response was also deleted with its local manifest; its
historical measurements remain in the [source
record](../docs/records/2026-10-09-source-bio-oracle-oceantemperature.md).
The user reports running the Bio-ORACLE handoff. The local
`interim/bio_oracle/source_validation/` inventory contains 714 files totaling
4,021,176,513 bytes; its aggregate manifest records run
`20261009T163625858012Z`, 356 layers, 2,392 variables and 4,017,532,960 bytes
of NetCDF payloads. That manifest and file inventory were inspected, but the
payload SHA-256 values were not independently recalculated during the later UX
update. The handoff preserves the raw files and does not perform scientific
processing or integration.

**Current collection:** D-036 uses the OBIS API to save every Area 230
occurrence response unchanged under `raw/obis/json/`, then converts a
verified-complete run to `raw/obis/csv/`. The query includes absence and
dropped records and applies no taxon, date, depth, quality or record-count
filter. Both folders are explicitly kept under `raw/` by the user; the CSV is
a tabular copy and the exact JSON pages remain the source. The 8 October run
contains 23,934 API records across 24 pages and a 23,934-row, 230-column CSV;
the OBIS area page's 23,327 count matches API records with both `absence` and
`dropped` false. The other 607 flagged records are deliberately included.

The earlier two bounded feasibility samples and historical API JSON/CSV
payloads were removed at the user's request. The later AWS/GeoParquet attempt
failed its final field check and retained no output; its advertised object
sizes and unknown transfer are documented in the [failure record](../docs/records/2026-10-08-obis-area-230-export-attempt.md).
The current API acquisition outcome and checksums are recorded in the
[Area 230 source record](../docs/records/2026-10-08-source-obis-area-230-api-csv.md).
The acquisition scripts do not select taxa, integrate sources or create an
analysis-ready dataset. The OBIS validation command records the selected raw
CSV's fingerprint; the cleaning script applies the bounded source-status and
coordinate exclusions documented above. Species-level review, remaining
cleaning decisions and source integration remain pending.

The existing `raw/`, `interim/` and `processed/` paths serve the proposed Bronze, Silver and Gold lifecycle roles respectively; no duplicate lifecycle directories are planned.

Data payloads are excluded from Git by default. Review coordinate sensitivity before retaining or sharing marine occurrence data. Put tracked manifests, dictionaries, citations and processing notes in `docs/records/` under the [record conventions](../CONTRIBUTING.md#project-evidence-records). See [data storage and provenance](../docs/data/data-storage-and-provenance.md) before acquiring or sharing data. The [source manifest](../docs/templates/data-source-record.md) records individual resources; the [dictionary](../docs/templates/data-dictionary.md) describes the integrated dataset.

The project Python baseline is 3.14, and the current data-intake and handoff
scripts remain compatible with Python 3.10 or later while using only the
standard library. If a future data-preparation stage adds a
third-party Python package, declare its exact version in the root
[`requirements.txt`](../requirements.txt) and update the
[setup instructions](../CONTRIBUTING.md#python-dependencies) in the same change.
The documented Conda environment for running current Python tooling is named
`OCEAVERA`; its version comes from the root [`.python-version`](../.python-version).
Follow the user-led setup steps in the [root README](../README.md#create-the-conda-environment).
Agents require explicit prior user authorisation before creating, modifying or
removing an environment or installing, upgrading or removing packages. This
repository does not store a Python environment; see the [contributor policy](../CONTRIBUTING.md#python-dependencies).

Preserve publisher files unchanged: the OBIS API's JSON pages are retained byte-for-byte; the CSV is produced separately from the complete pages and validated against them. The first complete Bio-ORACLE snapshot and a later partial snapshot were deleted at the user's request. The latest Python-file run has all 356 regional NetCDF payloads and 2,392 variables, and the independent transfer audit matched each payload with its receipt. The tracked [source record](../docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) preserves all run histories and the detailed audit. The current ERDDAP axes expose baseline coordinates at 2000/2010 and SSP coordinates at 2020–2090, not a 2100 snapshot. Extract selected raster values at modelling locations into derived tables; do not flatten complete environmental grids. Record actual formats and fingerprints in source records/manifests. COG (`.tif`) and ONNX (`.onnx`) remain optional, unfinalised future BLUEVERSE integration suggestions, not required OCEAVERA data/model formats.

## Member responsibilities

Sanuda leads biological data preparation; Ushan environmental preparation and integration; Adithya integrated-dataset cleaning. Wanshaja reviews these inputs. All four contribute to feasibility and final dataset decisions. See the [complete responsibility plan](../docs/project/member-responsibilities.md) for all activities, shared roles and handovers. Planned ownership does not establish a completed contribution; the D-036 intake result is recorded separately, and later technical work remains subject to its scope and evidence gates.
