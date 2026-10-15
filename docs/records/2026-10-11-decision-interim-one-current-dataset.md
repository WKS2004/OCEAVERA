# Decision D-049 — One current interim dataset per data family

- **ID:** D-049
- **Date:** 11 October 2026
- **Question:** How many derived dataset versions should remain under `data/interim/`?
- **Context:** D-038 established separate, stable folders for interim phases. The user clarified that only one current dataset per data family should be retained because raw inputs and scripts can regenerate earlier states. The user further clarified that phase folders must not coexist as siblings: OBIS `source_validation/` must be replaced by `cleaning/`, and the same replacement rule applies when Bio-ORACLE cleaning is implemented. Before the clarification, OBIS had both `source_validation/` and `cleaning/` directories, plus multiple CSV outputs.
- **Evidence and source:** The OBIS source snapshot remains in `data/raw/obis/csv/` with its acquisition provenance. The OBIS cleaner and source-validation utility are reproducible scripts. The Bio-ORACLE handoff stages all layers and receipts into a temporary directory and replaces the stable collection directory only after the complete transfer passes checks. The repository currently has no integrated interim dataset.
- **Decision:** Maintain one current interim dataset per family. Where a dataset family is represented by stage directories, retain exactly one active stage directory directly beneath the family directory. A later stage replaces that directory only after the complete new result has been generated and validated:
  - **OBIS:** the only interim subdirectory is `data/interim/obis/cleaning/`. It contains `occurrences_cleaned.csv`, the JSON reports and `source_validation_manifest.json`. Source validation writes its manifest into this directory; it does not create a sibling `source_validation/` directory.
  - **Bio-ORACLE:** at the time of the original decision application, the single stage directory was `data/interim/bio_oracle/source_validation/`, containing the collection bundle under its dataset ID. Its many NetCDF layer files and receipts are components of one collection. The validated cleaning output must replace this directory rather than sit beside it.
  - **Integrated dataset:** one current table at `data/interim/integrated/integrated_dataset.parquet`, using GeoParquet when the output retains spatial geometry. This is a planned destination; no integrated dataset currently exists.

  A single-table family may use its fixed dataset-file destination instead. Do not retain sibling phase directories, previous derived dataset versions or timestamped interim run folders. Keep manifests, diagnostics and run summaries with the one current dataset; they are support metadata, not additional dataset versions. Preserve timestamped raw snapshots and their provenance.
- **Rationale:** The user prefers a simple interim layout and can reproduce earlier intermediate states from the preserved raw sources and scripts. Replacing only after a new result is successfully generated and validated keeps the current state usable if a run fails, while preserving raw source history.
- **Consequences and limitations:** OBIS has exactly one `cleaning/` directory with its CSV, source-validation manifest and reports. Bio-ORACLE has exactly one `cleaning/` directory with 356 byte-verified NetCDF copies and its manifest and array summary. The 714-file source-validation bundle was rechecked against its sources and receipts before replacement. One Bio-ORACLE product remains flagged for review; the integrated family has a planned single-file destination and no current output. Reproduction depends on retaining the necessary raw inputs and compatible scripts; this decision does not create an integrated dataset or alter downstream scientific processing.
- **Status:** Accepted by the user and applied to both OBIS and Bio-ORACLE. The current Bio-ORACLE implementation and evidence are recorded in the [cleaning record](2026-10-11-bio-oracle-cleaning.md). The integrated output remains planned and ungenerated.
- **Affected documents and artefacts:** [OBIS data guide](../../data/README.md), [storage conventions](../data/data-storage-and-provenance.md), [source guide](../../src/README.md), [ML workflow](../ml/ml-workflow-and-evidence-gates.md), [readiness review](../project/repository-readiness-and-alignment.md), [OBIS source validator](../../src/data_preparation/03_stage_obis_csv.py), [OBIS cleaner](../../src/data_preparation/04_clean_obis_occurrences_csv.py), [Bio-ORACLE source staging script](../../src/data_preparation/06_stage_bio_oracle_layers.py), [Bio-ORACLE cleaner](../../src/data_preparation/07_clean_bio_oracle_layers.py), and [Bio-ORACLE cleaning record](2026-10-11-bio-oracle-cleaning.md).
- **Supersedes / superseded by, if applicable:** Supersedes D-038's interim convention to retain distinct dataset outputs for each processing phase. D-038 remains historical context for source selection and the original intake workflow.

## Directory layout clarification — 11 October 2026

The source-validation manifest now lives at `data/interim/obis/cleaning/source_validation_manifest.json`, beside the cleaned CSV and JSON reports. Both OBIS scripts use this single directory. The scripts were rerun successfully; the cleaned result remains 23,371 rows × 112 columns, and the older OBIS `source_validation/` directory was removed after the new manifest and outputs were verified.

## Bio-ORACLE application — 11 October 2026

The first Bio-ORACLE cleaning run on 11 October read and checked all 356 raw
NetCDF products and 2,392 variable instances. Before replacing the earlier
source-validation folder, it rehashed and reconciled all 714 staged files
with the raw payloads, receipts and catalogue run manifest; there were no
missing, additional or mismatched files. That first run left only
`manifest.json` and `cleaning_summary.json` in `cleaning/`; the follow-up
below records the materialized dataset bundle. The scan found 355 validated
products and one review item for a `kdpar_mean_range` fill cell at the 2000
baseline coordinate. The staging script recreates the source-validation
state by replacing the sole current stage, never by adding a sibling
directory. No environmental integration is included in this application.

## Bio-ORACLE interim materialization follow-up — 12 October 2026

After the user noted that `data/interim/bio_oracle/cleaning/` contained only
JSON reports and no NetCDF dataset files, the cleaner was updated to retain
356 byte-for-byte products alongside the reports. The first follow-up did
not implement the complete handoff: its cleaner required an existing
`cleaning/` directory even though the staging script had just produced
`source_validation/`. The corrected workflow scans the staged payloads and
renames that same directory to `cleaning/` after validation, with products
directly under `cleaning/<dataset-id>/`. This keeps one active interim stage
and avoids an extra full dataset copy. The raw NetCDF files remain unchanged;
the single `kdpar_mean_range` fill remains flagged for review. See the
[Bio-ORACLE cleaning record](2026-10-11-bio-oracle-cleaning.md) for current
verification evidence.
