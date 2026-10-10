# Data storage and provenance

This document defines the OCEAVERA data and model-artefact storage conventions. The conventions guide future work; they do not establish that a model has been trained or an integration has been implemented. Two limited OBIS feasibility samples were reviewed and their raw payloads were later removed. An earlier Area 230 API JSON/CSV retrieval was also removed at the user's request. D-035's AWS GeoParquet route was later attempted, failed its final field-schema check and retained no output. Under current D-036, the user has selected the OBIS API: preserve every downloaded JSON response unchanged under `data/raw/obis/json/` and place its complete CSV conversion under `data/raw/obis/csv/` as requested. The conversion does not replace the raw JSON source. The current acquisition result is recorded in the [dated source record](../records/2026-10-08-source-obis-area-230-api-csv.md).

## Storage choices by role

| Role | Working format | OCEAVERA convention |
| --- | --- | --- |
| Original occurrence source | OBIS API response JSON (`.json`) | Preserve every complete paginated response unchanged under `data/raw/obis/json/`. Use the Area 230 API query and cursor pages; request all returned fields, include absence and dropped records, and record page hashes, counts, response-body bytes and the final API-reported total. |
| Area 230 tabular copy | CSV (`.csv`), stored under `data/raw/obis/csv/` by explicit user decision D-036 | Convert only a manifest-verified complete JSON run. Include the union of all top-level fields, all 68 names on the OBIS Data Access page and every record without filtering or deduplication; encode nested values as compact JSON strings. Retain the exact JSON pages as the lossless source because CSV cannot represent JSON types without a conversion convention. |
| Environmental layer responses | Publisher-delivered format; NetCDF (`.nc`) for the current Bio-ORACLE ERDDAP collector | Retain each bounded publisher response byte-for-byte under `data/raw/bio_oracle/<dataset-id>/`; record the exact layer, variable, bounds, URL and checksum in its local manifest and dated source record. Keep the returned grid in NetCDF and do not flatten the full raster. |
| Bio-ORACLE source-validation copy | NetCDF (`.nc`) with unchanged per-layer JSON receipts | The first Bio-ORACLE handoff copies one complete, selected catalogue run to `data/interim/bio_oracle/source_validation/<dataset-id>/`. Verify the D-048 rectangle, requested time window, complete run counts, receipt scope, NetCDF signature, byte count and SHA-256. Keep copied receipts and the catalogue run manifest with a stable aggregate `manifest.json`; do not alter or remove the raw source. This is structural validation, not scientific processing. |
| Derived spatial tables | GeoParquet, normally using `.parquet` | Use for spatial occurrences, background samples, integrated records and spatial prediction tables when the selected tools support the format. Preserve geometry and its CRS metadata. |
| Non-spatial modelling tables | Apache Parquet (`.parquet`) | Use for tabular feature matrices or other derived tables when spatial geometry is no longer required and the format is compatible with the agreed tools. Retain stable sample/grid identifiers and lineage. |
| Dataset manifests, model metadata and compact machine-readable metrics | JSON (`.json`) | Keep metadata and summaries in tracked records outside ignored payload directories. JSON is not the storage format for large tables or rasters. |
| Trained model artefacts | Selected only after model and environment decisions | Record the actual artefact format, relevant serialization package/version, environment, dataset and fingerprint in model metadata. A scikit-learn artefact may use Joblib (`.joblib`); an XGBoost artefact may use its native JSON (`.json`) or UBJSON (`.ubj`) format if XGBoost is selected. Neither framework is selected by this guidance. |

