# OBIS–Bio-ORACLE spatial integration prepublication audit

- **Date:** 12 October 2026
- **Decision:** [D-050](2026-10-12-decision-obis-bio-oracle-integration.md)
- **Status:** Full in-memory integration and source-integrity checks passed. No GeoParquet dataset was written because the required writer packages are unavailable and package/environment operations require explicit authorisation.
- **Machine-readable evidence:** [Prepublication audit JSON](2026-10-12-obis-bio-oracle-prepublication-audit.json)

## Scope and inputs

The audit used the current cleaned OBIS CSV (23,371 rows × 112 columns) and only six selected Bio-ORACLE products. Each selected interim NetCDF file was checked against its raw source and both Bio-ORACLE manifests. The integration reads the current cleaned stage and selected raster cells in memory; it does not modify either source family or write an integrated dataset.

| Output prefix | Bio-ORACLE product | Source variable | Units as recorded | Context |
| --- | --- | --- | --- | --- |
| `bio_thetao_mean_t2000`, `bio_thetao_mean_t2010` | `thetao_baseline_2000_2019_depthsurf` | `thetao_mean` | `degree_C` | Surface; stored decadal coordinates 2000 and 2010 |
| `bio_so_mean_t2000`, `bio_so_mean_t2010` | `so_baseline_2000_2019_depthsurf` | `so_mean` | `PSU` | Surface; stored decadal coordinates 2000 and 2010 |
| `bio_chl_mean_t2000`, `bio_chl_mean_t2010` | `chl_baseline_2000_2018_depthsurf` | `chl_mean` | `mg m-3` | Surface; stored decadal coordinates 2000 and 2010 |
| `bio_o2_mean_t2000`, `bio_o2_mean_t2010` | `o2_baseline_2000_2018_depthsurf` | `o2_mean` | `MMol' 'M-3` | Surface; stored decadal coordinates 2000 and 2010 |
| `bio_no3_mean_t2000`, `bio_no3_mean_t2010` | `no3_baseline_2000_2018_depthsurf` | `no3_mean` | `MMol' 'M-3` | Surface; stored decadal coordinates 2000 and 2010 |
| `bio_bathymetry_mean` | `terrain_characteristics` | `bathymetry_mean` | `m` | Static terrain; original values and sign convention retained |

The dynamic layer labels are stored decadal coordinates, not exact annual observations. Terrain's source time coordinate is not treated as an observation year. No future SSP product or other product in the 356-file archive was loaded for extraction. All selected products use the same 178 × 165 increasing latitude/longitude grid at approximately 0.05° spacing and WGS84/EPSG:4326.

## Matching and extraction method

For each valid observation coordinate, the code finds the nearest grid-cell centre on the actual coordinate arrays. Ties resolve to the lower coordinate index. The outer coverage boundary is one-half a grid step beyond the edge cell centres; points outside it remain unmatched and are not clamped. Raster indices are zero-based. The original OBIS coordinate strings are preserved. The planned point geometry uses the original longitude as X and latitude as Y; matched cell-centre coordinates are separate fields. Centre distance is calculated with a spherical haversine formula and IUGG mean Earth radius 6,371,008.8 m.

Declared `_FillValue` and `missing_value` entries become null, declared scale and offset are applied if present, and genuine zero remains valid. No spatial or temporal imputation, interpolation, temporal averaging or bathymetry sign conversion occurs. `raster_match_status` distinguishes matched, outside extent, invalid coordinates, fully masked cells, partly missing selected values and extraction errors. `environmental_coverage_status` describes only selected-layer empirical value availability. Neither status assigns authoritative land/water meaning.

## Audit results

