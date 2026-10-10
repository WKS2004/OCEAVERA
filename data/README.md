# Data directory

| Directory | Purpose |
| --- | --- |
| `raw/` | Unmodified source downloads in the formats actually supplied |
| `interim/` | Reproducible cleaning, extraction and spatial integration products; GeoParquet for compatible spatial tables |
| `processed/` | Reviewed analysis-ready tables; GeoParquet where geometry is retained, Parquet for compatible non-spatial ML tables |

## Paths and phase folders

Raw acquisition folders may include timestamps so a source snapshot and its
manifest stay together. The OBIS raw-to-interim entry point accepts the chosen
CSV path once; [`stage_obis_csv.py`](../src/data_preparation/stage_obis_csv.py)
validates and copies it to the current phase path:

| Source or stage | Input selection | Stable destination or layout | Status |
| --- | --- | --- | --- |
| OBIS source validation | `--obis-csv <path>` | `interim/obis/source_validation/occurrences.csv` and its `manifest.json` | Code implemented; it makes a byte-for-byte copy and does not apply scientific cleaning. |
| Later OBIS phases | Fixed input from the previous phase | `interim/obis/<phase>/<artifact>` | Path pattern adopted; later phase scripts are not implemented. |
| Bio-ORACLE source responses | Run `python src/data_collection/bio_oracle_layers.py` with no options | `raw/bio_oracle/<dataset-id>/<UTC timestamp>_all-variables.nc` plus per-layer query manifests and a run manifest | The latest D-047/D-048 run completed 356/356 grids and all 2,392 variables (4,017,532,960 payload bytes); every payload passed byte-count, SHA-256 and NetCDF-signature checks, with no failed or pending layer. Earlier complete and partial snapshots were deleted at the user's request. See the [dated source record](../docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) for run history. The earlier D-046 test payload and its local manifest were also deleted at the user's request. |
| Bio-ORACLE source validation | `--run-manifest <complete-run>`; add `--dry-run` for preflight | `interim/bio_oracle/source_validation/<dataset-id>/` plus `catalog_run_manifest.json` and `manifest.json` | User-reported run completed; the local aggregate manifest records all 356 layers and 2,392 variables (4,017,532,960 payload bytes). This is structural validation and byte-for-byte copying, not scientific processing. |
| Later Bio-ORACLE phases | Fixed input from the preceding phase | `interim/bio_oracle/<phase>/<artifact>` | Path pattern adopted; scientific processing and integration scripts are not implemented. |
| Cross-source integration | Fixed inputs from the relevant source phases | A fixed integration-stage path under `interim/` | Not implemented. |
| Analysis-ready data | Fixed input from the completed integration stage | `processed/modeling_dataset.parquet` | Stable destination convention; not generated. |

`<phase>` and `<artifact>` are placeholders for meaningful names selected when
each stage is implemented; do not copy a raw timestamp into a derived path.
Each new transformation stage gets its own stable subfolder beneath its source
directory. A stage script reads the fixed output of the preceding stage and
writes its own fixed destination. Re-running a stage replaces its output only
after successful validation; it does not create another run folder.

The OBIS entry point accepts CSVs under `data/raw/obis/`, validates row widths,
preserves source bytes, rows and fields, and writes a timestamp-free manifest
inside its phase folder. That manifest may cite the timestamped raw source path
for provenance. No cleaning rules have been applied. Under D-047 and D-048,
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
The intake scripts do not clean, select taxa, integrate sources or create an
analysis-ready dataset. The new handoff command only validates and stages
explicitly selected raw CSVs; cleaning and source integration remain unrun.

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
