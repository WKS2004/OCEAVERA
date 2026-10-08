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
| Bio-ORACLE phases | No code or runtime input selection in this branch | `interim/bio_oracle/<phase>/<artifact>` | Documented future layout only. |
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
for provenance. No cleaning rules have been applied. Bio-ORACLE is documented
only: there is no Bio-ORACLE code or staged input in this branch. Retain any
future publisher arrays in their original format and select a compatible
source-specific reader when that source is authorised.

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

The project Python baseline is 3.14, and the current OBIS collection and handoff
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

Preserve publisher files unchanged: the OBIS API's JSON pages are retained byte-for-byte; the CSV is produced separately from the complete pages and validated against them. NetCDF environmental arrays remain an anticipated example until a specific layer is verified. Extract selected raster values at modelling locations into derived tables; do not flatten complete environmental grids. Record actual formats and fingerprints in source records/manifests. COG (`.tif`) and ONNX (`.onnx`) remain optional, unfinalised future BLUEVERSE integration suggestions, not required OCEAVERA data/model formats.

## Member responsibilities

Sanuda leads biological data preparation; Ushan environmental preparation and integration; Adithya integrated-dataset cleaning. Wanshaja reviews these inputs. All four contribute to feasibility and final dataset decisions. See the [complete responsibility plan](../docs/project/member-responsibilities.md) for all activities, shared roles and handovers. Planned ownership does not establish a completed contribution; the D-036 intake result is recorded separately, and later technical work remains subject to its scope and evidence gates.