GeoParquet adds spatial metadata and geometry columns to Apache Parquet; record the format/specification version and the coordinate reference system where known. The maintained [GeoParquet specification](https://geoparquet.org/releases/v1.1.0/) recommends the `.parquet` extension. Apache describes Parquet as a column-oriented data format ([Apache Parquet documentation](https://parquet.apache.org/)). NetCDF represents scientific data as related variables, dimensions and attributes, including multidimensional arrays ([Unidata NetCDF data model](https://docs.unidata.ucar.edu/netcdf-c/current/netcdf_data_model.html)). These references explain the formats; they do not verify any OCEAVERA resource's actual encoding or compatibility.

## Data lifecycle

Keep the repository's existing `data/raw/`, `data/interim/` and `data/processed/` layout. These locations map in purpose to the proposed Bronze (raw), Silver (cleaned/integrated) and Gold (analysis-ready) stages; retain the existing paths rather than adding a second directory hierarchy.

| Location | Content | Handling |
| --- | --- | --- |
| `data/raw/` | Original source downloads | Preserve unchanged and associate each resource with a source manifest. |
| `data/interim/` | Reproducible cleaning, extraction and integration products | Record inputs, transformations, versions, counts, exclusions and generating artefacts. Use GeoParquet for spatial tables and retain raster arrays in their source format. |
| `data/processed/` | Reviewed analysis-ready tables | Use GeoParquet when spatial geometry is part of the table; use Parquet for non-spatial ML tables where compatible. Document row meaning, target, schema, exclusions and dataset version. |
| `docs/records/` | Manifests, dictionaries and processing evidence | Track provenance and definitions here, outside ignored data directories. Keep credentials and sensitive payloads out. |
| `outputs/` | Reviewed figures, maps and evaluation outputs | Include deliberately after checking provenance, rights, size and ecological sensitivity. Identify the generating dataset and work. |

### Timestamp and phase-folder convention

Use timestamps only to distinguish retained raw acquisition snapshots. Repeated
downloads may add raw files and consume more local storage; the collector does
not silently delete prior source responses. The current path decision keeps
that raw-history trade-off while preventing timestamped copies from
accumulating at derived stages. Any future retention cleanup must preserve
the provenance record and be separately authorised.

At the first OBIS raw-to-interim CSV handoff, provide the selected raw path to
[`stage_obis_csv.py`](../../src/data_preparation/stage_obis_csv.py). This is the
only OBIS stage that accepts a run-specific input path. It validates and copies
the CSV unchanged to a stable phase folder. The manifest is colocated with the
output and has no timestamp in its name; it may refer to the timestamped raw
source path for lineage.

The Bio-ORACLE collector, [`bio_oracle_layers.py`](../../src/data_collection/bio_oracle_layers.py),
is a fixed, no-option script. Running it inventories the live Bio-ORACLE v3
catalogue, then downloads all matching grids and their data variables for the
EEZ-extrema rectangle under [D-048](../records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md)
and the requested 2000–2100 time window. It preserves each publisher NetCDF
response and records its query/checksum in a local manifest; an incremental run
manifest tracks completed and failed layers. Raw files and local manifests are
ignored by Git. Bio-ORACLE supplies decade-level values rather than annual
records; only publisher coordinates within the requested time bounds are
downloaded. The rectangle is not polygon-clipped and may include land or waters
outside the EEZ. The script shows stage and transfer progress, retries transient
response interruptions, and reports a final layer/variable summary with a run
manifest path. Previous catalogue and download outcomes are recorded in the
dated intake record. The earlier complete and partial snapshots were deleted
at the user's request; the latest Python-file run has all 356 of 356 layers
verified. The user reports running the source-validation handoff, which leaves
raw data unchanged. Its local aggregate manifest records 356 layers, 2,392
variables and 4,017,532,960 payload bytes; the current interim inventory
contains 714 files totaling 4,021,176,513 bytes. The manifest and inventory
were inspected, but payload hashes were not independently recalculated during
the later UX update. No scientific environmental processing, integration or
processed data exists.

| Stage or source | Stable path pattern | Status and use |
| --- | --- | --- |
| OBIS source validation | `data/interim/obis/source_validation/occurrences.csv` and adjacent `manifest.json` | Implemented; byte-preserving structural validation only. |
| Later OBIS phases | `data/interim/obis/<phase>/<artifact>` | Adopted layout; each implemented phase reads the preceding fixed path and writes its own fixed path. |
| Bio-ORACLE source validation | `data/interim/bio_oracle/source_validation/<dataset-id>/` with `catalog_run_manifest.json` and adjacent `manifest.json` | Implemented in [`stage_bio_oracle_layers.py`](../../src/data_preparation/stage_bio_oracle_layers.py); the user reports a completed run, and its local manifest/inventory records are summarized above. The script copies a selected complete D-047/D-048 run unchanged after structural and integrity checks; no scientific processing is applied. |
| Later Bio-ORACLE phases | `data/interim/bio_oracle/<phase>/<artifact>` | Path pattern adopted; scientific processing and integration are not implemented. |
| Cross-source integration | A fixed, timestamp-free integration-stage path beneath `data/interim/` | Planned; not implemented. |
| Analysis-ready table | `data/processed/modeling_dataset.parquet` | Stable planned destination; record whether the actual file is GeoParquet or non-spatial Parquet. Processing is not implemented. |

`<phase>` and `<artifact>` stand for names chosen when a specific transformation
is implemented; they are not timestamp fields. Each transformation phase gets
its own folder under the relevant source directory. Later scripts use fixed
upstream and output paths rather than prompting for a run-specific location.
Regeneration replaces the same phase output only after successful validation.
The phase folders keep successive transformations distinct without creating a
new derived run folder on every execution.

Data payloads are excluded from Git by default. The earlier feasibility response bodies and historical Area 230 JSON/CSV payloads were removed at the user's request; their query summaries and available fingerprints remain as historical evidence. The 8 October AWS export attempt retained no subset. The current API collection is stored locally under the two D-036 raw paths, with tracked checksums and provenance in `docs/records/`; payloads remain ignored by Git. An ignore rule does not remove an already tracked file. Keep trained model binaries out of Git unless the group has reviewed the artefact's size, provenance, rights and storage purpose.

## Spatial integration and table construction

Do not convert an entire multidimensional environmental raster into a large table merely to fit the modelling workflow. Retain the complete source array in its delivered format; extract the selected environmental values at the justified modelling locations and store those extracted values as columns in the derived spatial dataset. If later work requires a raster transformation, record the reason, source fingerprint, transformation, output format and validation.

For spatial tables, retain an explicit geometry and CRS where supported. If a later modelling table omits geometry, retain the stable observation/grid-cell identifier and enough provenance to recover its spatial meaning. Record units, resolution, coordinate system, marine mask, no-data conventions, depth stratum and temporal statistic/period for each environmental layer. Specify the extraction/join method, grid alignment, coastal-cell handling, unmatched points and any temporal approximation. Historical climatologies are not contemporaneous measurements.

Before recommending a species, region or layer, measure coverage and record quality from retrieved data. Check taxonomic identity, coordinate validity and order, observation dates, duplicate or repeated records, depth context and sampling concentration. For every material filter or join, record input versions, counts before and after, exclusions and reasons, and the generating artefact. Distinguish legitimate repeated observations from duplicates. Update the [data dictionary](../templates/data-dictionary.md) whenever field meaning or transformations change.

## Acquisition provenance

Copy the [source manifest](../templates/data-source-record.md) for each actual resource. Record publisher, stable URL/DOI/accession, exact release/layer, retrieval date, query and filters, actual file format, source citation, licence/terms, coverage, and checksum algorithm/value where practical. Record file paths relative to the repository. Do not infer a format from a publisher's name or a discussion example.

Use descriptive resource IDs and version identifiers consistently in manifests, dictionaries, notebooks and outputs. Retain the original resource identity when renaming a local file. A resource can change without changing its URL; record both retrieval details and a content fingerprint.

When an integrated dataset is created, complete the [machine-readable manifest](../templates/dataset-manifest.json), including its actual data format and specification version when applicable. Link its source records, dictionary, processing artefact, configuration, counts and fingerprint. This complements the narrative source records; blank template fields establish no acquisition evidence.

OBIS occurrences and Bio-ORACLE layers are proposed core inputs; OBIStherm is only a possible supporting resource. The D-046 test response's array shape, coordinate centers and fill/non-fill counts remain historical measurements in the [source record](../records/2026-10-09-source-bio-oracle-oceantemperature.md); that payload and its local manifest were deleted at the user's request. Under [D-047](../records/2026-10-09-decision-bio-oracle-catalog-intake.md) and [D-048](../records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md), the first complete regional acquisition and a later partial manual snapshot were deleted at the user's request. The latest Python-file run completed all 356 grids and 2,392 variables, totaling 4,017,532,960 bytes; every payload matched its recorded size and SHA-256, and all 356 per-layer receipts passed the request-scope audit. The tracked [regional intake record](../records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) preserves all three outcomes and current run details. The latest payloads and manifests remain in the ignored raw folder. The current ERDDAP axes expose baseline coordinates at 2000/2010 and SSP coordinates at 2020–2090, with no 2100 coordinate in these layers. The deleted test response's fill-cell marine meaning, exact time aggregation and compatibility remain unverified.

The current Bio-ORACLE v3 layers are decade summaries rather than annual values. The publisher defines present-day conditions as 2000–2020 and offers the 2000–2010 and 2010–2020 decades, but the downloaded per-layer metadata does not specify the exact averaging window attached to its 2000/2010 labels. Since titles vary between 2000–2018, 2000–2019 and 2000–2020, coverage through 2020 remains unresolved for individual baseline layers. SSP labels 2020–2090 reach the documented 2100 horizon; 2090 is the last decade label, with no separate 2100 timestamp. See the [regional source record](../records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) and the publisher's [documentation](https://www.bio-oracle.org/documentation.php).

## Targets, models and interpretation

Keep observed biological presences separate from constructed background/pseudo-absence labels. Missing occurrences are not confirmed absences. Preserve sample origin, sampling domain and split information so the target and evaluation can be audited.

Document learned transformations and fit them within training partitions. Deterministic extraction of independently published environmental covariates can precede splitting; target-guided choices and learned transformations must respect the evaluation boundary.

No model family or model-file format is fixed. Select serialization only after the model, reproducible environment and intended use are agreed. Save an accepted preprocessing-plus-estimator pipeline as one artefact where the chosen framework supports it; record the actual format and environment in [model metadata](../templates/model-metadata.json). Joblib persistence uses Python pickle and can execute code when loading; only load artefacts from a trusted, verified source ([Joblib persistence and security guidance](https://joblib.readthedocs.io/en/latest/user_guide/persistence.html)). If XGBoost is selected, its [model I/O guide](https://xgboost.readthedocs.io/en/stable/tutorials/saving_model.html) documents JSON and UBJSON formats and distinguishes model files from memory snapshots. Do not load untrusted model files as a shortcut to evaluation or integration.

## Later BLUEVERSE integration

OCEAVERA's analytical data remain in the repository's source and derived-data lifecycle. A later integration should transfer only reviewed, application-relevant outputs with an explicit schema, model/data version, score interpretation, domain, uncertainty and sharing conditions. The architecture discussed for the integration uses PostgreSQL with [PostGIS](https://postgis.net/documentation/manual/) for operational spatial records, JSON for ordinary API messages and [GeoJSON](https://www.rfc-editor.org/rfc/rfc7946) for modest spatial API payloads; large analytical files belong in file/object storage with database references, not as bulk payloads in the operational database. These are downstream integration conventions, not an OCEAVERA database implementation.

Zarr is not part of the current OCEAVERA storage convention. Revisit it only if later data scale or multidimensional processing needs provide a concrete reason.

**Cloud Optimized GeoTIFF (`.tif`, COG) and ONNX (`.onnx`) are optional, unfinalised integration suggestions only.** They are not required OCEAVERA outputs, not additions to the current OCEAVERA model/data format selection and not implementation commitments. A COG could be considered by the BLUEVERSE integration owners if an actual large raster-map delivery need is established; ONNX could be considered if an agreed integration requires an inference representation compatible with a non-Python runtime. Neither should be generated or added as a dependency before that need and contract are selected. See the [GDAL COG driver](https://gdal.org/en/stable/drivers/raster/cog.html) and [ONNX introduction](https://onnx.ai/onnx/intro/) for format references.

## Responsible sharing and handover

Review publisher terms and attribution requirements before reuse or redistribution. Review fine-resolution species locations for ecological sensitivity before publishing maps or coordinates. Keep credentials, tokens and unrelated personal data out of project files. Record relevant permissions or anonymisation measures without exposing sensitive details.

Follow the [complete member plan](../project/member-responsibilities.md): Sanuda owns biological preparation/target inputs, Ushan environmental preparation/spatial integration and Adithya integrated cleaning/preprocessing. Wanshaja reviews source preparation and leads evaluation with group participation. Each producing member supplies provenance, actual file formats, field definitions, row counts, exclusions, versions and generating references; combine biological and environmental definitions in the integrated dictionary/manifest. All four decide species/domain, sampling and final features from that evidence. The allocation does not establish acquisition or authorise payload redistribution.
