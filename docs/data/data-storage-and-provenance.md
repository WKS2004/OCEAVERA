# Data storage and provenance

This document defines the OCEAVERA data and model-artefact storage conventions. The conventions guide future work; they do not establish that data have been acquired, a model has been trained, or an integration has been implemented. No source resource, modelling runtime or dependency stack has been selected.

## Storage choices by role

| Role | Working format | OCEAVERA convention |
| --- | --- | --- |
| Original occurrence download | Publisher-delivered format; CSV (`.csv`) where supplied | Preserve the exact source payload unchanged. The anticipated OBIS download format must be verified for the actual query or snapshot. |
| Original environmental arrays | Publisher-delivered format; NetCDF (`.nc`) where supplied | Retain the complete source array in its delivered format. NetCDF is the anticipated form for Bio-ORACLE layers in the proposed workflow, subject to verification of the selected resource. |
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

Data payloads are excluded from Git by default. The three data directories retain only structural markers until acquisition is authorised. An ignore rule does not remove an already tracked file. Keep trained model binaries out of Git unless the group has reviewed the artefact's size, provenance, rights and storage purpose.

## Spatial integration and table construction

Do not convert an entire multidimensional environmental raster into a large table merely to fit the modelling workflow. Retain the complete source array in its delivered format; extract the selected environmental values at the justified modelling locations and store those extracted values as columns in the derived spatial dataset. If later work requires a raster transformation, record the reason, source fingerprint, transformation, output format and validation.

For spatial tables, retain an explicit geometry and CRS where supported. If a later modelling table omits geometry, retain the stable observation/grid-cell identifier and enough provenance to recover its spatial meaning. Record units, resolution, coordinate system, marine mask, no-data conventions, depth stratum and temporal statistic/period for each environmental layer. Specify the extraction/join method, grid alignment, coastal-cell handling, unmatched points and any temporal approximation. Historical climatologies are not contemporaneous measurements.

Before recommending a species, region or layer, measure coverage and record quality from retrieved data. Check taxonomic identity, coordinate validity and order, observation dates, duplicate or repeated records, depth context and sampling concentration. For every material filter or join, record input versions, counts before and after, exclusions and reasons, and the generating artefact. Distinguish legitimate repeated observations from duplicates. Update the [data dictionary](../templates/data-dictionary.md) whenever field meaning or transformations change.

## Acquisition provenance

Copy the [source manifest](../templates/data-source-record.md) for each actual resource. Record publisher, stable URL/DOI/accession, exact release/layer, retrieval date, query and filters, actual file format, source citation, licence/terms, coverage, and checksum algorithm/value where practical. Record file paths relative to the repository. Do not infer a format from a publisher's name or a discussion example.

Use descriptive resource IDs and version identifiers consistently in manifests, dictionaries, notebooks and outputs. Retain the original resource identity when renaming a local file. A resource can change without changing its URL; record both retrieval details and a content fingerprint.

When an integrated dataset is created, complete the [machine-readable manifest](../templates/dataset-manifest.json), including its actual data format and specification version when applicable. Link its source records, dictionary, processing artefact, configuration, counts and fingerprint. This complements the narrative source records; blank template fields establish no acquisition evidence.

OBIS occurrences and Bio-ORACLE layers are proposed core inputs; OBIStherm is only a possible supporting resource. Use current authoritative publisher documentation when actual acquisition begins. Verify the exact resource packaging, access and terms at that time.

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