| Check | Result |
| --- | --- |
| Input and row lineage | All 23,371 cleaned OBIS rows retained; one-based source row numbers are contiguous and unique; original coordinate strings unchanged |
| Planned output shape | 23,371 rows; 133 columns including geometry |
| Spatial status | 16,840 `matched`; 6,531 `masked_raster_cell`; 0 outside extent; 0 invalid coordinates; 0 partially missing; 0 extraction errors |
| Occupied grid cells | 965 |
| Distance to cell centre | n=23,371; min 0.169 m; median 2,436.42 m; p90 3,901.75 m; p95 3,916.89 m; max 3,928.80 m |
| Environmental nulls | 6,531 nulls in each of the 11 value columns, all on cells with no values in any selected field; no `-9999.9` retained as a measurement |
| Direct NetCDF check | 24 scalar byte-offset reads across six products matched the array-index extraction path; no independent external NetCDF reader was available |
| Repeated coordinate pairs | 7,321 unique valid pairs; 1,088 pairs repeat; 17,138 records occur at repeated pairs; maximum 933 records at one coordinate. No rows were deduplicated. |
| Source preservation | OBIS cleaned/raw and Bio-ORACLE selected source/interim fingerprints were rechecked after the audit and remained unchanged |
| Target/background safeguards | No target columns, pseudo-absence/background rows or species-specific filters created |

The complete data-quality distributions and source fingerprints are retained in the machine-readable audit JSON. Coordinate uncertainty is present for 10,964 rows and absent for 12,407. `ON_LAND` is present on 8,000 rows; among those, 2,339 map to cells with empirical non-fill values and 5,661 to cells whose selected values are all fill. 7,912 `ON_LAND` rows also have `marine=true`; these cross-field counts are review signals, not coordinate verification. All 8,000 flagged rows have numeric `shoredistance`; its units are not asserted here. The empirical non-fill footprint is not an authoritative ocean mask.

Taxonomic fields remain as supplied. `scientificName` and `AphiaID` are populated for all 23,371 rows; `species` and `speciesid` are populated for 17,419; `taxonRank` is populated for 10,338. These values do not independently verify species-level identification. Occurrence status, absence flags, marine classifications and dataset concentration are preserved and summarized in the JSON record. Records sharing coordinates or raster cells are not assumed to be independent samples.

## Output and remaining gate

The intended primary output follows D-049 at `data/interim/integrated/integrated_dataset.parquet`. The output design preserves all 112 source fields, assigns `obis_id` to the source `id`, prefixes OBIS bathymetry/SST/SSS fields, and adds row lineage, grid match fields, explicit statuses, eleven environmental value fields and a WKB Point geometry in EPSG:4326. The actual GeoParquet file has **not** been created: metadata validation, read-back geometry reconstruction, final file fingerprint/size and publication are therefore not claimed.

The inspected Python 3.12.14 runtime has none of GeoPandas, PyArrow, Fastparquet, DuckDB, Polars, Shapely or Pyogrio. The project Python baseline is 3.14. The minimal pinned writer requirements are `geopandas==1.2.0` and `pyarrow==26.0.0`; no package or environment operation has been performed. The user-supplied task instructions and D-043 require explicit authorisation before setup. After authorisation, rerun the pilot, then the default integration command, validate the produced GeoParquet metadata and read-back, verify input fingerprints and finalize the branch work notebook under the notebook convention.

The integration is not an analysis-ready or supervised-learning dataset. Focal species eligibility, marine modelling boundary, target meaning, background/sampling design, validation, EDA and any feature/model work remain future decisions.

## Publication follow-up — 12 October 2026

This document and its JSON companion are the prepublication audit snapshot; their original status statements describe the audit before a GeoParquet writer was available in the inspected runtime. After the user directed use of the existing WSL `OCEAVERA` environment, the normal publication command completed without changing the environment or installing packages. The 23,371-row, 133-column GeoParquet was written to the D-049 destination and its metadata, schema, source attributes, row lineage, geometries, spatial assignments, null pattern and SHA-256 were verified after reopening the saved file.

The [integration summary](2026-10-12-integration-summary.json) and [manifest](2026-10-12-integration-manifest.json) record the published artifact and fingerprints. The [branch work notebook](../../notebooks/branch_work/05_pipeline_data_integration_and_data_cleaning.ipynb) independently compares all 112 cleaned OBIS attributes, verifies the raw/interim source fingerprints and checks 55 scalar values across the six raw Bio-ORACLE products. These additions supersede the prepublication status only; the audit findings, limitations and original evidence remain intact. The source datasets were preserved.
