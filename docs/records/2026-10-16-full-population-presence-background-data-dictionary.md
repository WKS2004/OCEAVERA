# Full-population long-format presence/background GeoParquet data dictionary

- **Current dataset:** data/interim/pseudo_absence/presence_background_candidates.parquet
- **Decision:** [D-056](2026-10-16-decision-paired-presence-background.md)
- **Input:** data/interim/integrated/gridded/grid_observations.parquet
- **Shape:** 4,706 rows × 527 columns
- **Spatial metadata:** GeoParquet 1.1.0, WKB Point, EPSG:4326, ZSTD
- **Schema:** 519 original source fields, followed by eight construction fields

## Row meaning

Rows 1–2,353 are the original Policy B observations with label 1, retained once in source order. Rows 2,354–4,706 are separate sampled marine background examples with label 0. A background is not a confirmed absence. The 1:1 ratio is a construction choice, not a prevalence estimate.

The original 519 fields remain first and in their original order. Positive-row values and geometries match the source exactly. Background rows contain source-derived environmental values at sampled raster centres, conditioning taxonomic fields and the period of the linked positive. Observation identifiers, original source-row IDs, occurrence event dates and absence values remain null on backgrounds. The new paired_presence_source_row field links a background example to its conditioning source observation; it does not fabricate an occurrence ID.

Two original fields need nullable types so synthetic rows can remain null: integration_source_row is nullable Int64 and marine_uncertainty_verified is nullable Boolean. Their positive-row values are unchanged. Other source fields that have no meaning for sampled backgrounds are null. Background taxonomic identifiers are conditioning information only and do not represent a taxon occurrence at the sampled coordinate.

## Eight appended fields

| Field | Type | Meaning |
| --- | --- | --- |
| presence_background_label | int8 | 1 for an observed Policy B occurrence; 0 for a newly sampled background example, not a confirmed absence. |
| sample_type | string | observed_presence or sampled_background. |
| target_taxon_key | string | AphiaID:<integer> where the source has a valid positive integer identifier; otherwise unresolved_source_row:<source row ID>. The key does not verify species identity. |
| paired_presence_source_row | int64 | integration_source_row of the conditioning positive; populated for both classes. |
| eligible_species_level_ml | bool | Preliminary technical eligibility copied from the linked source row. It does not verify taxonomy or sample adequacy. |
| ml_eligibility_reason | string | preliminary_species_core_eligible or a semicolon-separated list of failed conditions. Reason counts may overlap. |
| background_sampling_method | nullable string | Null for positives; uniform_unique_GSHHG_water_core_complete for sampled backgrounds. |
| sample_id | string | Unique row key: presence:<source row ID> or background:<source row ID>. |

## Original fields populated on background rows

Taxonomic conditioning fields copied from the source are AphiaID, aphiaID, taxonID, scientificName, scientificNameID, species, speciesid and taxonRank when those fields exist. The source analysis_period and environment_period are copied to choose the correct environmental slice.

The script populates raster_row, raster_column, raster_cell_id, grid_cell_id and cell-centre coordinates from the actual raster axes. raster_cell_distance_km is zero because the geometry is the centre itself. The geometry is a Point at the selected Bio-ORACLE cell centre, strictly inside the validated GSHHG water polygon. Quality annotations identify this as a sampled GSHHG water centre, not an OBIS observation with positional uncertainty.

All 382 Bio-ORACLE feature columns are populated from the corresponding source arrays at the sampled cell. No environmental values are fabricated or imputed. All six core predictors are finite for every background; legitimate missing and quarantined values remain null. Positive rows retain their original environmental values, including nulls.

## Eligibility and measured population

A positive row is flagged eligible only when it has a valid positive integer AphiaID, explicit species rank, complete values for the six core predictors and a source raster-cell centre in GSHHG water. Policy B source validation already requires absence=false and marine=true. A failed reason list may contain more than one condition.

| Measure among 2,353 positives | Count |
| --- | ---: |
| Valid AphiaID rows / distinct valid AphiaIDs | 2,353 / 614 |
| Explicit species-rank rows / distinct species-rank AphiaIDs | 2,009 / 501 |
| Complete six-core environmental rows | 2,082 |
| Source grid-cell centres in GSHHG water | 2,029 |
| Preliminary eligible / ineligible rows | 1,729 / 624 |

Taxon-rank spelling/case is normalized for the species-rank screen; the original taxonRank values remain unchanged. Unknown or non-species records remain in both their positive row and linked background row, but their eligibility flag is false unless the complete screen passes.

## Sampling and periods

Seed: 20261016. Every original occupied Policy B grid cell is excluded for every taxon and period. Sampled background cells are unique globally. Candidate pools require a GSHHG water centre and all six core values for the applicable source period.

| Observation period | Environmental slice | Positives | Backgrounds | Candidate pool at draw |
| --- | --- | ---: | ---: | ---: |
| 2000–2009 | baseline_2000 | 376 | 376 | 24,175 |
| 2010–2019 | baseline_2010 | 596 | 596 | 23,799 |
| 2020–2026 | ssp245_2020 | 1,381 | 1,381 | 23,203 |

The 2020–2026 rows use the SSP245 2020 projection-based environmental slice. These periods are source-slice approximations, not annual measurements.

## Environmental coverage and source verification

| Class | Environmental positions | Non-null values | Null values | Rows complete for all 382 | Rows complete for all six core values |
| --- | ---: | ---: | ---: | ---: | ---: |
| Observed positive | 898,846 | 714,199 | 184,647 | 0 | 2,082 |
| Sampled background | 898,846 | 805,680 | 93,166 | 0 | 2,353 |

Script 10 verified 106 source products and 1,012 catalogue mappings. It checked all 898,846 background environmental positions after GeoParquet read-back against their mapped NetCDF source slices: zero numerical mismatches, zero null/fill discrepancies and maximum absolute difference 0. The full [construction report](2026-10-16-full-population-presence-background-construction.md) records per-period counts, nulls, fingerprints and archive checks.

## Interpretation and limits

There are 300 repeated valid species/AphiaID × cell × period combinations involving 920 positive rows (620 excess rows). Across all taxa, 2,099 source rows share a cell and period with another source row. These are not independent model samples.

Original positive median bathymetry is −15.9 m among rows with a value; sampled background median is −3,771.6 m. Background median longitude/latitude is 81.925°E / 6.375°N compared with 80.290°E / 7.112°N for positive locations. Broad uniform marine sampling therefore has a material geographic and depth difference from the occurrence process. It can create apparent class separation and must be reviewed before model evaluation.

Background is not confirmed species absence; uniform sampling does not correct OBIS effort bias or define a final accessible area. The dataset is not a deduplicated or spatially validated training set. A later approved step must prevent shared raster cells from crossing training/test folds, including across taxa and periods. No feature selection, imputation, model training or evaluation was performed.
